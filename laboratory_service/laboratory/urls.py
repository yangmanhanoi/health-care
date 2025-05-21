from django.urls import path
from . import views

urlpatterns = [
    # Health check endpoint
    path('health/', views.health_check, name='health-check'),
    
    # Test Type endpoints
    path('testtypes/', views.test_type_list_create, name='test-type-list-create'),
    path('testtypes/<int:pk>/', views.test_type_detail, name='test-type-detail'),
    
    # Lab Test Order endpoints
    path('', views.lab_test_order_list_create, name='lab-test-order-list-create'),
    path('<int:pk>/', views.lab_test_order_detail, name='lab-test-order-detail'),
    path('patient/<int:patient_id>/', views.patient_lab_test_orders, name='patient-lab-test-orders'),
    path('doctor/<int:doctor_id>/', views.doctor_lab_test_orders, name='doctor-lab-test-orders'),
    path('<int:pk>/status/', views.update_lab_test_order_status, name='update-lab-test-order-status'),
    
    # Test Result endpoints
    path('results/upload/<int:order_item_id>/', views.upload_test_result, name='upload-test-result'),
    path('results/<int:result_id>/', views.update_test_result, name='update-test-result'),
]
