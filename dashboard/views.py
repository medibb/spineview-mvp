from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import os
import csv
import math
import json
import tempfile

from .forms import CSVUploadForm
from .services.csv_parser import parse_movella_csv, get_metadata
from .services.fe_calculator import calculate_fe_angles
from .services.statistics import calculate_statistics

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
        Note: newer DOT CSVs use `SampleTimeFine` as microseconds since device start,
        so convert to seconds by dividing by 1_000_000.
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
            t_raw = float(row.get("SampleTimeFine", 0))
            w = float(row.get("Quat_W", 0))
            x = float(row.get("Quat_X", 0))
            y = float(row.get("Quat_Y", 0))
            z = float(row.get("Quat_Z", 0))
        except Exception:
            continue

        # Convert time to seconds. `SampleTimeFine` is provided in microseconds
        # (us) in the current CSVs, so divide by 1_000_000.
        t = t_raw / 1_000_000.0

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


# New Dashboard Views

def index(request):
    """Main dashboard page"""
    return render(request, 'dashboard/index.html')


@csrf_exempt
@require_http_methods(["POST"])
def upload_csv(request):
    """
    API endpoint for CSV file upload
    POST /api/upload/
    """
    try:
        form = CSVUploadForm(request.POST, request.FILES)

        if not form.is_valid():
            errors = []
            for field, error_list in form.errors.items():
                for error in error_list:
                    errors.append(f"{field}: {error}")
            return JsonResponse({
                'status': 'error',
                'errors': errors
            }, status=400)

        # Get uploaded files
        spine_file = request.FILES['spine_file']
        pelvis_file = request.FILES['pelvis_file']

        # Save files temporarily
        spine_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        pelvis_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')

        for chunk in spine_file.chunks():
            spine_temp.write(chunk)
        for chunk in pelvis_file.chunks():
            pelvis_temp.write(chunk)

        spine_temp.close()
        pelvis_temp.close()

        # Parse CSV files
        spine_df = parse_movella_csv(spine_temp.name)
        pelvis_df = parse_movella_csv(pelvis_temp.name)

        # Get metadata
        spine_meta = get_metadata(spine_df)
        pelvis_meta = get_metadata(pelvis_df)

        # Clean up temp files
        os.unlink(spine_temp.name)
        os.unlink(pelvis_temp.name)

        return JsonResponse({
            'status': 'success',
            'data': {
                'spine': {
                    'filename': spine_file.name,
                    'samples': spine_meta['total_samples'],
                    'duration_sec': spine_meta['duration_sec'],
                    'sample_rate': spine_meta['sample_rate'],
                },
                'pelvis': {
                    'filename': pelvis_file.name,
                    'samples': pelvis_meta['total_samples'],
                    'duration_sec': pelvis_meta['duration_sec'],
                    'sample_rate': pelvis_meta['sample_rate'],
                }
            }
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def analyze_data(request):
    """
    API endpoint for data analysis
    POST /api/analyze/
    """
    try:
        # Get uploaded files from request
        spine_file = request.FILES.get('spine_file')
        pelvis_file = request.FILES.get('pelvis_file')

        if not spine_file or not pelvis_file:
            return JsonResponse({
                'status': 'error',
                'message': 'Both spine and pelvis files are required'
            }, status=400)

        # Parse CSV files
        spine_df = parse_movella_csv(spine_file)
        pelvis_df = parse_movella_csv(pelvis_file)

        # Calculate FE angles
        fe_data = calculate_fe_angles(spine_df, pelvis_df)

        # Calculate statistics
        statistics = calculate_statistics(
            fe_data['time_series'],
            fe_data['angular_velocity'],
            fe_data['acceleration']
        )

        # Prepare response
        response_data = {
            'status': 'success',
            'data': {
                'time_series': fe_data['time_series'],
                'angular_velocity': fe_data['angular_velocity'],
                'acceleration': fe_data['acceleration'],
                'statistics': statistics,
                'metadata': {
                    **fe_data['metadata'],
                    'spine_file': spine_file.name,
                    'pelvis_file': pelvis_file.name,
                }
            }
        }

        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
