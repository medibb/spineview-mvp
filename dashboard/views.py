from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.conf import settings
import os
import csv
import math
import json

try:
    from .models import Session, SensorSeries  # optional existing models
except Exception:
    Session = None
    SensorSeries = None


def dashboard_home(request):
    # keep legacy dashboard if models exist
    if Session is not None:
        sessions = Session.objects.select_related("patient").order_by("-started_at")[:20]
    else:
        sessions = []
    return render(request, "dashboard/home.html", {"sessions": sessions})


def session_series_api(request, session_id: int):
    if Session is None:
        return JsonResponse({"error": "models not available"}, status=404)
    session = get_object_or_404(Session, id=session_id)
    series = SensorSeries.objects.filter(session=session).order_by("sensor_name")

    payload = {
        "session": {
            "id": session.id,
            "patient_mrn": session.patient.mrn,
            "started_at": session.started_at.isoformat(),
            "note": session.note,
        },
        "series": [
            {
                "sensor_name": s.sensor_name,
                "axis": s.axis,
                "sample_rate_hz": s.sample_rate_hz,
                "data": s.data_json,
            }
            for s in series
        ],
    }
    return JsonResponse(payload)


def _parse_dot_csv(path):
    """Parse an Xsens DOT CSV file located at `path`.

    Skips preamble/metadata until the header line starting with 'PacketCounter'.
    Returns lists: times (s) and FE angles (degrees) where FE is taken as the
    Tait-Bryan 'pitch' angle from the quaternion (w,x,y,z) using the convention:
      roll = atan2(2*(w*x + y*z), 1 - 2*(x*x + y*y))
      pitch = asin(clamp(2*(w*y - z*x), -1, 1))
      yaw = atan2(2*(w*z + x*y), 1 - 2*(y*y + z*z))
    """
    if not os.path.exists(path):
        return [], []

    with open(path, newline="") as fh:
        lines = fh.readlines()

    header_idx = None
    for i, ln in enumerate(lines):
        if ln.strip().startswith("PacketCounter"):
            header_idx = i
            break
    if header_idx is None:
        return [], []

    reader = csv.DictReader(lines[header_idx:])
    times = []
    angles = []
    for row in reader:
        try:
            t_ms = float(row.get("SampleTimeFine", 0))
            w = float(row.get("Quat_W", 0))
            x = float(row.get("Quat_X", 0))
            y = float(row.get("Quat_Y", 0))
            z = float(row.get("Quat_Z", 0))
        except Exception:
            continue

        # Convert time to seconds (SampleTimeFine appears in ms)
        t = t_ms / 1000.0

        # compute pitch (FE) from quaternion
        t2 = 2.0 * (w * y - z * x)
        if t2 > 1.0:
            t2 = 1.0
        if t2 < -1.0:
            t2 = -1.0
        pitch = math.asin(t2)
        pitch_deg = math.degrees(pitch)

        times.append(t)
        angles.append(pitch_deg)

    return times, angles


def mvp_view(request):
    """Minimal single-page MVP: read sample CSVs, compute FE angles, and show Chart.js plot."""
    base = getattr(settings, "BASE_DIR", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    spine_path = os.path.join(base, "data", "spine_dot.csv")
    pelvis_path = os.path.join(base, "data", "pelvis_dot.csv")

    spine_t, spine_angles = _parse_dot_csv(spine_path)
    pelvis_t, pelvis_angles = _parse_dot_csv(pelvis_path)

    # Align lengths (use minimum length)
    n = min(len(spine_t), len(pelvis_t), len(spine_angles), len(pelvis_angles))
    times = spine_t[:n]
    spine_angles = spine_angles[:n]
    pelvis_angles = pelvis_angles[:n]
    relative = [s - p for s, p in zip(spine_angles, pelvis_angles)]

    context = {
        "times_json": json.dumps(times),
        "spine_json": json.dumps(spine_angles),
        "pelvis_json": json.dumps(pelvis_angles),
        "relative_json": json.dumps(relative),
    }
    return render(request, "dashboard/mvp.html", context)
