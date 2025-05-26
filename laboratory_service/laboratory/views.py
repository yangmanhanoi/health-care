from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from .models import TestType, LabTestOrder, LabTestOrderItem, TestResult, LabTestOrderStatus
from .serializers import (
    TestTypeSerializer,
    LabTestOrderSerializer,
    LabTestOrderItemSerializer,
    TestResultSerializer,
    LabTestOrderStatusUpdateSerializer,
    LabTestOrderItemStatusUpdateSerializer
)
from core.utils.request_utils import extract_user_info_from_headers
from django.db import connection
import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@api_view(['GET'])
@authentication_classes([])  # No authentication required
@permission_classes([])      # No permissions required
def health_check(request):
    """
    Health check endpoint to verify the service is running correctly
    """
    # Check database connection
    db_status = "OK"
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception as e:
        db_status = f"ERROR: {str(e)}"

    # Return health status
    return Response({
        "status": "UP",
        "timestamp": datetime.datetime.now().isoformat(),
        "service": "laboratory-service",
        "database": db_status,
        "version": "1.0.0"
    })

@api_view(['GET', 'POST'])
@authentication_classes([])  # No authentication required
@permission_classes([])      # No permissions required
def test_type_list_create(request):
    """
    List all test types or create a new test type
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    if request.method == 'GET':
        test_types = TestType.objects.all()
        serializer = TestTypeSerializer(test_types, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Only admins and lab technicians can create test types
        if not ('ADMIN' in roles or 'LAB_TECHNICIAN' in roles):
            return Response({"message": "Only admins and lab technicians can create test types"},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = TestTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([])  # No authentication required
@permission_classes([])      # No permissions required
def test_type_detail(request, pk):
    """
    Retrieve, update or delete a test type
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    try:
        test_type = TestType.objects.get(pk=pk)
    except TestType.DoesNotExist:
        return Response({"message": "Test type not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TestTypeSerializer(test_type)
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Only admins and lab technicians can update test types
        if not ('ADMIN' in roles or 'LAB_TECHNICIAN' in roles):
            return Response({"message": "Only admins and lab technicians can update test types"},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = TestTypeSerializer(test_type, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Only admins can delete test types
        if 'ADMIN' not in roles:
            return Response({"message": "Only admins can delete test types"},
                            status=status.HTTP_403_FORBIDDEN)

        test_type.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
@authentication_classes([])  # No authentication required
@permission_classes([])      # No permissions required
def lab_test_order_list_create(request):
    """
    List all lab test orders or create a new lab test order
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    if request.method == 'GET':
        # Filter lab test orders based on user role
        if 'DOCTOR' in roles:
            lab_test_orders = LabTestOrder.objects.filter(doctor_id=user_id)
        elif 'PATIENT' in roles or 'CUSTOMER' in roles:
            lab_test_orders = LabTestOrder.objects.filter(patient_id=user_id)
        elif 'ADMIN' in roles or 'LAB_TECHNICIAN' in roles:
            lab_test_orders = LabTestOrder.objects.all()
        else:
            return Response({"message": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        serializer = LabTestOrderSerializer(lab_test_orders, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Only doctors can create lab test orders
        if 'DOCTOR' not in roles:
            return Response({"message": "Only doctors can create lab test orders"},
                            status=status.HTTP_403_FORBIDDEN)

        # Set the doctor_id to the authenticated user's ID
        data = request.data.copy()
        data['doctor_id'] = user_id
        data['status'] = LabTestOrderStatus.ORDERED

        serializer = LabTestOrderSerializer(data=data)
        if serializer.is_valid():
            lab_test_order = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([])  # No authentication required
@permission_classes([])      # No permissions required
def lab_test_order_detail(request, pk):
    """
    Retrieve, update or delete a lab test order
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    try:
        lab_test_order = LabTestOrder.objects.get(pk=pk)
    except LabTestOrder.DoesNotExist:
        return Response({"message": "Lab test order not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # Check permissions
        if not ('ADMIN' in roles or 'LAB_TECHNICIAN' in roles or
                ('DOCTOR' in roles and lab_test_order.doctor_id == user_id) or
                (('PATIENT' in roles or 'CUSTOMER' in roles) and lab_test_order.patient_id == user_id)):
            return Response({"message": "You don't have permission to view this lab test order"},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = LabTestOrderSerializer(lab_test_order)
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Only the ordering doctor can update the lab test order
        if not ('ADMIN' in roles or
                ('DOCTOR' in roles and lab_test_order.doctor_id == user_id)):
            return Response({"message": "Only the ordering doctor can update this lab test order"},
                            status=status.HTTP_403_FORBIDDEN)

        # Don't allow status changes through this endpoint
        data = request.data.copy()
        if 'status' in data and data['status'] != lab_test_order.status:
            return Response({"message": "Use the status update endpoint to change the status"},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = LabTestOrderSerializer(lab_test_order, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Only the ordering doctor or an admin can cancel a lab test order
        if not ('ADMIN' in roles or
                ('DOCTOR' in roles and lab_test_order.doctor_id == user_id)):
            return Response({"message": "Only the ordering doctor can cancel this lab test order"},
                            status=status.HTTP_403_FORBIDDEN)

        # Don't actually delete, just set status to CANCELLED
        lab_test_order.status = LabTestOrderStatus.CANCELLED
        lab_test_order.save()

        # Also cancel all items
        for item in lab_test_order.items.all():
            item.status = LabTestOrderStatus.CANCELLED
            item.save()

        return Response({"message": "Lab test order cancelled"}, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([])  # No authentication required
@permission_classes([])      # No permissions required
def patient_lab_test_orders(request, patient_id):
    """
    List all lab test orders for a specific patient
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    # Check permissions
    if not ('ADMIN' in roles or 'LAB_TECHNICIAN' in roles or 'DOCTOR' in roles or
            (('PATIENT' in roles or 'CUSTOMER' in roles) and int(patient_id) == user_id)):
        return Response({"message": "You don't have permission to access these lab test orders"},
                        status=status.HTTP_403_FORBIDDEN)

    lab_test_orders = LabTestOrder.objects.filter(patient_id=patient_id)
    serializer = LabTestOrderSerializer(lab_test_orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@authentication_classes([])  # No authentication required
@permission_classes([])      # No permissions required
def doctor_lab_test_orders(request, doctor_id):
    """
    List all lab test orders by a specific doctor
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    # Check permissions
    if not ('ADMIN' in roles or 'LAB_TECHNICIAN' in roles or
            ('DOCTOR' in roles and int(doctor_id) == user_id)):
        return Response({"message": "You don't have permission to access these lab test orders"},
                        status=status.HTTP_403_FORBIDDEN)

    lab_test_orders = LabTestOrder.objects.filter(doctor_id=doctor_id)
    serializer = LabTestOrderSerializer(lab_test_orders, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
@authentication_classes([])  # No authentication required
@permission_classes([])      # No permissions required
def update_lab_test_order_status(request, pk):
    """
    Update the status of a lab test order
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    try:
        lab_test_order = LabTestOrder.objects.get(pk=pk)
    except LabTestOrder.DoesNotExist:
        return Response({"message": "Lab test order not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check permissions based on the requested status change
    new_status = request.data.get('status')

    # Only lab technicians and admins can update to certain statuses
    if new_status in [LabTestOrderStatus.SAMPLE_COLLECTED, LabTestOrderStatus.IN_PROGRESS, LabTestOrderStatus.COMPLETED]:
        if not ('ADMIN' in roles or 'LAB_TECHNICIAN' in roles):
            return Response({"message": "Only lab technicians can update to this status"},
                            status=status.HTTP_403_FORBIDDEN)

    # Only doctors and admins can cancel
    elif new_status == LabTestOrderStatus.CANCELLED:
        if not ('ADMIN' in roles or
                ('DOCTOR' in roles and lab_test_order.doctor_id == user_id)):
            return Response({"message": "Only the ordering doctor can cancel this lab test order"},
                            status=status.HTTP_403_FORBIDDEN)

    # Validate and update the status
    serializer = LabTestOrderStatusUpdateSerializer(lab_test_order, data=request.data)
    if serializer.is_valid():
        # Update the status
        lab_test_order = serializer.save()

        # If completing the order, set the completion date
        if new_status == LabTestOrderStatus.COMPLETED:
            lab_test_order.completion_date = datetime.datetime.now()
            lab_test_order.save()

        # If collecting the sample, set the collection date
        elif new_status == LabTestOrderStatus.SAMPLE_COLLECTED:
            lab_test_order.collection_date = datetime.datetime.now()
            lab_test_order.save()

        return Response(LabTestOrderSerializer(lab_test_order).data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([])  # No authentication required
@permission_classes([])      # No permissions required
def upload_test_result(request, order_item_id):
    """
    Upload a test result for a specific lab test order item
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    # Only doctors, lab technicians and admins can upload results
    if not ('ADMIN' in roles or 'LAB_TECHNICIAN' in roles or 'DOCTOR' in roles):
        return Response({"message": "Only doctors, lab technicians and admins can upload test results"},
                        status=status.HTTP_403_FORBIDDEN)

    try:
        order_item = LabTestOrderItem.objects.get(pk=order_item_id)
    except LabTestOrderItem.DoesNotExist:
        return Response({"message": "Lab test order item not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check if a result already exists
    try:
        existing_result = TestResult.objects.get(order_item=order_item)
        return Response({"message": "A result already exists for this test. Update it instead."},
                        status=status.HTTP_400_BAD_REQUEST)
    except TestResult.DoesNotExist:
        pass

    # Add the order_item and verified_by to the data
    data = request.data.copy()
    data['order_item'] = order_item_id
    data['verified_by'] = user_id

    serializer = TestResultSerializer(data=data)
    if serializer.is_valid():
        # Save the result
        test_result = serializer.save()

        # Update the order item status to COMPLETED
        order_item.status = LabTestOrderStatus.COMPLETED
        order_item.save()

        # Check if all items in the order are completed
        all_completed = True
        for item in order_item.order.items.all():
            if item.status != LabTestOrderStatus.COMPLETED:
                all_completed = False
                break

        # If all items are completed, update the order status
        if all_completed:
            order = order_item.order
            order.status = LabTestOrderStatus.COMPLETED
            order.completion_date = datetime.datetime.now()
            order.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([])  # No authentication required
@permission_classes([])      # No permissions required
def appointment_test_items(request, appointment_id):
    """
    Get all test items for a specific appointment with pricing information
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    try:
        # Get all lab test orders for this appointment
        lab_test_orders = LabTestOrder.objects.filter(appointment_id=appointment_id)

        if not lab_test_orders.exists():
            return Response({
                "message": "No lab test orders found for this appointment",
                "appointment_id": appointment_id,
                "test_items": []
            }, status=status.HTTP_200_OK)

        # Check permissions - users can only view their own appointment test items
        first_order = lab_test_orders.first()
        if not ('ADMIN' in roles or 'LAB_TECHNICIAN' in roles or
                ('DOCTOR' in roles and first_order.doctor_id == user_id) or
                (('PATIENT' in roles or 'CUSTOMER' in roles) and first_order.patient_id == user_id)):
            return Response({"message": "You don't have permission to view these test items"},
                            status=status.HTTP_403_FORBIDDEN)

        # Collect all test items from all orders for this appointment
        all_test_items = []
        total_cost = 0

        for order in lab_test_orders:
            for item in order.items.all():
                all_test_items.append(item)
                total_cost += item.price

        # Serialize the test items
        serializer = LabTestOrderItemSerializer(all_test_items, many=True)

        return Response({
            "appointment_id": appointment_id,
            "total_test_items": len(all_test_items),
            "total_cost": total_cost,
            "test_items": serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error retrieving test items for appointment {appointment_id}: {str(e)}")
        return Response(
            {"message": "An error occurred while retrieving test items"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PUT'])
@authentication_classes([])  # No authentication required
@permission_classes([])      # No permissions required
def update_test_result(request, result_id):
    """
    Update an existing test result
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    # Only doctors, lab technicians and admins can update results
    if not ('ADMIN' in roles or 'LAB_TECHNICIAN' in roles or 'DOCTOR' in roles):
        return Response({"message": "Only doctors, lab technicians and admins can update test results"},
                        status=status.HTTP_403_FORBIDDEN)

    try:
        test_result = TestResult.objects.get(pk=result_id)
    except TestResult.DoesNotExist:
        return Response({"message": "Test result not found"}, status=status.HTTP_404_NOT_FOUND)

    # Update the verified_by field
    data = request.data.copy()
    data['verified_by'] = user_id

    serializer = TestResultSerializer(test_result, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
