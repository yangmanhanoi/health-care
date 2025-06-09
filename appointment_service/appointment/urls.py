from django.contrib import admin
from django.urls import path
from .views import *
urlpatterns = [
    path('admin/', admin.site.urls),
    path('patient', patient_appointment_list_create, name='patient-list-create'),
    path('<int:appointment_id>/check-in', check_in_appointment, name='check-in-appointment'),
    path('<int:appointment_id>/diagnose', diagnose_appointment, name='diagnose-appointment'),
    path('<int:appointment_id>/complete-lab-test', complete_lab_test, name='complete-lab-test'),
    path('<int:appointment_id>/conclusion', conclude_appointment, name='conclude-appointment'),
    path('<int:appointment_id>/total-price', get_appointment_total_price, name='get-appointment-total-price'),
    # Doctor endpoints
    path('doctor', doctor_appointment_list, name='doctor-appointment-list'),
    path('doctor/<int:appointment_id>', doctor_appointment_detail, name='doctor-appointment-detail'),

    # New API endpoints for calling doctor and patient services
    path('doctor-info/<int:doctor_id>', get_doctor_info, name='get-doctor-info'),
    path('patient-info/<int:patient_id>', get_patient_info, name='get-patient-info'),
    path('<int:appointment_id>/full-details', get_appointment_full_details, name='get-appointment-full-details'),
    path('search-doctors', search_doctors, name='search-doctors'),
    path('patient-history/<int:patient_id>', get_patient_history, name='get-patient-history'),
    path('all-enriched', get_all_appointments_enriched, name='get-all-appointments-enriched'),

    # Test endpoint
    path('test-patient-service', test_patient_service, name='test-patient-service'),
]