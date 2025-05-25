from django.urls import path
from . import views

urlpatterns = [
    # Health check endpoint
    path('health/', views.health_check, name='health-check'),

    # List all prescriptions or create a new one
    path('', views.prescription_list_create, name='prescription-list-create'),


    # Retrieve, update or delete a prescription
    path('<int:pk>/', views.prescription_detail, name='prescription-detail'),

    # List all prescriptions for a specific patient
    path('patient/<int:patient_id>/', views.patient_prescriptions, name='patient-prescriptions'),

    # List all prescriptions by a specific doctor
    path('doctor/<int:doctor_id>/', views.doctor_prescriptions, name='doctor-prescriptions'),

    # Verify if a prescription is valid for dispensing
    path('<int:pk>/verify/', views.verify_prescription, name='verify-prescription'),

    # Update the status of a prescription
    path('<int:pk>/status/', views.update_prescription_status, name='update-prescription-status'),

    # Search medications from pharmacy service
    path('medications/search/', views.search_medications, name='search-medications'),


]
