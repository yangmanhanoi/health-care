from django.test import TestCase
from .models import Patient
from datetime import date

class PatientModelTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.patient_data = {
            'user_id': 1001,
            'fullName': 'John Doe',
            'dob': date(1990, 1, 1),
            'gender': 'M',
            'phone': '123-456-7890',
            'address': '123 Main St, New York, NY 10001',
            'email': 'john.doe@example.com'
        }

    def test_create_patient(self):
        """Test creating a patient"""
        patient = Patient.objects.create(**self.patient_data)
        self.assertEqual(patient.user_id, 1001)
        self.assertEqual(patient.fullName, 'John Doe')
        self.assertEqual(patient.gender, 'M')
        self.assertEqual(patient.email, 'john.doe@example.com')

    def test_patient_str_representation(self):
        """Test string representation of patient"""
        patient = Patient.objects.create(**self.patient_data)
        self.assertEqual(str(patient), 'Patient: John Doe')

    def test_patient_register_method(self):
        """Test patient register method"""
        patient = Patient.objects.create(**self.patient_data)
        old_register_date = patient.registerDate
        patient.register()
        self.assertGreaterEqual(patient.registerDate, old_register_date)

    def test_unique_user_id(self):
        """Test that user_id must be unique"""
        Patient.objects.create(**self.patient_data)

        # Try to create another patient with the same user_id
        with self.assertRaises(Exception):
            Patient.objects.create(**self.patient_data)
