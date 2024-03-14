from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.files.storage import default_storage

import os
from .models import Patient, Provider, Department, MultiModalDataPath, Encounter
from .serializers import PatientSerializer, ProviderSerializer, DepartmentSerializer, MultiModalDataPathSerializer, EncounterSerializer
# from .serializers import GraphPatientSerializer, GraphProviderSerializer, GraphDepartmentSerializer, GraphEncounterSerializer
# from neomodel import db


# class GraphPatientViewSet(viewsets.ReadOnlyModelViewSet):
#     serializer_class = GraphPatientSerializer

#     def get_queryset(self):
#         query = "MATCH (n:GraphPatient) RETURN n"
#         results, meta = db.cypher_query(query)
#         return [dict(node[0]) for node in results]


# class GraphProviderViewSet(viewsets.ReadOnlyModelViewSet):
#     serializer_class = GraphProviderSerializer

#     def get_queryset(self):
#         query = "MATCH (n:GraphProvider) RETURN n"
#         results, meta = db.cypher_query(query)
#         return [dict(node[0]) for node in results]


# class GraphDepartmentViewSet(viewsets.ReadOnlyModelViewSet):
#     serializer_class = GraphDepartmentSerializer

#     def get_queryset(self):
#         query = "MATCH (n:GraphDepartment) RETURN n"
#         results, meta = db.cypher_query(query)
#         return [dict(node[0]) for node in results]


# class GraphEncounterViewSet(viewsets.ReadOnlyModelViewSet):
#     serializer_class = GraphEncounterSerializer

#     def get_queryset(self):
#         query = "MATCH (n:GraphEncounter) RETURN n"
#         results, meta = db.cypher_query(query)
#         return [dict(node[0]) for node in results]


# class DepartmentEncountersView(APIView):
#     def get(self, request, department_name):
#         query = """
#         MATCH (e:GraphEncounter)-[:BELONGS_TO]->(d:GraphDepartment)
#         WHERE d.name = $department_name
#         RETURN e
#         """
#         params = {'department_name': department_name}
#         results, meta = db.cypher_query(query, params)
#         encounters = [dict(node[0]) for node in results]
#         serializer = GraphEncounterSerializer(encounters, many=True)
#         return Response(serializer.data)


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class MultiModalDataPathViewSet(viewsets.ModelViewSet):
    queryset = MultiModalDataPath.objects.all()
    serializer_class = MultiModalDataPathSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        response = self.get_file_existence(instance)
        return Response(response)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        response = [self.get_file_existence(instance) for instance in queryset]
        return Response(response)

    def get_file_existence(self, instance):
        serializer = self.get_serializer(instance)
        response = serializer.data

        response['provider_view_exists'] = default_storage.exists(
            instance.provider_view.name) if instance.provider_view else False
        response['patient_view_exists'] = default_storage.exists(
            instance.patient_view.name) if instance.patient_view else False
        response['room_view_exists'] = default_storage.exists(
            instance.room_view.name) if instance.room_view else False
        response['audio_exists'] = default_storage.exists(
            instance.audio.name) if instance.audio else False
        response['transcript_exists'] = default_storage.exists(
            instance.transcript.name) if instance.transcript else False
        response['patient_survey_path_exists'] = default_storage.exists(
            instance.patient_survey_path.name) if instance.patient_survey_path else False
        response['provider_survey_path_exists'] = default_storage.exists(
            instance.provider_survey_path.name) if instance.provider_survey_path else False

        return response


class EncounterViewSet(viewsets.ModelViewSet):
    queryset = Encounter.objects.all()
    serializer_class = EncounterSerializer
