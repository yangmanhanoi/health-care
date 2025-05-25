# pharmacy/models.py

from django.db import models

class Pharmacy(models.Model):
    name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=50)
    address = models.TextField()

    def __str__(self):
        return self.name


class Pharmacist(models.Model):
    name = models.CharField(max_length=255)
    license_number = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Medicine(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    quantity = models.IntegerField()
    price = models.FloatField()
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def add_stock(self, amount):
        self.quantity += amount
        self.save()

    def reduce_stock(self, amount):
        if self.quantity >= amount:
            self.quantity -= amount
            self.save()
        else:
            raise ValueError("Insufficient stock")


class DispenseRecord(models.Model):
    prescription_id = models.IntegerField()
    pharmacist = models.ForeignKey(Pharmacist, on_delete=models.CASCADE)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dispense #{self.id}"


class DispenseItem(models.Model):
    dispense_record = models.ForeignKey(DispenseRecord, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()

    def __str__(self):
        return f"{self.quantity} x {self.medicine.name}"
