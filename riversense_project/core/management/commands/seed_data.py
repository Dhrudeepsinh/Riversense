import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import SensorReading, TrashDetectionEvent, FloodAlert


class Command(BaseCommand):
    help = 'Seed the database with sample RiverSense data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding sample data...')

        stations = ['ellis_bridge', 'gandhi_bridge', 'nehru_bridge', 'sardar_bridge', 'vasna_barrage']
        station_coords = {
            'ellis_bridge':  (23.0338, 72.5677),
            'gandhi_bridge': (23.0225, 72.5714),
            'nehru_bridge':  (23.0150, 72.5750),
            'sardar_bridge': (23.0450, 72.5640),
            'vasna_barrage': (22.9950, 72.5800),
        }

        # Sensor readings - last 48 hours, every 30 min
        SensorReading.objects.all().delete()
        now = timezone.now()
        for hours_ago in range(48, 0, -1):
            for station in stations:
                ts = now - timedelta(hours=hours_ago, minutes=random.randint(0, 29))
                SensorReading.objects.create(
                    station=station,
                    timestamp=ts,
                    ph=round(random.uniform(6.8, 8.4), 2),
                    dissolved_oxygen=round(random.uniform(4.5, 9.0), 2),
                    turbidity=round(random.uniform(5, 85), 1),
                    temperature=round(random.uniform(24, 35), 1),
                    bod=round(random.uniform(2, 14), 1),
                    water_level=round(random.uniform(1.5, 4.8), 2),
                    conductivity=round(random.uniform(200, 800), 1),
                    tds=round(random.uniform(150, 600), 0),
                )

        # Trash detection events - last 7 days
        TrashDetectionEvent.objects.all().delete()
        classes = ['solo', 'cluster']
        for day in range(7, 0, -1):
            events_per_day = random.randint(3, 20)
            for _ in range(events_per_day):
                station = random.choice(stations)
                lat, lng = station_coords[station]
                trash_class = random.choice(classes)
                conf = round(random.uniform(0.55, 0.99), 3)
                ts = now - timedelta(days=day, hours=random.randint(0, 23), minutes=random.randint(0, 59))
                TrashDetectionEvent.objects.create(
                    station=station,
                    timestamp=ts,
                    trash_class=trash_class,
                    confidence=conf,
                    latitude=lat + random.uniform(-0.002, 0.002),
                    longitude=lng + random.uniform(-0.002, 0.002),
                    resolved=random.choice([True, True, False]),
                )

        # Flood alerts
        FloodAlert.objects.all().delete()
        FloodAlert.objects.create(
            station='Vasna Barrage',
            water_level=3.2,
            predicted_level=3.8,
            risk_level='watch',
            message='Water level rising. Monitor closely. IMD forecasts moderate rain next 24h.',
            is_active=True,
        )
        FloodAlert.objects.create(
            station='Ellis Bridge',
            water_level=2.1,
            predicted_level=2.3,
            risk_level='safe',
            message='All normal. No flood risk detected.',
            is_active=False,
        )

        self.stdout.write(self.style.SUCCESS(
            f'Done! Created {SensorReading.objects.count()} sensor readings, '
            f'{TrashDetectionEvent.objects.count()} detection events, '
            f'{FloodAlert.objects.count()} flood alerts.'
        ))
