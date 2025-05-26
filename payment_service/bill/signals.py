from django.conf import settings
from django.dispatch import receiver
from paypal.standard.ipn.signals import valid_ipn_received

@receiver(valid_ipn_received)
def paypal_payment_receiver(sender, **kwargs):
    ipn = sender
    item_name = ipn.item_name
    amount = ipn.mc_gross
    invoice_id = ipn.invoice
    payer_email = ipn.payer_email
    print(ipn)
    print(f"Amount: {ipn.mc_gross}, item_name: {item_name}, payer_email: {payer_email}")