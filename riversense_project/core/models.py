from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class SensorReading(models.Model):
    """Live IoT sensor data from Sabarmati river stations"""
    STATION_CHOICES = [
        ('ellis_bridge', 'Ellis Bridge'),
        ('gandhi_bridge', 'Gandhi Bridge'),
        ('nehru_bridge', 'Nehru Bridge'),
        ('sardar_bridge', 'Sardar Bridge'),
        ('vasna_barrage', 'Vasna Barrage'),
    ]

    station = models.CharField(max_length=50, choices=STATION_CHOICES)
    timestamp = models.DateTimeField(default=timezone.now)

    # Water Quality Parameters
    ph = models.FloatField(null=True, blank=True, verbose_name='pH Level')
    dissolved_oxygen = models.FloatField(null=True, blank=True, verbose_name='Dissolved Oxygen (mg/L)')
    turbidity = models.FloatField(null=True, blank=True, verbose_name='Turbidity (NTU)')
    temperature = models.FloatField(null=True, blank=True, verbose_name='Temperature (°C)')
    bod = models.FloatField(null=True, blank=True, verbose_name='BOD (mg/L)')
    water_level = models.FloatField(null=True, blank=True, verbose_name='Water Level (m)')
    conductivity = models.FloatField(null=True, blank=True, verbose_name='Conductivity (µS/cm)')
    tds = models.FloatField(null=True, blank=True, verbose_name='TDS (mg/L)')

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Sensor Reading'
        verbose_name_plural = 'Sensor Readings'

    def __str__(self):
        return f"{self.get_station_display()} — {self.timestamp.strftime('%d %b %Y %H:%M')}"

    def ph_status(self):
        if self.ph is None:
            return 'unknown'
        if 6.5 <= self.ph <= 8.5:
            return 'good'
        elif 5.5 <= self.ph < 6.5 or 8.5 < self.ph <= 9.5:
            return 'warning'
        return 'danger'

    def do_status(self):
        if self.dissolved_oxygen is None:
            return 'unknown'
        if self.dissolved_oxygen >= 6:
            return 'good'
        elif self.dissolved_oxygen >= 4:
            return 'warning'
        return 'danger'


class TrashDetectionEvent(models.Model):
    """YOLOv8 trash detection events from CCTV cameras"""
    CLASS_CHOICES = [
        ('solo', 'Solo Trash'),
        ('cluster', 'Cluster Trash'),
    ]
    ALERT_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    STATION_CHOICES = [
        ('ellis_bridge', 'Ellis Bridge'),
        ('gandhi_bridge', 'Gandhi Bridge'),
        ('nehru_bridge', 'Nehru Bridge'),
        ('sardar_bridge', 'Sardar Bridge'),
        ('vasna_barrage', 'Vasna Barrage'),
    ]

    station = models.CharField(max_length=50, choices=STATION_CHOICES)
    timestamp = models.DateTimeField(default=timezone.now)
    trash_class = models.CharField(max_length=10, choices=CLASS_CHOICES)
    confidence = models.FloatField(verbose_name='Confidence Score')
    alert_level = models.CharField(max_length=10, choices=ALERT_CHOICES, default='low')
    latitude = models.FloatField(default=23.0225)
    longitude = models.FloatField(default=72.5714)
    resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    resolved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    image = models.ImageField(upload_to='detections/', null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Trash Detection Event'
        verbose_name_plural = 'Trash Detection Events'

    def __str__(self):
        return f"{self.get_trash_class_display()} at {self.get_station_display()} — {self.timestamp.strftime('%d %b %H:%M')}"

    def save(self, *args, **kwargs):
        if self.trash_class == 'cluster' and self.confidence > 0.75:
            self.alert_level = 'high'
        elif self.trash_class == 'cluster':
            self.alert_level = 'medium'
        else:
            self.alert_level = 'low'
        super().save(*args, **kwargs)


class FloodAlert(models.Model):
    """Flood risk alerts and predictions"""
    RISK_CHOICES = [
        ('safe', 'Safe'),
        ('watch', 'Watch'),
        ('warning', 'Warning'),
        ('emergency', 'Emergency'),
    ]

    station = models.CharField(max_length=50)
    timestamp = models.DateTimeField(default=timezone.now)
    water_level = models.FloatField(verbose_name='Water Level (m)')
    predicted_level = models.FloatField(null=True, blank=True, verbose_name='Predicted Level (m)')
    risk_level = models.CharField(max_length=20, choices=RISK_CHOICES, default='safe')
    message = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.station} — {self.get_risk_level_display()} — {self.timestamp.strftime('%d %b %H:%M')}"


class ContactMessage(models.Model):
    """Contact form submissions"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    organization = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.name} — {self.submitted_at.strftime('%d %b %Y')}"
