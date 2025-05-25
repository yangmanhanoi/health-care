from django.contrib import admin
from .models import Patient

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'fullName', 'email', 'phone', 'gender', 'registerDate']
    list_filter = ['gender', 'registerDate']
    search_fields = ['fullName', 'email', 'phone', 'user_id']
    readonly_fields = ['registerDate']
    ordering = ['-registerDate']
