from django.db import models

class LabTestOrderStatus(models.TextChoices):
    ORDERED = 'ORDERED', 'Ordered'
    SAMPLE_COLLECTED = 'SAMPLE_COLLECTED', 'Sample Collected'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    COMPLETED = 'COMPLETED', 'Completed'
    CANCELLED = 'CANCELLED', 'Cancelled'

class TestType(models.Model):
    """
    Model representing a type of laboratory test that can be performed
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, blank=True, null=True)  # e.g., "mg/dL", "%"
    normal_range = models.CharField(max_length=100, blank=True, null=True)  # e.g., "70-100"
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class LabTestOrder(models.Model):
    """
    Model representing a laboratory test order for a patient
    """
    patient_id = models.IntegerField()
    doctor_id = models.IntegerField()
    appointment_id = models.IntegerField(blank=True, null=True)  # Link to appointment
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=LabTestOrderStatus.choices,
        default=LabTestOrderStatus.ORDERED
    )
    clinical_notes = models.TextField(blank=True, null=True)
    urgency = models.CharField(max_length=20, blank=True, null=True)  # e.g., 'routine', 'urgent'
    collection_date = models.DateTimeField(blank=True, null=True)
    completion_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Lab Order {self.id} for Patient {self.patient_id} by Doctor {self.doctor_id}"

class LabTestOrderItem(models.Model):
    """
    Model representing an individual test within a lab test order
    """
    order = models.ForeignKey(
        LabTestOrder,
        on_delete=models.CASCADE,
        related_name='items'
    )
    test_type = models.ForeignKey(
        TestType,
        on_delete=models.PROTECT,
        related_name='order_items'
    )
    status = models.CharField(
        max_length=20,
        choices=LabTestOrderStatus.choices,
        default=LabTestOrderStatus.ORDERED
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def price(self):
        """Return the price of the test type"""
        return self.test_type.cost

    def __str__(self):
        return f"{self.test_type.name} for Order {self.order.id}"

class TestResult(models.Model):
    """
    Model representing the result of a specific test
    """
    order_item = models.OneToOneField(
        LabTestOrderItem,
        on_delete=models.CASCADE,
        related_name='result'
    )
    result_value = models.CharField(max_length=255)
    normal_range = models.CharField(max_length=100, blank=True, null=True)
    unit = models.CharField(max_length=50, blank=True, null=True)
    technician_notes = models.TextField(blank=True, null=True)
    result_date = models.DateTimeField(auto_now_add=True)
    verified_by = models.IntegerField(blank=True, null=True)  # User ID of the technician
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Result for {self.order_item.test_type.name} - {self.result_value} {self.unit}"
