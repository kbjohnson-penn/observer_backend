# Research App Test Suite

## Overview

The research app test suite provides comprehensive coverage for all OMOP-based research data models, API endpoints, serializers, and database routing functionality. Tests are organized into specialized modules for maintainability and focused testing.

## Test Summary

- **Total Tests**: 110+ tests across 5 specialized files
- **Models Tested**: 12 research models (Person, Provider, VisitOccurrence, Note, etc.)
- **API Endpoints**: Sample data API and video streaming API
- **Serializers**: All 12 model serializers with validation testing
- **ViewSets**: 4 read-only research viewsets with authentication
- **Infrastructure**: Database routing and multi-database architecture

## Test Organization

### 1. test_models.py (53 tests)
Tests for all OMOP research database models:

- **PersonModelTest**: Demographics and identifiers
- **ProviderModelTest**: Healthcare provider information
- **VisitOccurrenceModelTest**: Patient visit records with relationships
- **NoteModelTest**: Clinical notes with foreign key relationships
- **ConditionOccurrenceModelTest**: Diagnosis records
- **DrugExposureModelTest**: Medication prescriptions and exposures
- **ProcedureOccurrenceModelTest**: Medical procedures performed
- **MeasurementModelTest**: Vital signs and lab values
- **ObservationModelTest**: Additional clinical observations
- **PatientSurveyModelTest**: Patient-reported outcomes
- **ProviderSurveyModelTest**: Provider satisfaction surveys
- **AuditLogsModelTest**: System access and usage tracking

### 2. test_api_views.py (31 tests)
Tests for research API endpoints:

- **SampleDataAPITest**: CSV data processing and security
  - Authentication requirements
  - File existence and size validation
  - Path traversal protection
  - CSV parsing and type conversion
  - Unicode handling and caching
- **PublicVideoStreamAPITest**: Media file streaming
  - HEAD and GET request handling
  - Range request support for video streaming
  - Content type detection for multiple file formats
  - Path traversal and directory access protection
  - File not found and error handling

### 3. test_serializers.py (15 tests)
Tests for DRF serializers:

- **PersonSerializer**: Demographics serialization/deserialization
- **ProviderSerializer**: Provider data handling
- **VisitOccurrenceSerializer**: Visit records with foreign keys
- **NoteSerializer**: Clinical note serialization
- **ConceptSerializer**: OMOP concept dictionary
- **AuditLogsSerializer**: Read-only audit trail serialization

### 4. test_viewsets.py (8 tests)
Tests for DRF viewsets:

- **BaseResearchViewSet**: Database routing to research DB
- **PersonViewSet**: Read-only person data API
- **ProviderViewSet**: Read-only provider data API
- **VisitOccurrenceViewSet**: Visit records with select_related optimization
- **ConceptViewSet**: OMOP concept dictionary API
- Authentication requirements and read-only behavior validation

### 5. test_infrastructure.py (3 tests)
Tests for database architecture:

- **DatabaseRoutingTest**: Multi-database routing for research models
- Research model internal relationships validation
- Migration routing between databases

## Running Tests

### Full Research App Test Suite
```bash
python manage.py test research.tests --settings=observer_backend.settings.testing
```

### Individual Test Files
```bash
# Model tests
python manage.py test research.tests.test_models --settings=observer_backend.settings.testing

# API view tests
python manage.py test research.tests.test_api_views --settings=observer_backend.settings.testing

# Serializer tests
python manage.py test research.tests.test_serializers --settings=observer_backend.settings.testing

# ViewSet tests
python manage.py test research.tests.test_viewsets --settings=observer_backend.settings.testing

# Infrastructure tests
python manage.py test research.tests.test_infrastructure --settings=observer_backend.settings.testing
```

