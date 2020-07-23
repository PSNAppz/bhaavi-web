from django.urls import path
from . import views

urlpatterns = [
    # Mentor Dash
    path('mentorboard/', views.mentorDashboard, name="mentorboard"),
    path('mentorboard/viewDetails', views.mentorDetailsView, name="view_details_mentor"),
    path('mentorboard/prevDetails', views.mentorHistory, name="view_history_mentor"),
    path('mentorboard/submitReport', views.submitReport, name="submit_report"),
    path('dashboard/conference/end/<reqid>', views.endCall, name="end_call"),

    path('dashboard/careerReport/<id>', views.submitCareerReport, name="career-report"),
]
