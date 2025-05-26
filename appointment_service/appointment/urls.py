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
]