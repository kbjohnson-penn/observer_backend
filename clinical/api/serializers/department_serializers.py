from rest_framework import serializers

from clinical.models import Department, EncounterSource


class EncounterSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EncounterSource
        fields = "__all__"


class PublicEncounterSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EncounterSource
        fields = ["name"]


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class PublicDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["name"]
