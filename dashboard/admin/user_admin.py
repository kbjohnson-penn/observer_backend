from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from ..models.profile_models import Profile
from ..forms import ProfileForm

class ProfileInline(admin.StackedInline):
    model = Profile
    form = ProfileForm
    can_delete = False
    verbose_name_plural = 'profile'
    fk_name = 'user'
    fields = ['date_of_birth', 'phone_number', 'address', 'city', 'state', 'country', 'zip_code', 'bio']

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super(UserAdmin, self).get_inline_instances(request, obj)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change and not hasattr(obj, 'profile'):
            Profile.objects.create(user=obj)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)