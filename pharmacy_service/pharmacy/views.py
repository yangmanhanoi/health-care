# pharmacy/views.py

from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

class PharmacyViewSet(viewsets.ModelViewSet):
    queryset = Pharmacy.objects.all()
    serializer_class = PharmacySerializer

    @action(detail=False, methods=['get'], url_path='all-medicines')
    def get_all_medicines(self, request):
        """
        Get all medicines from all pharmacies.
        """
        medicines = Medicine.objects.all()
        serializer = MedicineSerializer(medicines, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='medicines')
    def get_pharmacy_medicines(self, request, pk=None):
        """
        Get medicines for a specific pharmacy.
        """
        try:
            medicines = Medicine.objects.filter(pharmacy_id=pk)
            serializer = MedicineSerializer(medicines, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Pharmacy.DoesNotExist:
            return Response({'error': 'Pharmacy not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], url_path='check-medicine-availability')
    def check_medicine_availability(self, request, pk=None):
        """
        Check if a medicine is available in a specific pharmacy.
        URL query param: ?medicine_id=1
        """
        medicine_id = request.query_params.get('medicine_id')

        if not medicine_id:
            return Response({'error': 'medicine_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            medicine = Medicine.objects.get(id=medicine_id, pharmacy_id=pk)
            available = medicine.quantity > 0
            return Response({
                'medicine_id': medicine.id,
                'medicine_name': medicine.name,
                'available': available,
                'stock': medicine.quantity
            }, status=status.HTTP_200_OK)
        except Medicine.DoesNotExist:
            return Response({'available': False, 'message': 'Medicine not found in this pharmacy'}, status=status.HTTP_404_NOT_FOUND)


class PharmacistViewSet(viewsets.ModelViewSet):
    queryset = Pharmacist.objects.all()
    serializer_class = PharmacistSerializer

class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer

class DispenseRecordViewSet(viewsets.ModelViewSet):
    queryset = DispenseRecord.objects.all()
    serializer_class = DispenseRecordSerializer

class DispenseItemViewSet(viewsets.ModelViewSet):
    queryset = DispenseItem.objects.all()
    serializer_class = DispenseItemSerializer
