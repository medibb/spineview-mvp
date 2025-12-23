from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("legacy/", views.dashboard_home, name="dashboard_home"),
    path("mvp/", views.mvp_view, name="mvp_view"),
    path("api/sessions/<int:session_id>/series/", views.session_series_api, name="session_series_api"),
    path("api/upload/", views.upload_csv, name="upload_csv"),
    path("api/analyze/", views.analyze_data, name="analyze_data"),
]
