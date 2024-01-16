from rest_framework import serializers
from .models import Encounter, Department
import os
from django.conf import settings


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']


class EncounterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Encounter
        fields = ['id', 'case_id', 'department', 'visit_type', 'racial_category', 'ethnic_category', 'gender', 'age_range',
                  'is_deidentified', 'is_restricted', 'visit_date']