### Specific Test Classes
```bash
# Person model tests
python manage.py test research.tests.test_models.PersonModelTest --settings=observer_backend.settings.testing

# Sample data API tests
python manage.py test research.tests.test_api_views.SampleDataAPITest --settings=observer_backend.settings.testing

# Video streaming tests
python manage.py test research.tests.test_api_views.PublicVideoStreamAPITest --settings=observer_backend.settings.testing

# Person serializer tests
python manage.py test research.tests.test_serializers.PersonSerializerTest --settings=observer_backend.settings.testing

# Person viewset tests
python manage.py test research.tests.test_viewsets.ResearchViewSetAPITest.test_person_viewset_list_authenticated --settings=observer_backend.settings.testing
```

## Key Features Tested

### Multi-Database Architecture
- **Research Database**: All OMOP models route to 'research' database
- **Accounts Database**: User, Profile, Tier, Organization models
- **Cross-Database Relationships**: Proper handling of foreign keys across databases
- **Database Routing**: Automatic routing based on model app labels

### OMOP CDM Compliance
- **Person Demographics**: Year of birth, gender, race, ethnicity with concept IDs
- **Healthcare Providers**: Provider demographics and identifiers
- **Visit Occurrences**: Patient encounters with timing and type information
- **Clinical Events**: Conditions, drugs, procedures, measurements, observations
- **Survey Data**: Patient and provider reported outcomes
- **Audit Trail**: Complete access logging for compliance

### API Security and Performance
- **Authentication**: JWT token-based authentication for all endpoints
- **Path Traversal Protection**: Comprehensive security against directory traversal
- **File Size Limits**: Protection against memory exhaustion attacks
- **Caching**: Sample data endpoint caching for performance
- **Range Requests**: Video streaming with HTTP range support
- **Content Type Detection**: Proper MIME type handling for multiple file formats

### Data Processing
- **CSV Processing**: Automatic type conversion (int, float, string)
- **Unicode Handling**: Graceful handling of character encoding issues
- **Large File Handling**: Size limits and truncation for large datasets
- **Empty Value Handling**: Conversion of empty strings to None

### Read-Only Research Data
- **ViewSets**: All research viewsets are read-only (no create/update/delete)
- **Serializers**: Proper field handling with read-only audit fields
- **Database Queries**: Optimized queries with select_related for performance
- **Authentication**: Required authentication for all research data access

## Database Setup for Tests

Tests use the multi-database setup with these databases:
- `research`: OMOP research data models
- `accounts`: User authentication and profile data
- `clinical`: Clinical workflow data (separate from research)

Each test class specifies `databases = ['research', 'accounts']` to enable multi-database testing.

## Model Relationships

The research models form a comprehensive OMOP CDM structure:

```
Person ──┐
         ├── VisitOccurrence ──┐
Provider ─┘                   ├── Note
                              ├── ConditionOccurrence
                              ├── DrugExposure
                              ├── ProcedureOccurrence
                              ├── Measurement
                              ├── Observation
                              ├── PatientSurvey
                              ├── ProviderSurvey
                              └── AuditLogs

Concept (standalone dictionary for OMOP concepts)
```

## Security Considerations

### Path Traversal Protection
- File path validation in sample data and video streaming APIs
- Absolute path resolution with base directory checking
- Filename sanitization and dangerous character filtering

### Authentication Requirements
- All research data requires authenticated users
- JWT token validation for API access
- Read-only access patterns for research data integrity

### Audit Trail
- Complete access logging in AuditLogs model
- Read-only audit fields to prevent tampering
- User and workstation identification for compliance

## Performance Optimizations

### Database Queries
- `select_related()` for foreign key relationships in VisitOccurrenceViewSet
- Database routing to appropriate research database
- Proper indexing through OMOP model design

### File Handling
- File size limits to prevent memory issues
- Row limits for large CSV processing
- Caching for frequently accessed sample data

### API Response
- Paginated responses for large datasets
- HTTP range support for large media files
- Content type optimization for different file formats

This test suite ensures the research app maintains OMOP CDM compliance while providing secure, performant access to research data through well-tested APIs and database operations.