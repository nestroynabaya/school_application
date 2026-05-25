from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, School, Application, Payment

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'is_active']
    list_filter = ['role']
    fieldsets = UserAdmin.fieldsets + (
        ('Role & Contact', {'fields': ('role', 'phone')}),
    )

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'city', 'status', 'is_featured', 'application_fee']
    list_filter = ['category', 'status']
    search_fields = ['name', 'city']
    list_editable = ['status', 'is_featured']

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'school', 'student', 'status', 'submitted_at']
    list_filter = ['status']
    search_fields = ['full_name', 'school__name']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['student', 'school', 'amount', 'payment_method', 'status', 'paid_at']
    list_filter = ['status', 'payment_method']
