from django.contrib import admin
from django.urls import path, include
from .views import *
urlpatterns = [
    path('admin/', admin.site.urls),
    path('patient', patient_appointment_list_create, name='patient-list-create'),
    path('appointments/<int:appointment_id>/status/', update_appointment_status, name='update-appointment-status'),
]