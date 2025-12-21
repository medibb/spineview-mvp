from django.contrib import admin
from .models import Patient, Session, SensorSeries

admin.site.register(Patient)
admin.site.register(Session)
admin.site.register(SensorSeries)
