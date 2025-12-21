from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard_home, name="dashboard_home"),
    path("mvp/", views.mvp_view, name="mvp_view"),
    path("api/sessions/<int:session_id>/series/", views.session_series_api, name="session_series_api"),
]
