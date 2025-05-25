from django.urls import path
from .views import *

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('register/patient', RegisterPatientView.as_view(), name='register-patient'),
    path('register/doctor', register_doctor, name='register-doctor')
]
