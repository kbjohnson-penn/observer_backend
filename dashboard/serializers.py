from rest_framework import serializers
from .models import Encounter, Department, Choice
import os
from django.conf import settings


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'name']


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']


class EncounterSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField()
    media_types = serializers.StringRelatedField(many=True)

    class Meta:
        model = Encounter
        fields = ['id', 'case_id', 'department', 'media_types', 'racial_category', 'ethnic_category', 'gender', 'age_range',
                  'is_deidentified', 'is_restricted', 'visit_date']
