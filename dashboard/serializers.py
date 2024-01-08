from rest_framework import serializers
from .models import Encounter, Department
import os
from django.conf import settings


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class EncounterSerializer(serializers.ModelSerializer):
    audio_exists = serializers.SerializerMethodField()
    video_exists = serializers.SerializerMethodField()
    transcript_exists = serializers.SerializerMethodField()
    other_files_exists = serializers.SerializerMethodField()

    class Meta:
        model = Encounter
        fields = ['id', 'case_id', 'visit_type', 'audio_exists', 'video_exists', 'transcript_exists', 'other_files_exists', 'department']

    def get_audio_exists(self, obj):
        return os.path.isfile(os.path.join(settings.MEDIA_ROOT, obj.audio.name)) if obj.audio else False

    def get_video_exists(self, obj):
        return os.path.isfile(os.path.join(settings.MEDIA_ROOT, obj.video.name)) if obj.video else False

    def get_transcript_exists(self, obj):
        return os.path.isfile(os.path.join(settings.MEDIA_ROOT, obj.transcript.name)) if obj.transcript else False

    def get_other_files_exists(self, obj):
        return os.path.isfile(os.path.join(settings.MEDIA_ROOT, obj.other_files.name)) if obj.other_files else False

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        custom_representation = {
            'encounter_id': representation['id'],
            'case': representation['case_id'],
            'visit': representation['visit_type'],
            'department': representation['department'],
            'files': {
                'audio': representation['audio_exists'],
                'video': representation['video_exists'],
                'transcript': representation['transcript_exists'],
                'other': representation['other_files_exists'],
            }
        }
        return custom_representation