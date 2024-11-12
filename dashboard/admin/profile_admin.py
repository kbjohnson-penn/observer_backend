from django.contrib import admin
from ..models.profile_models import Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth', 'phone_number', 'city', 'state', 'country')
    search_fields = ('user__username', 'user__email', 'phone_number', 'city', 'state', 'country')

# admin.site.register(Profile, ProfileAdmin)