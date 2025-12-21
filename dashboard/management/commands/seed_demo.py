import math
import random
from datetime import datetime, timezone

from django.core.management.base import BaseCommand
from dashboard.models import Patient, Session, SensorSeries

class Command(BaseCommand):
    help = "Seed demo data for dashboard"

    def handle(self, *args, **options):
        SensorSeries.objects.all().delete()
        Session.objects.all().delete()
        Patient.objects.all().delete()

        p = Patient.objects.create(mrn="DEMO-0001", name="Demo Patient")
        s = Session.objects.create(patient=p, started_at=datetime.now(timezone.utc), note="Demo squat")

        sr = 100  # Hz
        n = 600   # 6 seconds

        def make_series(phase: float):
            data = []
            for i in range(n):
                t = i / sr
                v = 0.8 * math.sin(2 * math.pi * 1.2 * t + phase) + 0.08 * random.uniform(-1, 1)
                data.append({"t": round(t, 3), "v": round(v, 4)})
            return data

        SensorSeries.objects.create(session=s, sensor_name="IMU_A", axis="z", sample_rate_hz=sr, data_json=make_series(0.0))
        SensorSeries.objects.create(session=s, sensor_name="IMU_B", axis="z", sample_rate_hz=sr, data_json=make_series(0.6))

        self.stdout.write(self.style.SUCCESS("Seeded demo data."))
