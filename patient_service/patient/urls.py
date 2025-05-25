from django.urls import path
from .views import (
    patient_list_create, patient_detail, patient_history,
    register_patient, update_patient_profile
)
from .auth_integration import register_patient_from_auth

urlpatterns = [
    path('', patient_list_create, name='patient-list-create'),
    path('<int:patient_id>', patient_detail, name='patient-detail'),
    path('<int:patient_id>/history', patient_history, name='patient-history'),
    path('register', register_patient, name='register-patient'),
    path('<int:patient_id>/update', update_patient_profile, name='update-patient-profile'),
    path('auth/register', register_patient_from_auth, name='register-patient-from-auth'),
]
