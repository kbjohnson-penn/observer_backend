# Research App Test Suite

## Overview

The research app test suite provides comprehensive coverage for the private research API implementation with tier-based access control. Tests focus on security, authentication, and proper data filtering across ViewSets.

## Current Test Summary

- **Total Tests**: 26 tests across 4 test files (plus 1 base utility file)
- **ViewSets Tested**: 3 private research ViewSets (VisitOccurrence, Person, Provider)
- **Security Testing**: Tier-based access control, authentication, authorization
- **Database Architecture**: Multi-database routing (accounts, research, clinical)
- **API Coverage**: Complete CRUD operations with proper security
- **Structure**: Modular, maintainable test files with clear separation of concerns

## Test Organization

The test suite is organized into focused, maintainable files:

### 1. **test_base.py** 
Shared utilities and base test case:
- **BaseResearchAPITestCase**: Common setup for all tests (authentication, data creation)

### 2. **test_visit_occurrence_api.py** (5 tests)
VisitOccurrence API endpoint tests:
- ✅ List authenticated access (200 OK)
- ✅ Detail authenticated access (200 OK) 
- ✅ Unauthorized list access (401)
- ✅ Unauthorized detail access (401)
- ✅ Non-existent resource (404)

### 3. **test_person_provider_api.py** (10 tests)
Person and Provider API endpoint tests:
- **PersonAPITest** (5 tests): Complete CRUD testing
- **ProviderAPITest** (5 tests): Complete CRUD testing
- Each ViewSet tested for same scenarios as VisitOccurrence

### 4. **test_tier_access_control.py** (5 tests)
Comprehensive multi-tier security scenarios:
- **TierBasedAccessControlTest**: Multi-user, multi-tier data filtering
  - Tier 1 users see only Tier 1 data
  - Tier 2 users see Tier 1 & 2 data (hierarchical access)
  - Tier 3 users see all tier data
  - Lower tier users get 404 for higher tier data
  - Higher tier users can access lower tier data

### 5. **test_edge_cases.py** (6 tests)
Edge cases and administrative access:
- **EmptyResultsTest** (3 tests): Returns empty arrays when users have no accessible data
- **SuperuserAccessTest** (3 tests): Superusers bypass all tier restrictions

## Running Tests

### Full Private API Test Suite
```bash
# Run all 26 private API tests across all test files
python manage.py test research.tests.test_visit_occurrence_api research.tests.test_person_provider_api research.tests.test_tier_access_control research.tests.test_edge_cases

# Or run all research tests
python manage.py test research.tests
```

### Individual Test Files
```bash
# Basic VisitOccurrence tests (5 tests)
python manage.py test research.tests.test_visit_occurrence_api

# Person and Provider tests (10 tests)
python manage.py test research.tests.test_person_provider_api

# Tier-based access control (5 tests)
python manage.py test research.tests.test_tier_access_control

# Edge cases and admin access (6 tests)
python manage.py test research.tests.test_edge_cases
```

### Specific Test Classes
```bash
# Person API tests (5 tests)
python manage.py test research.tests.test_person_provider_api.PersonAPITest

# Provider API tests (5 tests)
python manage.py test research.tests.test_person_provider_api.ProviderAPITest

# Tier access control (5 tests)
python manage.py test research.tests.test_tier_access_control.TierBasedAccessControlTest

# Empty results (3 tests)
python manage.py test research.tests.test_edge_cases.EmptyResultsTest

# Superuser access (3 tests)
python manage.py test research.tests.test_edge_cases.SuperuserAccessTest
```

### Individual Test Methods
```bash
# Test tier 1 user restrictions
python manage.py test research.tests.test_tier_access_control.TierBasedAccessControlTest.test_tier1_user_access

# Test unauthorized access handling
python manage.py test research.tests.test_person_provider_api.PersonAPITest.test_get_persons_unauthorized

# Test empty results
python manage.py test research.tests.test_edge_cases.EmptyResultsTest.test_empty_visits_list
```

## Key Features Tested

