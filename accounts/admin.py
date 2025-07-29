from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Tier, Organization, Profile

# Register the custom User model
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for the custom User model."""
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    date_hierarchy = 'date_joined'
    ordering = ['-date_joined']

# Register your models here.
@admin.register(Tier)
class TierAdmin(admin.ModelAdmin):
    list_display = ['tier_name', 'level', 'complete_deidentification', 'external_access']
    list_filter = ['complete_deidentification', 'external_access', 'blur_face', 'obscure_voice']
    search_fields = ['tier_name']
    ordering = ['level']

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'state', 'country']
    list_filter = ['country', 'state']
    search_fields = ['name', 'city']
    ordering = ['name']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'organization', 'tier', 'created_at']
    list_filter = ['tier', 'organization', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    date_hierarchy = 'created_at'
    raw_id_fields = ['user']
    ordering = ['-created_at']
