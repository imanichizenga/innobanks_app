from django.apps import AppConfig
import os

class AttendanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'attendance'
    path = os.path.dirname(os.path.abspath(__file__))
