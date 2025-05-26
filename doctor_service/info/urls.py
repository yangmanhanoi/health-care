from django.urls import path, include
from .views import *
urlpatterns = [
    path('', create_doctor, name='create-doctor-info'),
    path('doctors/', list_doctors, name='list-doctors'),
    path('doctors/profile/<int:user_id>', get_doctor_profile, name='get_doctor_profile'),
    path('doctors/update/<int:user_id>', update_doctor_profile, name='update_doctor_profile'),
    path('doctors/<int:doctor_id>', get_doctor, name='get_doctor'),
]