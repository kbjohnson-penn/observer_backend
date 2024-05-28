from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from itertools import chain

from neomodel import db

from .models import Patient, Provider, EncounterSource, Department, MultiModalDataPath, Encounter, EncounterSimCenter, EncounterRIAS
from .serializers import PatientSerializer, ProviderSerializer, EncounterSourceSerializer, DepartmentSerializer, MultiModalDataPathSerializer, EncounterSerializer, EncounterSimCenterSerializer, EncounterRIASSerializer

from .serializers import GraphSerializer


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [ReadOnly]


class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [ReadOnly]


class EncounterSourceViewSet(viewsets.ModelViewSet):
    queryset = EncounterSource.objects.all()
    serializer_class = EncounterSourceSerializer
    permission_classes = [ReadOnly]


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [ReadOnly]


class MultiModalDataPathViewSet(viewsets.ModelViewSet):
    queryset = MultiModalDataPath.objects.all()
    serializer_class = MultiModalDataPathSerializer
    permission_classes = [ReadOnly]


class EncounterViewSet(viewsets.ModelViewSet):
    queryset = Encounter.objects.all()
    serializer_class = EncounterSerializer
    permission_classes = [ReadOnly]


class EncounterSimCenterViewSet(viewsets.ModelViewSet):
    queryset = EncounterSimCenter.objects.all()
    serializer_class = EncounterSimCenterSerializer
    permission_classes = [ReadOnly]


class EncounterRIASViewSet(viewsets.ModelViewSet):
    queryset = EncounterRIAS.objects.all()
    serializer_class = EncounterRIASSerializer
    permission_classes = [ReadOnly]


class GetKnowledgeGraph(APIView):
    def get(self, request):
        query = """
        MATCH (n)-[r]->(m)
        RETURN n, r, m
        """
        results, _ = db.cypher_query(query)

        nodes = set()
        edges = []

        for n, r, m in results:
            nodes.add(n)
            nodes.add(m)
            edges.append(r)

        # Prepare data for serialization
        nodes_data = [{'id': node.id, 'labels': list(
            node.labels), 'properties': node._properties} for node in nodes]
        edges_data = [{'source': rel.start_node.id, 'target': rel.end_node.id,
                       'type': rel.type, 'properties': rel._properties} for rel in edges]

        # Create an instance of GraphSerializer with the data
        graph_data = {'nodes': nodes_data, 'edges': edges_data}
        serializer = GraphSerializer(data=graph_data)

        # Call is_valid() before accessing .data
        if serializer.is_valid():
            # Return a Response with the serialized data
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)
