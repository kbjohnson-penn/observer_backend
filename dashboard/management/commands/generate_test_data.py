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
    help = 'Generates test data'

    def add_arguments(self, parser):
        parser.add_argument('--n_samples', type=int, default=10, help='Number of data samples to create in each model')
        parser.add_argument('--seed', type=int, default=42, help='Random seed for reproducibility')

    def handle(self, *args, **options):
        num_samples = options['n_samples']
        seed = options['seed']
        random.seed(seed)
        Faker.seed(seed)

        counter = [1]
        def unique_mm_id():
            counter[0] += 1
            return counter[0]
        
        def int_to_letters(num):
            return ''.join(chr(97 + int(digit)) for digit in str(num))

        used_ids = set()
        def generate_unique_id():
            while True:
                new_id = random.randint(1, 100_000)
                if new_id not in used_ids:
                    used_ids.add(new_id)
                    return new_id


        # Generate patients/providers
        for model in ["Patient", "Provider"]:
            model_names = [generate_unique_id() for _ in range(num_samples)]

            fields = {
                'first_name': lambda: Faker().first_name(),
                'last_name': lambda: Faker().last_name(),
                'date_of_birth': lambda: datetime.now().date() - timedelta(days=random.randint(365*18, 365*80)),
                'sex': lambda: random.choice([choice[0] for choice in SEX_CATEGORIES]),
                'race': lambda: random.choice([choice[0] for choice in RACIAL_CATEGORIES]),
                'ethnicity': lambda: random.choice([choice[0] for choice in ETHNIC_CATEGORIES]),
            }
            
            if model == "Patient":
                fields['patient_id'] = iter(model_names)
            elif model == "Provider":
                fields['provider_id'] = iter(model_names)

            baker.make(model, _quantity=num_samples, **fields)

            self.stdout.write(self.style.SUCCESS(f'Successfully created {num_samples} test {model.lower()}s'))


        # Generate departments
        baker.make(
            "Department",
            _quantity = num_samples,
            name = lambda: int_to_letters(generate_unique_id())
        )
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {num_samples} test departments'))
        

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


        # Generate organizations
        baker.make(
            "Organization",
            _quantity = num_samples,
            name = lambda: Faker().name(),
            address_1 = lambda: Faker().name(),
            address_2 = lambda: Faker().name(),
            city = lambda: Faker().name(),
            state = lambda: Faker().name(),
            country = lambda: Faker().name(),
            zip_code = lambda: random.randint(10_000, 99_999),
            phone_number = lambda: random.randint(1_000_000_000, 9_999_999_999),
            website = lambda: Faker().first_name() + ".com",
        )
            
        self.stdout.write(self.style.SUCCESS(f'Successfully created {num_samples} test organizations'))


        # Generate tiers
        for i in range(5):
            baker.make(
                "Tier",
                id=i+2,
                tier_name=f"tier {int_to_letters(i)}",
                level=i+1,
                complete_deidentification=True if i in [1, 2] else False,
                blur_sexually_explicit_body_parts=True if i in [1, 2] else False,
                blur_face=True if i in [1, 2] else False,
                obscure_voice=True if i in [1, 2] else False,
                dua=False if i in [0, 1] else True,
                external_access=False if i == 4 else True
            )

        self.stdout.write(self.style.SUCCESS('Successfully created 5 test tiers'))


        # Objects used for generating users & encounters
        patient_objects = Patient.objects.all()
        provider_objects = Provider.objects.all()
        department_objects = Department.objects.all()
        encountersource_objects = EncounterSource.objects.all()
        # multimodaldata_objects = MultiModalData.objects.all()
        tier_objects = Tier.objects.all()
        organization_objects = Organization.objects.all()


        # Generate users
        for i in range(5):
            user = baker.make(
                User,
                username=f"user{i+1}",
            )

            user.set_password("observer123")
            user.save()

            profile, _ = Profile.objects.get_or_create(user=user)
            dob = datetime.now().date() - timedelta(days=random.randint(365 * 18, 365 * 80))
            profile.date_of_birth = dob
            profile.phone_number = f"{random.randint(100, 999)}{random.randint(100, 999)}{random.randint(1000, 9999)}"
            profile.organization = organization_objects[i]
            profile.tier = tier_objects[i]
            profile.address_1 = Faker().name()
            profile.city = Faker().name()
            profile.state = Faker().name()
            profile.country = Faker().name()
            profile.zip_code = str(random.randint(10000, 99999)).zfill(5)
            profile.bio = "Bio for user"
            profile.save()

        self.stdout.write(self.style.SUCCESS('Successfully created 5 test profiles'))


        # Generate multi modal data
        # baker.make(
        #     "MultiModalData",
        #     _quantity = num_samples,
        #     id = unique_mm_id(),
        #     provider_view = lambda: random.choice([choice[0] for choice in BOOLEAN_CHOICES]),
        #     patient_view = lambda: random.choice([choice[0] for choice in BOOLEAN_CHOICES]),
        #     room_view = lambda: random.choice([choice[0] for choice in BOOLEAN_CHOICES]),
        #     audio = lambda: random.choice([choice[0] for choice in BOOLEAN_CHOICES]),
        #     transcript = lambda: random.choice([choice[0] for choice in BOOLEAN_CHOICES]),
        #     patient_survey = lambda: random.choice([choice[0] for choice in BOOLEAN_CHOICES]),
        #     provider_survey = lambda: random.choice([choice[0] for choice in BOOLEAN_CHOICES]),
        #     patient_annotation = lambda: random.choice([choice[0] for choice in BOOLEAN_CHOICES]),
        #     provider_annotation = lambda: random.choice([choice[0] for choice in BOOLEAN_CHOICES]),
        #     rias_transcript = lambda: random.choice([choice[0] for choice in BOOLEAN_CHOICES]),
        #     rias_codes = lambda: random.choice([choice[0] for choice in BOOLEAN_CHOICES])
        # )

        # self.stdout.write(self.style.SUCCESS(f'Successfully created {num_samples} test multi modal data objects'))
    

        # Generate encounter data
        baker.make(
            "Encounter",
            _quantity = num_samples,
            csn_number = lambda: generate_unique_id(),
            case_id = lambda: Faker().name(),
            encounter_source = lambda: random.choice(encountersource_objects),
            department = lambda: random.choice(department_objects),
            provider = lambda: random.choice(provider_objects),
            patient = lambda: random.choice(patient_objects),
            provider_satisfaction = lambda: random.choice([0, 1, 2, 3, 4, 5]),
            patient_satisfaction = lambda: random.choice([0, 1, 2, 3, 4, 5]),
            # multi_modal_data = lambda: random.choice(multimodaldata_objects),
            type = lambda: random.choice([choice[0] for choice in ENCOUNTER_TYPE_CHOICES]),
            is_deidentified = lambda: random.choice([choice[0] for choice in BOOLEAN_CHOICES]),
            is_restricted = lambda: random.choice([choice[0] for choice in BOOLEAN_CHOICES]),
            tier = lambda: random.choice(tier_objects),
        )

        self.stdout.write(self.style.SUCCESS(f'Successfully created {num_samples} test encounters'))
