import os
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from datetime import timedelta
import random
import json

from .models import SensorReading, TrashDetectionEvent, FloodAlert, ContactMessage
from .forms import ContactForm, LoginForm, RegisterForm


# ── STATIONS ──────────────────────────────────────────────────────
STATIONS = [
    {'key': 'ellis_bridge',  'label': 'Ellis Bridge',  'lat': 23.0338, 'lng': 72.5677},
    {'key': 'gandhi_bridge', 'label': 'Gandhi Bridge', 'lat': 23.0225, 'lng': 72.5714},
    {'key': 'nehru_bridge',  'label': 'Nehru Bridge',  'lat': 23.0150, 'lng': 72.5750},
    {'key': 'sardar_bridge', 'label': 'Sardar Bridge', 'lat': 23.0450, 'lng': 72.5640},
    {'key': 'vasna_barrage', 'label': 'Vasna Barrage', 'lat': 22.9950, 'lng': 72.5800},
]


# ── HOME ──────────────────────────────────────────────────────────
def home(request):
    stats = {
        'total_detections': TrashDetectionEvent.objects.count() or 148,
        'active_stations':  5,
        'map_accuracy':     84.9,
        'alerts_resolved':  TrashDetectionEvent.objects.filter(resolved=True).count() or 92,
    }
    latest_alerts = TrashDetectionEvent.objects.filter(alert_level='high')[:3]
    return render(request, 'core/home.html', {
        'stats':         stats,
        'latest_alerts': latest_alerts,
        'stations_list': STATIONS,
    })


# ── REGISTER ──────────────────────────────────────────────────────
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = User.objects.create_user(
            username   = form.cleaned_data['username'],
            email      = form.cleaned_data['email'],
            password   = form.cleaned_data['password1'],
            first_name = form.cleaned_data['first_name'],
            last_name  = form.cleaned_data['last_name'],
        )
        # Auto-login immediately after registration
        user = authenticate(
            request,
            username = form.cleaned_data['username'],
            password = form.cleaned_data['password1'],
        )
        if user:
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name}! Your account has been created.')
            return redirect('dashboard')

    return render(request, 'registration/register.html', {'form': form})


# ── LOGIN ─────────────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username = form.cleaned_data['username'],
            password = form.cleaned_data['password'],
        )
        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'dashboard'))
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'registration/login.html', {'form': form})


# ── LOGOUT ────────────────────────────────────────────────────────
def logout_view(request):
    logout(request)
    return redirect('home')


# ── DASHBOARD ─────────────────────────────────────────────────────
@login_required
def dashboard(request):
    now      = timezone.now()
    last_24h = now - timedelta(hours=24)

    total_detections = TrashDetectionEvent.objects.count()
    detections_24h   = TrashDetectionEvent.objects.filter(timestamp__gte=last_24h).count()
    high_alerts      = TrashDetectionEvent.objects.filter(alert_level='high', resolved=False).count()
    cluster_count    = TrashDetectionEvent.objects.filter(trash_class='cluster').count()
    recent_events    = TrashDetectionEvent.objects.select_related('resolved_by')[:8]
    flood_alerts     = FloodAlert.objects.filter(is_active=True)[:3]

    # Latest sensor reading per station from DB
    sensor_data = []
    for s in STATIONS:
        reading = SensorReading.objects.filter(station=s['key']).order_by('-timestamp').first()
        sensor_data.append({'station': s['key'], 'label': s['label'], 'reading': reading})

    # Chart: detections per day last 7 days
    chart_labels, chart_data = [], []
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        chart_labels.append(day.strftime('%d %b'))
        chart_data.append(TrashDetectionEvent.objects.filter(timestamp__date=day.date()).count())

    return render(request, 'core/dashboard.html', {
        'total_detections': total_detections,
        'detections_24h':   detections_24h,
        'high_alerts':      high_alerts,
        'cluster_count':    cluster_count,
        'recent_events':    recent_events,
        'sensor_data':      sensor_data,
        'flood_alerts':     flood_alerts,
        'chart_labels':     chart_labels,
        'chart_data':       chart_data,
        'model_map':        84.9,
        'model_precision':  96.9,
        'model_recall':     74.4,
    })


# ── API: LIVE SENSORS (reads from DB) ─────────────────────────────
def api_live_sensors(request):

    def turb_status(v):
        return 'good' if v <= 300 else ('warning' if v <= 500 else 'danger')

    mongo_data = get_latest_water_data()

    if not mongo_data:
        mongo_data = {
            "turbidity": 0,
            "status": 0,
            "time": "No Data"
        }

    data = []

    for s in STATIONS:
        turbidity = mongo_data["turbidity"]

        data.append({
            'station': s['key'],
            'label': s['label'],
            'lat': s['lat'],
            'lng': s['lng'],

            # Only turbidity real, rest dummy (since not in Mongo)
            'ph': 7.0,
            'ph_status': 'good',

            'dissolved_oxygen': 6.0,
            'do_status': 'good',

            'turbidity': turbidity,
            'turb_status': turb_status(turbidity),

            'temperature': 28,
            'water_level': 2,
            'tds': 300,

            'timestamp': str(mongo_data["time"]),
            'source': 'mongodb',
        })

    return JsonResponse({
        'stations': data
    })

