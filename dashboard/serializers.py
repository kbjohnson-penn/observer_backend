from rest_framework import serializers
from .models import Encounter, Department
import os
from django.conf import settings


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class EncounterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Encounter
        fields = ['case_id', 'department', 'visit_type',
                  'is_deidentified', 'is_restricted', 'visit_date']
