# RiverSense — Smart Management of Sabarmati Riverfront
**B.Tech IT · Semester 8 · Ahmedabad, Gujarat · 2025–2026**

IoT · AI/ML · GIS · Computer Vision — YOLOv8 Floating Trash Detection

---

## Quick Setup

### 1. Navigate into your existing Django project folder or create a new one
Place all these files inside your Django project root.

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add 'core' to INSTALLED_APPS in settings.py
Already done in the provided settings.py.

### 4. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a superuser (for login & admin panel)
```bash
python manage.py createsuperuser
```

### 6. Seed sample data (optional but recommended)
```bash
python manage.py seed_data
```

### 7. Run the development server
```bash
python manage.py runserver
```

### 8. Open in browser
- **Home:**        http://127.0.0.1:8000/
- **Login:**       http://127.0.0.1:8000/login/
- **Dashboard:**   http://127.0.0.1:8000/dashboard/  *(login required)*
- **Technology:**  http://127.0.0.1:8000/technology/
- **About:**       http://127.0.0.1:8000/about/
- **Contact:**     http://127.0.0.1:8000/contact/
- **Admin:**       http://127.0.0.1:8000/admin/
- **Live API:**    http://127.0.0.1:8000/api/sensors/

---

## Project Structure

```
riversense/
├── manage.py
├── requirements.txt
├── db.sqlite3                  ← auto-created after migrate
│
├── riversense/                 ← Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── core/                       ← Main app
│   ├── models.py               ← SensorReading, TrashDetectionEvent, FloodAlert, ContactMessage
│   ├── views.py                ← All page + API views
│   ├── urls.py                 ← URL routing
│   ├── forms.py                ← LoginForm, ContactForm
│   ├── admin.py                ← Admin panel config
│   └── management/
│       └── commands/
│           └── seed_data.py    ← Sample data seeder
│
├── templates/
│   ├── base.html               ← Nav + Footer base
│   ├── registration/
│   │   └── login.html
│   └── core/
│       ├── home.html           ← Landing page
│       ├── dashboard.html      ← Live monitoring dashboard
│       ├── technology.html     ← Tech stack + YOLOv8 details
│       ├── about.html          ← Team + timeline
│       └── contact.html        ← Contact form
│
├── static/
│   ├── css/
│   │   └── main.css            ← Full design system
│   └── js/
│       └── main.js             ← Live updates, counters, nav
│
└── media/                      ← Uploaded detection images
```

---

## Key Features

| Feature | Details |
|---|---|
| **Live Sensor Data** | `/api/sensors/` returns simulated live water quality data, auto-refreshes every 5s |
| **Trash Detection Log** | Dashboard shows all YOLOv8 detection events with resolve action |
| **User Auth** | Login/logout with `LOGIN_REQUIRED` on dashboard |
| **Contact Form** | Saves to DB, viewable in Admin panel |
| **Admin Panel** | Full CRUD for all models at `/admin/` |
| **Seed Command** | `python manage.py seed_data` populates realistic sample data |
| **Responsive** | Mobile-first, works on all screen sizes |

---

## Database Models

### SensorReading
Stores live IoT sensor data: pH, DO, turbidity, temperature, BOD, water level, conductivity, TDS — per station per timestamp.

### TrashDetectionEvent
Stores YOLOv8 detection events: station, class (solo/cluster), confidence, alert level (auto-calculated), GPS coords, resolved status.

### FloodAlert
Stores flood risk alerts with predicted water level, risk level (safe/watch/warning/emergency), active status.

### ContactMessage
Stores contact form submissions with name, email, organization, message.

---

## Live API Endpoints

| Endpoint | Description |
|---|---|
| `GET /api/sensors/` | Live water quality data for all 5 stations (JSON) |
| `GET /api/detections/` | Recent unresolved trash detection events (JSON) |
| `POST /api/resolve/<id>/` | Mark a detection event as resolved |

---

## Connecting Real YOLOv8 Model

Replace the simulated data in `views.py` → `api_live_detections()` with actual inference:

```python
from ultralytics import YOLO
model = YOLO('path/to/best.pt')

def run_inference(frame_path):
    results = model(frame_path)
    detections = []
    for r in results:
        for box in r.boxes:
            detections.append({
                'class': 'cluster' if int(box.cls) == 1 else 'solo',
                'confidence': float(box.conf),
                'bbox': box.xyxy.tolist(),
            })
    return detections
```

---

## Connecting Real IoT Sensors

Replace the random data in `views.py` → `api_live_sensors()` with actual InfluxDB queries:

```python
from influxdb_client import InfluxDBClient

client = InfluxDBClient(url="http://localhost:8086", token="your-token", org="riversense")
query_api = client.query_api()

def get_latest_reading(station):
    query = f'''
    from(bucket: "riversense")
      |> range(start: -1h)
      |> filter(fn: (r) => r["station"] == "{station}")
      |> last()
    '''
    return query_api.query(query)
```

---

## Designed for
- AMC (Ahmedabad Municipal Corporation)
- SRFDCL (Sabarmati Riverfront Development Corporation Ltd.)
- Smart Cities Mission · AMRUT 2.0 · Namami Gange · Swachh Bharat