# ── API: PUSH SENSOR DATA FROM HARDWARE ───────────────────────────
@csrf_exempt
def api_push_sensor(request):
    """
    POST endpoint — your Arduino/Raspberry Pi/Python script sends
    sensor readings here and they instantly appear on the dashboard UI.

    Expected JSON body:
    {
        "station": "ellis_bridge",
        "ph": 7.2,
        "dissolved_oxygen": 6.5,
        "turbidity": 18.3,
        "temperature": 28.1,
        "water_level": 2.4,
        "bod": 4.2,
        "conductivity": 350.0,
        "tds": 280
    }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    station = payload.get('station', '').strip()
    valid_stations = [s['key'] for s in STATIONS]
    if station not in valid_stations:
        return JsonResponse({
            'error': f'Invalid station. Valid: {valid_stations}'
        }, status=400)

    reading = SensorReading.objects.create(
        station          = station,
        timestamp        = timezone.now(),
        ph               = payload.get('ph'),
        dissolved_oxygen = payload.get('dissolved_oxygen'),
        turbidity        = payload.get('turbidity'),
        temperature      = payload.get('temperature'),
        water_level      = payload.get('water_level'),
        bod              = payload.get('bod'),
        conductivity     = payload.get('conductivity'),
        tds              = payload.get('tds'),
    )

    return JsonResponse({
        'status':    'saved',
        'id':        reading.id,
        'station':   station,
        'timestamp': reading.timestamp.strftime('%d %b %Y %H:%M:%S'),
    })


# ── API: PUSH DETECTION FROM YOLO ─────────────────────────────────
@csrf_exempt
def api_push_detection(request):
    """
    POST endpoint — your YOLOv8 inference script sends detections here.
    They instantly appear in the dashboard detection table.

    Expected JSON body:
    {
        "station": "gandhi_bridge",
        "trash_class": "cluster",
        "confidence": 0.87,
        "latitude": 23.0225,
        "longitude": 72.5714
    }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    station     = payload.get('station', 'gandhi_bridge')
    trash_class = payload.get('trash_class', 'solo')
    confidence  = float(payload.get('confidence', 0.75))
    lat         = float(payload.get('latitude',  23.0225))
    lng         = float(payload.get('longitude', 72.5714))

    event = TrashDetectionEvent.objects.create(
        station     = station,
        trash_class = trash_class,
        confidence  = confidence,
        latitude    = lat,
        longitude   = lng,
        timestamp   = timezone.now(),
    )

    return JsonResponse({
        'status':      'saved',
        'id':          event.id,
        'alert_level': event.alert_level,
        'station':     event.get_station_display(),
        'trash_class': event.trash_class,
        'timestamp':   event.timestamp.strftime('%d %b %Y %H:%M:%S'),
    })


# ── API: LIVE DETECTIONS ──────────────────────────────────────────
def api_live_detections(request):
    events = TrashDetectionEvent.objects.filter(resolved=False)[:20]
    data = [{
        'id':          e.id,
        'station':     e.get_station_display(),
        'trash_class': e.trash_class,
        'confidence':  round(e.confidence * 100, 1),
        'alert_level': e.alert_level,
        'lat':         e.latitude,
        'lng':         e.longitude,
        'timestamp':   e.timestamp.strftime('%d %b %H:%M'),
    } for e in events]
    return JsonResponse({'detections': data})


# ── RESOLVE DETECTION ─────────────────────────────────────────────
@login_required
def resolve_detection(request, pk):
    try:
        event             = TrashDetectionEvent.objects.get(pk=pk)
        event.resolved    = True
        event.resolved_by = request.user
        event.resolved_at = timezone.now()
        event.save()
        return JsonResponse({'status': 'ok'})
    except TrashDetectionEvent.DoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)


# ── CONTACT ───────────────────────────────────────────────────────
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you! Your message has been received.')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'core/contact.html', {'form': form})


# ── STATIC PAGES ──────────────────────────────────────────────────
def technology(request):
    return render(request, 'core/technology.html')


def about(request):
    team = [
        {'name': 'Roshni Panchal',  'role': 'AI/ML',           'avatar': 'RP'},
        {'name': 'Dhrudeepsinh Jadeja', 'role': 'IoT, Backend',             'avatar': 'DJ'},
        {'name': 'Vishvjitsinh Chauhan','role': 'GIS & Dashboard', 'avatar': 'VC'},
    ]
    return render(request, 'core/about.html', {'team': team})



# fetch turbinity data

MONGO_URI = os.getenv("MONGO_URI")

#mongodb
from .mongo_utils import get_latest_water_data


