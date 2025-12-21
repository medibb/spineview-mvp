from django.db import models

class Patient(models.Model):
    mrn = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return f"{self.mrn} {self.name}".strip()

class Session(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    started_at = models.DateTimeField()
    note = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Session {self.id} ({self.patient.mrn})"

class SensorSeries(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    sensor_name = models.CharField(max_length=32)  # IMU_A / IMU_B
    axis = models.CharField(max_length=8, default="z")
    sample_rate_hz = models.IntegerField(default=100)
    data_json = models.JSONField()  # [{"t":0.00,"v":0.12}, ...]

    def __str__(self):
        return f"{self.session.id}-{self.sensor_name}-{self.axis}"
