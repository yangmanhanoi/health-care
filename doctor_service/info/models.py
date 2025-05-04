from django.db import models

# Create your models here.
class Doctor(models.Model):
    user_id = models.IntegerField(unique=True)  # user_id từ auth_service
    full_name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    contact = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.specialty})"

