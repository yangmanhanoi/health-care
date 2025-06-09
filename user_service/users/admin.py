from django.contrib import admin
from .models import User, UserActivity


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'email', 'user_type', 'is_active', 
        'is_verified', 'created_at'
    ]
    list_filter = [
        'user_type', 'is_active', 'is_verified', 'gender', 
        'created_at', 'country'
    ]
    search_fields = [
        'first_name', 'last_name', 'email', 'phone'
    ]
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at', 'full_name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'auth_user_id', 'user_type', 'first_name', 
                      'last_name', 'full_name', 'email')
        }),
        ('Personal Information', {
            'fields': ('date_of_birth', 'gender', 'phone', 'profile_picture', 'bio')
        }),
        ('Address Information', {
            'fields': ('address_line_1', 'address_line_2', 'city', 
                      'state', 'postal_code', 'country')
        }),
        ('System Information', {
            'fields': ('is_active', 'is_verified', 'created_at', 
                      'updated_at', 'last_login')
        }),
    )


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'activity_type', 'ip_address', 'timestamp'
    ]
    list_filter = ['activity_type', 'timestamp']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'description']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp']
