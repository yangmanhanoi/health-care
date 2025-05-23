# pharmacy/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'pharmacies', PharmacyViewSet)     #GET /pharmacy/all-medicines/
router.register(r'pharmacists', PharmacistViewSet)
router.register(r'medicines', MedicineViewSet)
router.register(r'dispense-records', DispenseRecordViewSet)
router.register(r'dispense-items', DispenseItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
