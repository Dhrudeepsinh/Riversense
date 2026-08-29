from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Auth
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),
    path('register/', views.register_view, name='register'),

    # Pages
    path('dashboard/',  views.dashboard,  name='dashboard'),
    path('technology/', views.technology, name='technology'),
    path('about/',      views.about,      name='about'),
    path('contact/',    views.contact,    name='contact'),

    # Live read APIs (frontend polls these every 5s)
    path('api/sensors/',          views.api_live_sensors,    name='api_sensors'),
    path('api/detections/',       views.api_live_detections, name='api_detections'),
    path('api/resolve/<int:pk>/', views.resolve_detection,   name='resolve_detection'),

    # Push APIs (hardware/YOLOv8 script POSTs to these)
    path('api/push/sensor/',    views.api_push_sensor,    name='api_push_sensor'),
    path('api/push/detection/', views.api_push_detection, name='api_push_detection'),

    
]