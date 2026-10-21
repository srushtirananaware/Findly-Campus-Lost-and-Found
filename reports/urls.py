
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("accounts/signup/", views.signup, name="signup"),
    path("reports/", views.report_list, name="report_list"),
    path("reports/new/", views.report_create, name="report_create"),
    path("reports/<int:pk>/", views.report_detail, name="report_detail"),
    path("reports/<int:pk>/edit/", views.report_edit, name="report_edit"),
    path("reports/<int:pk>/status/", views.report_status, name="report_status"),
    path("reports/<int:pk>/matches/", views.matches, name="matches"),
    path("reports/<int:pk>/message/", views.send_message, name="send_message"),
    path("reports/<int:pk>/claim/", views.claim_create, name="claim_create"),
    path("reports/<int:pk>/claims/<int:claim_id>/decision/", views.claim_decision, name="claim_decision"),
    path("reports/<int:pk>/flag/", views.flag_report, name="flag_report"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("notifications/<int:pk>/read/", views.notification_read, name="notification_read"),
]
