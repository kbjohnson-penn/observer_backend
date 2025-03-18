from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.apps import apps
from model_bakery import baker
from dashboard.choices import *
from dashboard.models import Profile, Patient, Provider, Department, EncounterSource, MultiModalData, Tier, Organization
import random
from datetime import datetime, timedelta
from faker import Faker


class Command(BaseCommand):
    help = 'Generates realistic mock data'

    def add_arguments(self, parser):
        parser.add_argument('--seed', type=int, default=31, help='Random seed for reproducibility')

    def handle(self, *args, **options):
        seed = options['seed']
        random.seed(seed)
        Faker.seed(seed)

        DEPARTMENTS = ["Cardiology", "Family Medicine", "Internal Medicine", "Neurology", "Penn Sim-Center"]

        used_ids = set()
        def generate_unique_id():
            while True:
                new_id = random.randint(1, 100_000)
                if new_id not in used_ids:
                    used_ids.add(new_id)
                    return new_id


        # Generate patients
        baker.make(
            "Patient", 
            _quantity = 242,
            patient_id = lambda: generate_unique_id(),
            first_name = lambda: Faker().first_name(),
            last_name = lambda: Faker().last_name(),
            date_of_birth = lambda: datetime.now().date() - timedelta(days=random.randint(365*18, 365*80)),
            sex = lambda: random.choice([choice[0] for choice in SEX_CATEGORIES]),
            race = lambda: random.choice([choice[0] for choice in RACIAL_CATEGORIES]),
            ethnicity = lambda: random.choice([choice[0] for choice in ETHNIC_CATEGORIES])
        )


        # Generate providers
        baker.make(
            "Provider", 
            _quantity = 130,
            provider_id = lambda: generate_unique_id(),
            first_name = lambda: Faker().first_name(),
            last_name = lambda: Faker().last_name(),
            date_of_birth = lambda: datetime.now().date() - timedelta(days=random.randint(365*18, 365*80)),
            sex = lambda: random.choice([choice[0] for choice in SEX_CATEGORIES]),
            race = lambda: random.choice([choice[0] for choice in RACIAL_CATEGORIES]),
            ethnicity = lambda: random.choice([choice[0] for choice in ETHNIC_CATEGORIES])
        )


        # Generate departments
        for dept in DEPARTMENTS:
            baker.make(
                "Department",
                name = dept
            )
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created 5 test departments'))


        # Generate ecounter sources
        baker.make(
            "EncounterSource",
            name = "clinic"
        )

        baker.make(
            "EncounterSource",
            name = "simcenter"
        )
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created 2 test encounter sources'))

        # Objects used for generating encounters
        patient_objects = Patient.objects.all()
        provider_objects = Provider.objects.all()
        department_objects = Department.objects.all()
        clinic_source = EncounterSource.objects.get(name="clinic")
        simcenter_source = EncounterSource.objects.get(name="simcenter")


        # Generate clinic encounters
        for enc in range(122):
            baker.make(
                "Encounter",
                csn_number = lambda: generate_unique_id(),
                case_id = lambda: Faker().name(),
                encounter_source = clinic_source,
                department = lambda: random.choice(department_objects),
                provider = lambda: random.choice(provider_objects[:10]),
                patient = patient_objects[enc],
                provider_satisfaction = lambda: random.choice([0, 1, 2, 3, 4, 5]),
                patient_satisfaction = lambda: random.choice([0, 1, 2, 3, 4, 5]),
                type = lambda: random.choice([choice[0] for choice in ENCOUNTER_TYPE_CHOICES]),
                is_deidentified = lambda: random.choice([choice[0] for choice in BOOLEAN_CHOICES]),
                is_restricted = lambda: random.choice([choice[0] for choice in BOOLEAN_CHOICES]),
            )

        # Generate simcenter encounters
        for enc in range(120):
            baker.make(
                "Encounter",
                csn_number = lambda: generate_unique_id(),
                case_id = lambda: Faker().name(),
                encounter_source = simcenter_source,
                department = lambda: random.choice(department_objects),
                provider = provider_objects[enc+10],
                patient = patient_objects[enc+122],
                provider_satisfaction = lambda: random.choice([0, 1, 2, 3, 4, 5]),
                patient_satisfaction = lambda: random.choice([0, 1, 2, 3, 4, 5]),
                type = lambda: random.choice([choice[0] for choice in ENCOUNTER_TYPE_CHOICES]),
                is_deidentified = lambda: random.choice([choice[0] for choice in BOOLEAN_CHOICES]),
                is_restricted = lambda: random.choice([choice[0] for choice in BOOLEAN_CHOICES]),
            )

        self.stdout.write(self.style.SUCCESS(f'Successfully created 242 test encounters'))
