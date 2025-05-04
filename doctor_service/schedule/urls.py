from django.urls import path, include
from .views import *
urlpatterns = [
    path('availabilities', availability_list_create, name='availability-list-create'),
    path('availabilities/<int:pk>', availability_detail, name='availability-detail'),
    path('availabilities/doctor/<int:doctor_id>', get_availability_by_doctor, name='get-availability-by-doctor'),
    path('availabilities/doctor/<int:doctor_id>/<str:date>', get_availability_by_doctor_and_date_and_time, name='get-availability-by-doctor-and-date-and_time'),
]
