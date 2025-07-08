from django.core.management.base import BaseCommand
from model_bakery import baker
from dashboard.choices import *
from dashboard.models import Profile, Tier, Organization
from dashboard.constants import (
    SIMCENTER_PATIENT_ID_LOWER_LIMIT, 
    SIMCENTER_PATIENT_ID_UPPER_LIMIT,
    SIMCENTER_PROVIDER_ID_LOWER_LIMIT,
    SIMCENTER_PROVIDER_ID_UPPER_LIMIT
)
import random
import os
from faker import Faker


class Command(BaseCommand):
    help = 'Generates realistic mock data for the Observer healthcare platform'

    def add_arguments(self, parser):
        parser.add_argument('--seed', type=int, help='Random seed for reproducibility (default from env or 42)')
        parser.add_argument('--clinic-patients', type=int, help='Number of clinic patients to generate (default from env or 200)')
        parser.add_argument('--clinic-providers', type=int, help='Number of clinic providers to generate (default from env or 200)')
        parser.add_argument('--simcenter-patients', type=int, help='Number of SimCenter patients to generate (default from env or 50)')
        parser.add_argument('--simcenter-providers', type=int, help='Number of SimCenter providers to generate (default from env or 30)')
        parser.add_argument('--clinic-encounters', type=int, help='Number of clinic encounters to generate (default from env or 150)')
        parser.add_argument('--simcenter-encounters', type=int, help='Number of SimCenter encounters to generate (default from env or 50)')
        parser.add_argument('--clear-existing', action='store_true', help='Clear existing data before generating new data (default from env or False)')
        parser.add_argument('--use-env', action='store_true', help='Use environment variables for configuration (default behavior)')

    def handle(self, *args, **options):
        # Get configuration from environment variables or command line arguments
        def get_env_bool(key, default=False):
            return os.getenv(key, str(default)).lower() in ('true', '1', 'yes', 'on')
        
        def get_env_int(key, default):
            try:
                return int(os.getenv(key, default))
            except ValueError:
                return default

        # Use environment variables as defaults, override with command line if provided
        seed = options.get('seed') or get_env_int('MOCK_DATA_SEED', 42)
        clinic_patients_count = options.get('clinic_patients') or get_env_int('MOCK_DATA_CLINIC_PATIENTS', 200)
        clinic_providers_count = options.get('clinic_providers') or get_env_int('MOCK_DATA_CLINIC_PROVIDERS', 200)
        simcenter_patients_count = options.get('simcenter_patients') or get_env_int('MOCK_DATA_SIMCENTER_PATIENTS', 50)
        simcenter_providers_count = options.get('simcenter_providers') or get_env_int('MOCK_DATA_SIMCENTER_PROVIDERS', 30)
        clinic_encounters_count = options.get('clinic_encounters') or get_env_int('MOCK_DATA_CLINIC_ENCOUNTERS', 150)
        simcenter_encounters_count = options.get('simcenter_encounters') or get_env_int('MOCK_DATA_SIMCENTER_ENCOUNTERS', 50)
        clear_existing = options.get('clear_existing') or get_env_bool('MOCK_DATA_CLEAR_EXISTING', False)
        
        random.seed(seed)
        Faker.seed(seed)
        fake = Faker()

        self.stdout.write(self.style.SUCCESS('Starting Observer Mock Data Generation'))
        self.stdout.write(f'Seed: {seed}')
        self.stdout.write(f'Clinic Patients: {clinic_patients_count}, Providers: {clinic_providers_count}')
        self.stdout.write(f'SimCenter Patients: {simcenter_patients_count}, Providers: {simcenter_providers_count}')
        self.stdout.write(f'Encounters - Clinic: {clinic_encounters_count}, SimCenter: {simcenter_encounters_count}')
        
        # Clear existing data if requested
        if clear_existing:
            self._clear_existing_data()

        # Department configuration
        DEPARTMENTS = [
            "Cardiology", "Family Medicine", "Internal Medicine", 
            "Neurology", "Penn Sim-Center"
        ]

        try:
            # Generate core data
            tiers = self._generate_tiers()
            self._generate_departments(DEPARTMENTS)
            self._generate_encounter_sources()
            
            # Generate patients and providers
            clinic_patients = self._generate_clinic_patients(clinic_patients_count, fake)
            simcenter_patients = self._generate_simcenter_patients(simcenter_patients_count, fake)
            
            clinic_providers = self._generate_clinic_providers(clinic_providers_count, fake)
            simcenter_providers = self._generate_simcenter_providers(simcenter_providers_count, fake)
            
            # Generate encounters and files together to ensure consistency
            clinic_encounters, clinic_files = self._generate_clinic_encounters_with_files(
                clinic_encounters_count, clinic_patients, clinic_providers, tiers, fake
            )
            simcenter_encounters, simcenter_files = self._generate_simcenter_encounters_with_files(
                simcenter_encounters_count, simcenter_patients, simcenter_providers, tiers, fake
            )
            
            all_encounters = clinic_encounters + simcenter_encounters
            encounter_files = clinic_files + simcenter_files
            
            # Summary
            self._print_summary(
                clinic_patients, simcenter_patients, clinic_providers, simcenter_providers,
                clinic_encounters, simcenter_encounters, encounter_files, tiers
            )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error generating mock data: {str(e)}'))
            raise

    def _clear_existing_data(self):
        """Clear all existing data from the database"""
        from dashboard.models import (
            Encounter, EncounterFile, MultiModalData, Patient, Provider,
            Department, EncounterSource, Tier, Organization, Profile
        )
        
        self.stdout.write('Clearing existing data...')
        models_to_clear = [
            Encounter, EncounterFile, MultiModalData, Patient, Provider,
            Department, EncounterSource, Tier, Organization, Profile
        ]
        
        for model in models_to_clear:
            count = model.objects.count()
            if count > 0:
                model.objects.all().delete()
                self.stdout.write(f'  Deleted {count} {model.__name__} records')
        
        self.stdout.write(self.style.SUCCESS('Data cleared successfully'))

    def _generate_tiers(self):
        """Generate access control tiers"""
        tier_configs = [
            {"tier_name": "Level1", "level": 1, "complete_deidentification": False, "blur_sexually_explicit_body_parts": False, "blur_face": False, "obscure_voice": False, "dua": False, "external_access": False},
            {"tier_name": "Level2", "level": 2, "complete_deidentification": True, "blur_sexually_explicit_body_parts": False, "blur_face": False, "obscure_voice": False, "dua": False, "external_access": False},
            {"tier_name": "Level3", "level": 3, "complete_deidentification": True, "blur_sexually_explicit_body_parts": True, "blur_face": False, "obscure_voice": False, "dua": True, "external_access": False},
            {"tier_name": "Level4", "level": 4, "complete_deidentification": True, "blur_sexually_explicit_body_parts": True, "blur_face": True, "obscure_voice": False, "dua": True, "external_access": True},
            {"tier_name": "Level5", "level": 5, "complete_deidentification": True, "blur_sexually_explicit_body_parts": True, "blur_face": True, "obscure_voice": True, "dua": True, "external_access": True},
        ]
        
        tiers = []
        for tier_config in tier_configs:
            tier = baker.make("Tier", **tier_config)
            tiers.append(tier)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(tiers)} access control tiers'))
        return tiers

    def _generate_departments(self, departments):
        """Generate department records"""
        for dept_name in departments:
            baker.make("Department", name=dept_name)
        self.stdout.write(self.style.SUCCESS(f'Created {len(departments)} departments'))

    def _generate_encounter_sources(self):
        """Generate encounter source records"""
        sources = ["Clinic", "Simcenter"]
        for source_name in sources:
            baker.make("EncounterSource", name=source_name)
        self.stdout.write(self.style.SUCCESS(f'Created {len(sources)} encounter sources'))

    def _generate_clinic_patients(self, count, fake):
        """Generate clinic patients with IDs 1-count"""
        patients = []
        for patient_id in range(1, count + 1):
            patient = baker.make(
                "Patient",
                patient_id=patient_id,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                date_of_birth=fake.date_between(start_date='-80y', end_date='-18y'),
                sex=random.choice([choice[0] for choice in SEX_CATEGORIES]),
                race=random.choice([choice[0] for choice in RACIAL_CATEGORIES]),
                ethnicity=random.choice([choice[0] for choice in ETHNIC_CATEGORIES])
            )
            patients.append(patient)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(patients)} clinic patients'))
        return patients

    def _generate_simcenter_patients(self, count, fake):
        """Generate SimCenter patients with IDs from constants range"""
        patient_ids = random.sample(
            range(SIMCENTER_PATIENT_ID_LOWER_LIMIT, SIMCENTER_PATIENT_ID_UPPER_LIMIT), count
        )
        patients = []
        for patient_id in patient_ids:
            patient = baker.make(
                "Patient",
                patient_id=patient_id,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                date_of_birth=fake.date_between(start_date='-80y', end_date='-18y'),
                sex=random.choice([choice[0] for choice in SEX_CATEGORIES]),
                race=random.choice([choice[0] for choice in RACIAL_CATEGORIES]),
                ethnicity=random.choice([choice[0] for choice in ETHNIC_CATEGORIES])
            )
            patients.append(patient)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(patients)} SimCenter patients'))
        return patients

    def _generate_clinic_providers(self, count, fake):
        """Generate clinic providers with IDs 1-count"""
        providers = []
        for provider_id in range(1, count + 1):
            provider = baker.make(
                "Provider",
                provider_id=provider_id,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                date_of_birth=fake.date_between(start_date='-65y', end_date='-25y'),
                sex=random.choice([choice[0] for choice in SEX_CATEGORIES]),
                race=random.choice([choice[0] for choice in RACIAL_CATEGORIES]),
                ethnicity=random.choice([choice[0] for choice in ETHNIC_CATEGORIES])
            )
            providers.append(provider)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(providers)} clinic providers'))
        return providers

    def _generate_simcenter_providers(self, count, fake):
        """Generate SimCenter providers with IDs from constants range"""
        provider_ids = random.sample(
            range(SIMCENTER_PROVIDER_ID_LOWER_LIMIT, SIMCENTER_PROVIDER_ID_UPPER_LIMIT), count
        )
        providers = []
        for provider_id in provider_ids:
            provider = baker.make(
                "Provider",
                provider_id=provider_id,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                date_of_birth=fake.date_between(start_date='-65y', end_date='-25y'),
                sex=random.choice([choice[0] for choice in SEX_CATEGORIES]),
                race=random.choice([choice[0] for choice in RACIAL_CATEGORIES]),
                ethnicity=random.choice([choice[0] for choice in ETHNIC_CATEGORIES])
            )
            providers.append(provider)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(providers)} SimCenter providers'))
        return providers

    def _generate_clinic_encounters_with_files(self, count, patients, providers, tiers, fake):
        """Generate clinic encounters with matching files and multimodal data"""
        from dashboard.models import Department, EncounterSource
        
        clinic_source = EncounterSource.objects.get(name="clinic")
        clinic_departments = Department.objects.exclude(name="Penn Sim-Center")
        
        encounters = []
        encounter_files = []
        used_csn = set()
        
        # Available file types
        file_types = [
            'room_view', 'provider_view', 'patient_view', 'audio', 'transcript',
            'patient_survey', 'provider_survey', 'patient_annotation',
            'provider_annotation', 'rias_transcript', 'rias_codes', 'other'
        ]
        
        file_extensions = {
            'room_view': 'mp4', 'provider_view': 'mp4', 'patient_view': 'mp4',
            'audio': 'wav', 'transcript': 'txt', 'patient_survey': 'json',
            'provider_survey': 'json', 'patient_annotation': 'json',
            'provider_annotation': 'json', 'rias_transcript': 'txt',
            'rias_codes': 'json', 'other': 'pdf'
        }
        
        for i in range(count):
            # Generate unique CSN
            while True:
                csn = str(random.randint(1000000, 9999999))
                if csn not in used_csn:
                    used_csn.add(csn)
                    break
            
            # Clinic encounters have more files (3-6 files per encounter)
            num_files = random.randint(3, 6)
            selected_file_types = random.sample(file_types, min(num_files, len(file_types)))
            
            # Create multimodal data based on selected files
            multimodal_data_fields = {}
            for file_type in selected_file_types:
                if file_type in ['provider_view', 'patient_view', 'room_view', 'audio', 'transcript',
                               'patient_survey', 'provider_survey', 'patient_annotation',
                               'provider_annotation', 'rias_transcript', 'rias_codes']:
                    multimodal_data_fields[file_type] = True
            
            # Create multimodal data only if we have relevant files
            multimodal_data = None
            if multimodal_data_fields:
                # Set all fields to False first, then set selected ones to True
                all_fields = {field: False for field in [
                    'provider_view', 'patient_view', 'room_view', 'audio', 'transcript',
                    'patient_survey', 'provider_survey', 'patient_annotation',
                    'provider_annotation', 'rias_transcript', 'rias_codes'
                ]}
                all_fields.update(multimodal_data_fields)
                multimodal_data = baker.make("MultiModalData", **all_fields)
            
            # Create encounter
            encounter = baker.make(
                "Encounter",
                csn_number=csn,
                case_id=f"CLINIC_{i+1:03d}",
                encounter_source=clinic_source,
                department=random.choice(clinic_departments),
                provider=random.choice(providers[:min(50, len(providers))]),
                patient=random.choice(patients),
                provider_satisfaction=random.randint(0, 5),
                patient_satisfaction=random.randint(0, 5),
                type="clinic",
                is_deidentified=random.choice([True, False]),
                is_restricted=random.choice([True, False]),
                encounter_date_and_time=fake.date_time_between(start_date='-1y', end_date='now'),
                tier=random.choice(tiers),
                multi_modal_data=multimodal_data
            )
            encounters.append(encounter)
            
            # Create matching encounter files
            for file_type in selected_file_types:
                file_ext = file_extensions.get(file_type, 'dat')
                encounter_date = encounter.encounter_date_and_time
                date_str = encounter_date.strftime("%m.%d.%Y")
                
                provider_id = encounter.provider.provider_id if encounter.provider else random.randint(1, 200)
                patient_id = encounter.patient.patient_id if encounter.patient else random.randint(1, 200)
                
                suffix = random.choice(["", "_trimmed", "_processed", f"_{random.randint(1, 99):02d}"])
                file_name = f"PR{provider_id}_PT{patient_id}_{date_str}_{file_type}{suffix}.{file_ext}"
                folder_name = f"PR{provider_id}_PT{patient_id}_{date_str}"
                azure_path = f"Clinic/{folder_name}/{file_type}/{file_name}"
                
                encounter_file = baker.make(
                    "EncounterFile",
                    encounter=encounter,
                    file_type=file_type,
                    file_name=file_name,
                    file_path=azure_path
                )
                encounter_files.append(encounter_file)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(encounters)} clinic encounters with {len(encounter_files)} files'))
        return encounters, encounter_files

    def _generate_simcenter_encounters_with_files(self, count, patients, providers, tiers, fake):
        """Generate SimCenter encounters with matching files and multimodal data"""
        from dashboard.models import Department, EncounterSource
        
        simcenter_source = EncounterSource.objects.get(name="simcenter")
        simcenter_dept = Department.objects.get(name="Penn Sim-Center")
        
        encounters = []
        encounter_files = []
        used_csn = set()
        
        # Available file types
        file_types = [
            'room_view', 'provider_view', 'patient_view', 'audio', 'transcript',
            'patient_survey', 'provider_survey', 'patient_annotation',
            'provider_annotation', 'rias_transcript', 'rias_codes', 'other'
        ]
        
        file_extensions = {
            'room_view': 'mp4', 'provider_view': 'mp4', 'patient_view': 'mp4',
            'audio': 'wav', 'transcript': 'txt', 'patient_survey': 'json',
            'provider_survey': 'json', 'patient_annotation': 'json',
            'provider_annotation': 'json', 'rias_transcript': 'txt',
            'rias_codes': 'json', 'other': 'pdf'
        }
        
        for i in range(count):
            # Generate unique CSN
            while True:
                csn = str(random.randint(1000000, 9999999))
                if csn not in used_csn:
                    used_csn.add(csn)
                    break
            
            # SimCenter has fewer files (1-2 files per encounter)
            num_files = random.randint(1, 2)
            selected_file_types = random.sample(file_types, min(num_files, len(file_types)))
            
            # Create multimodal data based on selected files
            multimodal_data_fields = {}
            for file_type in selected_file_types:
                if file_type in ['provider_view', 'patient_view', 'room_view', 'audio', 'transcript',
                               'patient_survey', 'provider_survey', 'patient_annotation',
                               'provider_annotation', 'rias_transcript', 'rias_codes']:
                    multimodal_data_fields[file_type] = True
            
            # Create multimodal data only if we have relevant files
            multimodal_data = None
            if multimodal_data_fields:
                # Set all fields to False first, then set selected ones to True
                all_fields = {field: False for field in [
                    'provider_view', 'patient_view', 'room_view', 'audio', 'transcript',
                    'patient_survey', 'provider_survey', 'patient_annotation',
                    'provider_annotation', 'rias_transcript', 'rias_codes'
                ]}
                all_fields.update(multimodal_data_fields)
                multimodal_data = baker.make("MultiModalData", **all_fields)
            
            # Create encounter
            encounter = baker.make(
                "Encounter",
                csn_number=csn,
                case_id=f"SIMCENTER_{i+1:03d}",
                encounter_source=simcenter_source,
                department=simcenter_dept,
                provider=random.choice(providers),
                patient=random.choice(patients),
                provider_satisfaction=random.randint(0, 5),
                patient_satisfaction=random.randint(0, 5),
                type="simcenter",
                is_deidentified=random.choice([True, False]),
                is_restricted=random.choice([True, False]),
                encounter_date_and_time=fake.date_time_between(start_date='-6m', end_date='now'),
                tier=random.choice(tiers),
                multi_modal_data=multimodal_data
            )
            encounters.append(encounter)
            
            # Create matching encounter files
            for file_type in selected_file_types:
                file_ext = file_extensions.get(file_type, 'dat')
                encounter_date = encounter.encounter_date_and_time
                
                specialties = ["Obgyn", "Cardio", "Neuro", "Peds", "Surgery", "Internal"]
                last_names = ["Perez", "Johnson", "Smith", "Davis", "Wilson", "Brown", "Taylor", "Anderson"]
                
                specialty = random.choice(specialties)
                last_name = random.choice(last_names)
                file_number = f"{random.randint(1, 99):02d}"
                short_date = encounter_date.strftime("%m.%d.%y")
                
                file_name = f"{specialty}_{short_date}_{last_name}_{file_number}.{file_ext}"
                folder_name = f"{specialty}_{short_date}_{last_name}_{file_number}"
                azure_path = f"Simcenter/{folder_name}/{file_type}/{file_name}"
                
                encounter_file = baker.make(
                    "EncounterFile",
                    encounter=encounter,
                    file_type=file_type,
                    file_name=file_name,
                    file_path=azure_path
                )
                encounter_files.append(encounter_file)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(encounters)} SimCenter encounters with {len(encounter_files)} files'))
        return encounters, encounter_files


    def _print_summary(self, clinic_patients, simcenter_patients, clinic_providers, 
                      simcenter_providers, clinic_encounters, simcenter_encounters, 
                      encounter_files, tiers):
        """Print generation summary"""
        self.stdout.write(self.style.SUCCESS('\n=== MOCK DATA GENERATION COMPLETE ==='))
        self.stdout.write(f'Patients: {len(clinic_patients)} clinic + {len(simcenter_patients)} SimCenter = {len(clinic_patients) + len(simcenter_patients)} total')
        self.stdout.write(f'Providers: {len(clinic_providers)} clinic + {len(simcenter_providers)} SimCenter = {len(clinic_providers) + len(simcenter_providers)} total')
        self.stdout.write(f'Encounters: {len(clinic_encounters)} clinic + {len(simcenter_encounters)} SimCenter = {len(clinic_encounters) + len(simcenter_encounters)} total')
        self.stdout.write(f'Encounter Files: {len(encounter_files)} total')
        self.stdout.write(f'Access Tiers: {len(tiers)} levels')
        self.stdout.write(f'Departments: 5 (including Penn Sim-Center)')
        self.stdout.write(f'Encounter Sources: 2 (Clinic, Simcenter)')
        self.stdout.write(self.style.SUCCESS('Ready for testing!'))
