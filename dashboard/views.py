from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Patient, Provider, Department, MultiModalDataPath, Encounter
from .serializers import PatientSerializer, ProviderSerializer, DepartmentSerializer, MultiModalDataPathSerializer, EncounterSerializer
from .serializers import GraphPatientSerializer, GraphProviderSerializer, GraphDepartmentSerializer, GraphEncounterSerializer
from neomodel import db


class GraphPatientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GraphPatientSerializer

    def get_queryset(self):
        query = "MATCH (n:GraphPatient) RETURN n"
        results, meta = db.cypher_query(query)
        return [dict(node[0]) for node in results]


class GraphProviderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GraphProviderSerializer

    def get_queryset(self):
        query = "MATCH (n:GraphProvider) RETURN n"
        results, meta = db.cypher_query(query)
        return [dict(node[0]) for node in results]


class GraphDepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GraphDepartmentSerializer

    def get_queryset(self):
        query = "MATCH (n:GraphDepartment) RETURN n"
        results, meta = db.cypher_query(query)
        return [dict(node[0]) for node in results]


class GraphEncounterViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GraphEncounterSerializer

    def get_queryset(self):
        query = "MATCH (n:GraphEncounter) RETURN n"
        results, meta = db.cypher_query(query)
        return [dict(node[0]) for node in results]


class DepartmentEncountersView(APIView):
    def get(self, request, department_name):
        query = """
        MATCH (e:GraphEncounter)-[:BELONGS_TO]->(d:GraphDepartment)
        WHERE d.name = $department_name
        RETURN e
        """
        params = {'department_name': department_name}
        results, meta = db.cypher_query(query, params)
        encounters = [dict(node[0]) for node in results]
        serializer = GraphEncounterSerializer(encounters, many=True)
        return Response(serializer.data)


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


class EncounterViewSet(viewsets.ModelViewSet):
    queryset = Encounter.objects.all()
    serializer_class = EncounterSerializer
