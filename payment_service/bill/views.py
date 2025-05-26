from django.shortcuts import render
import requests
import uuid
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
from django.urls import reverse
from core.utils.request_utils import extract_user_info_from_headers
# Create your views here.
APPOINTMENT_URL='http://service-appoinment:8003/api/appointments/'

def get_appointment_total_price(request, appointment_id):
    user_id, roles, error_response = extract_user_info_from_headers(request=request)
    
    if error_response:
        return error_response
    
    try:
        headers = {
            'X-User-Id': str(user_id),
            'X-User-Roles': str(roles).replace("'", '"')
        }

        appointment_response = requests.get(
            f"{APPOINTMENT_URL}{appointment_id}/total-price",
            headers=headers,
            timeout=15
        )

        if appointment_response.status_code == 200:
            appointment_detail = appointment_response.json()
            total_price = appointment_detail['totalPrice']
            paypal_dict = {
                'business': settings.PAYPAL_RECEIVER_EMAIL,
                'amount': total_price,
                'item_name': appointment_id,
                'invoice': str(uuid.uuid4()),
                'currency_code': 'USD',
                'notify_url': '{}{}'.format(settings.NGROK_STATIC_URL, reverse('paypal-ipn')),
                'return_url': '{}{}'.format(settings.NGROK_STATIC_URL, reverse('payment_success')),
                'cancel_return': '{}{}'.format(settings.NGROK_STATIC_URL, reverse('payment_failed')),
            }
            forms = PayPalPaymentsForm(paypal_dict)
            context = {
                "appointment_id": appointment_id,
                "price": appointment_detail['price'],
                "test_results": appointment_detail['test_results'],
                "totalPrice": total_price,
                "form": forms
            }
            return render(request, 'paypal_checkout.html', context)
        else:
            print(f"Appointment service returned status {appointment_response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Error calling appointment service: {str(e)}")


def get_payment_total_price_test(request):
    payment_data = {
        "appointment_id": "APT20240526-001",
        "price": "100.00",  # appointment price
        "test_results": [
            {
                "id": 1,
                "test_type_details": {
                    "name": "Complete Blood Count",
                    "cost": "50.00"
                },
                "price": "50.00",
                "status": "ORDERED"
            },
            {
                "id": 2,
                "test_type_details": {
                    "name": "Urine Analysis",
                    "cost": "30.00"
                },
                "price": "30.00",
                "status": "ORDERED"
            }
        ],
        "totalPrice": "180.00",  # 100 + 50 + 30
        "patient_name": "Nguyen Van A",
        "created_at": "2025-05-26T10:00:00",
        "currency": "USD"
    }
    total_price = payment_data['totalPrice']
    appointment_id = payment_data['appointment_id']
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': total_price,
        'item_name': appointment_id,
        'invoice': str(uuid.uuid4()),
        'currency_code': 'USD',
        'notify_url': '{}{}'.format(settings.NGROK_STATIC_URL, reverse('paypal-ipn')),
        'return_url': '{}{}'.format(settings.NGROK_STATIC_URL, reverse('payment_success')),
        'cancel_return': '{}{}'.format(settings.NGROK_STATIC_URL, reverse('payment_failed')),
    }
    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {
        "appointment_id": appointment_id,
        "price": payment_data['price'],
        "test_results": payment_data['test_results'],
        "totalPrice": total_price,
        "form": form
    }
    return render(request, 'paypal_checkout.html', context)

def payment_success(request):
    return render(request, 'payment_success.html', {})

def payment_failed(request):
    return render(request, 'payment_failed.html', {})