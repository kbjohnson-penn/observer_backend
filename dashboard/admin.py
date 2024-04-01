from django.contrib import admin
from .models import Patient, Provider, EncounterSource, Department, MultiModalDataPath, Encounter

admin.site.register(Patient)
admin.site.register(Provider)
admin.site.register(EncounterSource)
admin.site.register(Department)
admin.site.register(MultiModalDataPath)
admin.site.register(Encounter)
