from django.urls import path, include
from .views import *
urlpatterns = [
    path('info', create_doctor, name='create-doctor-info'),
    path('doctors/<int:user_id>/', get_doctor_profile, name='get_doctor_profile'),
    path('doctors/update/<int:user_id>', update_doctor_profile, name='update_doctor_profile')
]