from django.contrib import admin
from .models import SensorReading, TrashDetectionEvent, FloodAlert, ContactMessage


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ['station', 'timestamp', 'ph', 'dissolved_oxygen', 'turbidity', 'temperature', 'water_level']
    list_filter = ['station']
    date_hierarchy = 'timestamp'


@admin.register(TrashDetectionEvent)
class TrashDetectionEventAdmin(admin.ModelAdmin):
    list_display = ['station', 'trash_class', 'confidence', 'alert_level', 'timestamp', 'resolved']
    list_filter = ['trash_class', 'alert_level', 'resolved', 'station']
    date_hierarchy = 'timestamp'
    actions = ['mark_resolved']

    def mark_resolved(self, request, queryset):
        queryset.update(resolved=True, resolved_by=request.user)
    mark_resolved.short_description = 'Mark selected as resolved'


@admin.register(FloodAlert)
class FloodAlertAdmin(admin.ModelAdmin):
    list_display = ['station', 'risk_level', 'water_level', 'timestamp', 'is_active']
    list_filter = ['risk_level', 'is_active']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'organization', 'submitted_at', 'is_read']
    list_filter = ['is_read']
