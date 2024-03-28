from django.contrib import admin
from .models import Patient, Provider, Department, MultiModalDataPath, Encounter, RIAS

admin.site.register(Patient)
admin.site.register(Provider)
admin.site.register(Department)
admin.site.register(MultiModalDataPath)
admin.site.register(Encounter)
admin.site.register(RIAS)
