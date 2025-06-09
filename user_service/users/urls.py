from django.urls import path
from . import views

urlpatterns = [
    # General user endpoints
    path('users/', views.UserListCreateView.as_view(), name='user-list-create'),
    path('users/<uuid:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    
    # User lookup endpoints
    path('users/auth/<int:auth_user_id>/', views.get_user_by_auth_id, name='user-by-auth-id'),
    path('users/email/<str:email>/', views.get_user_by_email, name='user-by-email'),
    
    # Specialized user creation endpoints
    path('users/doctors/create/', views.create_doctor_user, name='create-doctor-user'),
    path('users/patients/create/', views.create_patient_user, name='create-patient-user'),
    
    # User type specific endpoints
    path('users/doctors/', views.get_doctors, name='get-doctors'),
    path('users/patients/', views.get_patients, name='get-patients'),
    
    # User management endpoints
    path('users/<uuid:user_id>/login/', views.update_last_login, name='update-last-login'),
    path('users/<uuid:user_id>/verify/', views.verify_user, name='verify-user'),
    path('users/<uuid:user_id>/deactivate/', views.deactivate_user, name='deactivate-user'),
    path('users/<uuid:user_id>/activate/', views.activate_user, name='activate-user'),
    
    # Activity tracking endpoints
    path('activities/', views.log_user_activity, name='log-user-activity'),
    path('users/<uuid:user_id>/activities/', views.get_user_activities, name='get-user-activities'),
    
    # Health check
    path('health/', views.health_check, name='health-check'),
]
