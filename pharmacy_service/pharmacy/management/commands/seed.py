from django.core.management.base import BaseCommand
from pharmacy.models import Pharmacy, Medicine

class Command(BaseCommand):
    help = 'Seed the database with two pharmacies and their medicines'

    def handle(self, *args, **kwargs):
        # Clear existing data
        Medicine.objects.all().delete()
        Pharmacy.objects.all().delete()

        # Create two pharmacies
        pharmacy1 = Pharmacy.objects.create(
            name="City Pharmacy",
            contact_number="0123456789",
            address="123 Main Street, District 1"
        )

        pharmacy2 = Pharmacy.objects.create(
            name="GreenHealth Pharmacy",
            contact_number="0987654321",
            address="456 Central Ave, District 2"
        )


        # Medicines for each pharmacy
        pharmacy1_meds = [
            {"name": "Paracetamol", "description": "Pain reliever", "quantity": 100, "price": 5.0},
            {"name": "Amoxicillin", "description": "Antibiotic", "quantity": 60, "price": 10.0},
            {"name": "Loratadine", "description": "Allergy relief", "quantity": 50, "price": 7.5},
        ]

        pharmacy2_meds = [
            {"name": "Ibuprofen", "description": "Anti-inflammatory", "quantity": 80, "price": 8.0},
            {"name": "Cetirizine", "description": "Antihistamine", "quantity": 45, "price": 4.5},
            {"name": "Omeprazole", "description": "Acid reflux treatment", "quantity": 70, "price": 6.5},
        ]

        for med in pharmacy1_meds:
            Medicine.objects.create(pharmacy=pharmacy1, **med)

        for med in pharmacy2_meds:
            Medicine.objects.create(pharmacy=pharmacy2, **med)

        self.stdout.write(self.style.SUCCESS("✅ Seeded 2 pharmacies and their medicines successfully."))
