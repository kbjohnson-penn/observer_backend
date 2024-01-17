from django.contrib import admin
from .models import Department, Encounter, Choice

admin.site.register(Choice)
admin.site.register(Department)
admin.site.register(Encounter)