### ViewSets & URL Configuration
- **VisitOccurrenceViewSet**: `/api/v1/private/visits/` - Direct tier-based filtering
- **PersonViewSet**: `/api/v1/private/persons/` - Relationship-based filtering via visits
- **ProviderViewSet**: `/api/v1/private/research-providers/` - Relationship-based filtering via visits
- **Conflict Resolution**: Research providers use separate URL to avoid clinical app conflicts

### Tier-Based Security Model
- **Hierarchical Access**: Higher tier users can access lower tier data
- **Data Isolation**: Lower tier users cannot access higher tier data
- **Superuser Override**: Superusers bypass all tier restrictions
- **404 for Unauthorized**: Returns 404 (not 403) to avoid information leakage
- **Relationship Filtering**: Person/Provider access controlled via accessible VisitOccurrences

### Authentication & Authorization  
- **JWT Authentication**: Bearer token required for all private endpoints
- **401 for Unauthenticated**: Proper HTTP status codes for missing tokens
- **Profile Integration**: User tier access determined by profile.tier.level
- **Multi-Database Security**: Tier filtering works across database boundaries

### Database Architecture
- **Multi-Database Support**: Tests use 'accounts', 'research', 'clinical' databases
- **Proper Routing**: Uses `.using('research')` for research data queries
- **Cross-Database Relations**: VisitOccurrence.tier_id references accounts.Tier.id
- **Relationship Integrity**: Person ↔ VisitOccurrence ↔ Provider relationships maintained

## Implementation Pattern for New Models

To extend the research API with new models, follow this proven pattern:

### 1. Create ViewSet
```python
# research/api/viewsets/private/new_model_viewset.py
class NewModelViewSet(BaseAuthenticatedViewSet):
    serializer_class = NewModelSerializer
    
    def get_queryset(self):
        # Choose filtering strategy based on model:
        
        # Option A: Direct tier filtering (if model has tier_id field)
        return filter_queryset_by_user_tier(
            NewModel.objects.using('research').all(),
            self.request.user,
            related_field='tier_id'
        )
        
        # Option B: Relationship-based filtering (via visits)
        accessible_visits = filter_queryset_by_user_tier(
            VisitOccurrence.objects.using('research').all(),
            self.request.user,
            related_field='tier_id'
        )
        return NewModel.objects.using('research').filter(
            visit_occurrence__in=accessible_visits
        ).distinct()

    def get_object(self):
        queryset = self.get_queryset()
        try:
            obj = queryset.get(pk=self.kwargs['pk'])
            self.check_object_permissions(self.request, obj)
            return obj
        except NewModel.DoesNotExist:
            raise Http404
```

### 2. Register URL
```python
# research/api/urls/private_urls.py  
router.register(r'new-models', NewModelViewSet, basename='v1-research-newmodel')
```

### 3. Create Tests
Copy the test structure from the existing test files, adjusting for your model's specific relationships.

## Current Data Model

The implemented ViewSets work with this structure:

```
Person ──┐
         ├── VisitOccurrence (has tier_id)
Provider ─┘

- VisitOccurrence: Direct tier filtering on tier_id field
- Person/Provider: Indirect filtering via accessible VisitOccurrences  
```

## Database Configuration

Tests require this multi-database setup:

```python
databases = ['accounts', 'research', 'clinical']
```

- **accounts**: User, Profile, Tier, Organization
- **research**: Person, Provider, VisitOccurrence  
- **clinical**: Separate clinical workflow data

## Best Practices

1. **Always use tier filtering** - Never expose unfiltered research data
2. **Test all scenarios** - Authentication, authorization, empty results, cross-tier access
3. **Use consistent patterns** - Follow the established ViewSet structure  
4. **Handle Profile creation** - Check for auto-created profiles in tests
5. **Return 404 for unauthorized** - Avoid information leakage with 403s
6. **Use `.distinct()`** - For relationship-based filtering to avoid duplicates
7. **Specify database routing** - Always use `.using('research')` for research queries

This test suite provides a solid foundation for secure, tier-based research data access in the Observer platform.