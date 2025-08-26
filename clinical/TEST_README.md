# Clinical App Tests

## Test Summary

- **Total Tests**: 91
- **Coverage**: Models, Business Logic, Database Routing

## What We Test

### Models (91 tests)

- **Patient (12 tests)**: String representation, simcenter ID ranges, choice validation, CRUD operations
- **Provider (10 tests)**: Provider ID validation, data persistence, timestamp behavior
- **EncounterSource (9 tests)**: Unique constraints, name validation, manager methods  
- **Department (12 tests)**: Basic CRUD, field validation, meta attributes
- **MultiModalData (13 tests)**: Boolean workflows, defaults, verbose names
- **Encounter (19 tests)**: Business logic integration, EncounterService, tier access control, auto-relationships
- **EncounterFile (16 tests)**: String representations, unique constraints, cascade deletes, file types

## Running Tests

```bash
# All clinical model tests
python manage.py test clinical.tests.PatientModelTest clinical.tests.ProviderModelTest clinical.tests.EncounterSourceModelTest clinical.tests.DepartmentModelTest clinical.tests.MultiModalDataModelTest clinical.tests.EncounterModelTest clinical.tests.EncounterFileModelTest

# Specific test
python manage.py test clinical.tests.EncounterModelTest -v 2
```

## Key Features Tested

### Business Logic Integration
- **EncounterService**: Auto-creates MultiModalData and EncounterSource for all encounters
- **Simcenter Logic**: Auto-creates Patient/Provider objects for simcenter encounters  
- **Case ID Generation**: `{provider}_{patient}_{date}` format

### Database Architecture
- **Multi-database routing**: Clinical models use `_using='clinical'`
- **Cross-database references**: Tier integration with accounts database
- **Constraint validation**: Unique constraints and foreign key relationships

### Data Validation
- **Choice constants**: Uses shared.choices instead of hardcoded values
- **String representations**: All model `__str__` methods tested
- **Field validation**: Type checking, constraint enforcement

## Database Setup

- Uses `default`, `accounts`, and `clinical` databases
- Proper database routing with explicit `_using` parameters
- Tier integration: "Tier 1" (level=1, lowest) to "Tier 5" (level=5, highest)

## Critical Business Logic

### Encounter Creation Process
1. EncounterService.prepare_encounter_for_save() runs automatically
2. Creates EncounterSource if missing
3. Creates MultiModalData for all encounters  
4. For simcenter: auto-creates Patient/Provider if needed
5. Generates case_id based on provider_patient_date pattern

### File Management
- **Unique constraint**: encounter + file_path combination must be unique
- **Cascade delete**: files deleted when encounter is deleted
- **Related access**: `encounter.files.all()` returns associated files
- **File types**: video, audio, transcript, annotation support

## Next Steps

The following components remain to be tested:
- API endpoints and authentication
- Azure storage integration  
- Additional infrastructure tests