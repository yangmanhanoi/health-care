from django.urls import path
from .views import *

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('register/customer', RegisterCustomerView.as_view(), name='register-customer'),
    path('register/doctor', register_doctor, name='register-doctor')
]
