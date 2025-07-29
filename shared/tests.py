from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from unittest.mock import MagicMock, patch

from shared.validators import (
    validate_phone_number, validate_numeric, validate_time,
    validate_field, validate_address
)
from shared.choices import (
    SEX_CATEGORIES, BOOLEAN_CHOICES, ENCOUNTER_TYPE_CHOICES,
    FILE_TYPE_CHOICES, FILE_TYPE_CHOICES_DICT
)
from shared.constants import (
    SIMCENTER_PATIENT_ID_LOWER_LIMIT, SIMCENTER_PATIENT_ID_UPPER_LIMIT,
    SIMCENTER_PROVIDER_ID_LOWER_LIMIT, SIMCENTER_PROVIDER_ID_UPPER_LIMIT
)
from shared.utils import calculate_age
from shared.db_router import DatabaseRouter
from shared.api.permissions.tier_permissions import (
    filter_queryset_by_user_tier, BaseAuthenticatedViewSet, HasAccessToEncounter
)
from shared.api.permissions.public_permissions import IsReadOnly
from accounts.models import Profile, Tier, Organization
from model_bakery import baker
from datetime import date, datetime


class ValidatorsTest(TestCase):
    """Test cases for shared validators."""
    
    def test_validate_phone_number_valid(self):
        """Test valid phone number validation."""
        valid_numbers = [
            '+1234567890',
            '1234567890',
            '+12345678901',
            '123-456-7890',
            '(123) 456-7890',
            '123 456 7890'
        ]
        
        for number in valid_numbers:
            try:
                validate_phone_number(number)
            except ValidationError:
                self.fail(f"validate_phone_number raised ValidationError for valid number: {number}")
    
    def test_validate_phone_number_invalid(self):
        """Test invalid phone number validation."""
        invalid_numbers = [
            '123',  # Too short
            '12345678901234567890',  # Too long
            'abc123def',  # Contains letters
            '123-456-789a',  # Contains letter at end
            '+++1234567890',  # Too many plus signs
        ]
        
        for number in invalid_numbers:
            with self.assertRaises(ValidationError):
                validate_phone_number(number)
    
    def test_validate_phone_number_empty_values(self):
        """Test phone number validation with empty values."""
        empty_values = [None, '', ' ', '   ']
        
        for value in empty_values:
            try:
                validate_phone_number(value)
            except ValidationError:
                self.fail(f"validate_phone_number raised ValidationError for empty value: {value}")
    
    def test_validate_numeric_valid(self):
        """Test valid numeric validation."""
        valid_numbers = ['123', '123.45', '0', '-123', '-123.45', '0.0']
        
        for number in valid_numbers:
            try:
                validate_numeric(number)
            except ValidationError:
                self.fail(f"validate_numeric raised ValidationError for valid number: {number}")
    
    def test_validate_numeric_invalid(self):
        """Test invalid numeric validation."""
        invalid_numbers = ['abc', '123abc', 'abc123', '12.34.56']
        
        for number in invalid_numbers:
            with self.assertRaises(ValidationError):
                validate_numeric(number)
    
    def test_validate_numeric_empty_values(self):
        """Test numeric validation with empty values."""
        empty_values = [None, '', ' ', '   ']
        
        for value in empty_values:
            try:
                validate_numeric(value)
            except ValidationError:
                self.fail(f"validate_numeric raised ValidationError for empty value: {value}")
    
    def test_validate_time_valid(self):
        """Test valid time/date validation."""
        # Test datetime objects
        try:
            validate_time(datetime(2024, 1, 1, 12, 0, 0))
            validate_time(date(2024, 1, 1))
            validate_time(None)
            validate_time('')
            validate_time('2024-01-01')
            validate_time('2024-01-01 12:00:00')
        except ValidationError:
            self.fail("validate_time raised ValidationError for valid inputs")
    
    def test_validate_time_invalid(self):
        """Test invalid time/date validation."""
        # Test dates too far in past/future
        with self.assertRaises(ValidationError):
            validate_time(date(1800, 1, 1))
        
        with self.assertRaises(ValidationError):
            validate_time(date(2050, 1, 1))
        
        # Test invalid string formats
        with self.assertRaises(ValidationError):
            validate_time('invalid-date')
    
    def test_validate_field_valid(self):
        """Test valid field validation."""
        try:
            validate_field('valid text')
            validate_field('short')
            validate_field(None)
            validate_field('')
        except ValidationError:
            self.fail("validate_field raised ValidationError for valid inputs")
    
    def test_validate_field_invalid(self):
        """Test invalid field validation."""
        # Test whitespace only
        with self.assertRaises(ValidationError):
            validate_field('   ')
        
        # Test too long
        with self.assertRaises(ValidationError):
            validate_field('x' * 1001)
    
    def test_validate_address_valid(self):
        """Test valid address validation."""
        try:
            validate_address('123 Main St')
            validate_address('456 Oak Ave, Apt 2B')
            validate_address('789 Pine Road, Suite 100')
            validate_address(None)
            validate_address('')
        except ValidationError:
            self.fail("validate_address raised ValidationError for valid inputs")
    
    def test_validate_address_invalid(self):
        """Test invalid address validation."""
        # Test too short
        with self.assertRaises(ValidationError):
            validate_address('123')
        
        # Test whitespace only
        with self.assertRaises(ValidationError):
            validate_address('   ')
        
        # Test too long
        with self.assertRaises(ValidationError):
            validate_address('x' * 201)
        
        # Test invalid characters
        with self.assertRaises(ValidationError):
            validate_address('123 Main St @ Invalid$')


class ChoicesTest(TestCase):
    """Test cases for shared choices."""
    
    def test_sex_categories(self):
        """Test sex categories choices."""
        expected_choices = [
            ('M', 'Male'),
            ('F', 'Female'),
            ('O', 'Other'),
            ('U', 'Unknown'),
        ]
        self.assertEqual(SEX_CATEGORIES, expected_choices)
    
    def test_boolean_choices(self):
        """Test boolean choices."""
        expected_choices = [
            (True, 'Yes'),
            (False, 'No'),
        ]
        self.assertEqual(BOOLEAN_CHOICES, expected_choices)
    
    def test_encounter_type_choices(self):
        """Test encounter type choices."""
        # Check that required encounter types are present
        choice_values = [choice[0] for choice in ENCOUNTER_TYPE_CHOICES]
        self.assertIn('clinic', choice_values)
        self.assertIn('simcenter', choice_values)
        self.assertIn('pennpersonalizedcare', choice_values)
    
    def test_file_type_choices(self):
        """Test file type choices."""
        # Check that required file types are present
        choice_values = [choice[0] for choice in FILE_TYPE_CHOICES]
        self.assertIn('video', choice_values)
        self.assertIn('audio', choice_values)
        self.assertIn('document', choice_values)
        self.assertIn('image', choice_values)
    
    def test_file_type_choices_dict(self):
        """Test file type choices dictionary."""
        # Check that dictionary has expected keys
        self.assertIn('video', FILE_TYPE_CHOICES_DICT)
        self.assertIn('audio', FILE_TYPE_CHOICES_DICT)
        self.assertIn('document', FILE_TYPE_CHOICES_DICT)
        self.assertIn('image', FILE_TYPE_CHOICES_DICT)
        
        # Check that values are human-readable
        self.assertEqual(FILE_TYPE_CHOICES_DICT['video'], 'Video')
        self.assertEqual(FILE_TYPE_CHOICES_DICT['audio'], 'Audio')


class ConstantsTest(TestCase):
    """Test cases for shared constants."""
    
    def test_simcenter_patient_id_limits(self):
        """Test SimCenter patient ID limits."""
        self.assertIsInstance(SIMCENTER_PATIENT_ID_LOWER_LIMIT, int)
        self.assertIsInstance(SIMCENTER_PATIENT_ID_UPPER_LIMIT, int)
        self.assertGreater(SIMCENTER_PATIENT_ID_UPPER_LIMIT, SIMCENTER_PATIENT_ID_LOWER_LIMIT)
    
    def test_simcenter_provider_id_limits(self):
        """Test SimCenter provider ID limits."""
        self.assertIsInstance(SIMCENTER_PROVIDER_ID_LOWER_LIMIT, int)
        self.assertIsInstance(SIMCENTER_PROVIDER_ID_UPPER_LIMIT, int)
        self.assertGreater(SIMCENTER_PROVIDER_ID_UPPER_LIMIT, SIMCENTER_PROVIDER_ID_LOWER_LIMIT)
    
    def test_id_range_separation(self):
        """Test that patient and provider ID ranges don't overlap."""
        # Ensure patient and provider ranges don't overlap
        self.assertTrue(
            SIMCENTER_PATIENT_ID_UPPER_LIMIT <= SIMCENTER_PROVIDER_ID_LOWER_LIMIT or
            SIMCENTER_PROVIDER_ID_UPPER_LIMIT <= SIMCENTER_PATIENT_ID_LOWER_LIMIT
        )


class UtilsTest(TestCase):
    """Test cases for shared utilities."""
    
    def test_calculate_age_valid_date(self):
        """Test age calculation with valid birth date."""
        # Test with known birth date
        birth_date = date(1990, 1, 1)
        current_date = date(2024, 1, 1)
        
        # Mock date.today() to return known date
        with patch('shared.utils.date') as mock_date:
            mock_date.today.return_value = current_date
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
            
            age = calculate_age(birth_date)
            self.assertEqual(age, 34)
    
    def test_calculate_age_birthday_not_yet(self):
        """Test age calculation when birthday hasn't occurred this year."""
        birth_date = date(1990, 6, 15)
        current_date = date(2024, 3, 1)  # Before birthday
        
        with patch('shared.utils.date') as mock_date:
            mock_date.today.return_value = current_date
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
            
            age = calculate_age(birth_date)
            self.assertEqual(age, 33)  # Should be one year less
    
    def test_calculate_age_birthday_passed(self):
        """Test age calculation when birthday has already occurred this year."""
        birth_date = date(1990, 3, 15)
        current_date = date(2024, 6, 1)  # After birthday
        
        with patch('shared.utils.date') as mock_date:
            mock_date.today.return_value = current_date
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
            
            age = calculate_age(birth_date)
            self.assertEqual(age, 34)
    
    def test_calculate_age_same_birthday(self):
        """Test age calculation on exact birthday."""
        birth_date = date(1990, 3, 15)
        current_date = date(2024, 3, 15)  # Same day
        
        with patch('shared.utils.date') as mock_date:
            mock_date.today.return_value = current_date
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
            
            age = calculate_age(birth_date)
            self.assertEqual(age, 34)
    
    def test_calculate_age_none_input(self):
        """Test age calculation with None input."""
        age = calculate_age(None)
        self.assertIsNone(age)
    
    def test_calculate_age_future_date(self):
        """Test age calculation with future birth date."""
        birth_date = date(2025, 1, 1)
        current_date = date(2024, 1, 1)
        
        with patch('shared.utils.date') as mock_date:
            mock_date.today.return_value = current_date
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
            
            age = calculate_age(birth_date)
            self.assertEqual(age, -1)  # Should be negative


class DatabaseRouterTest(TestCase):
    """Test cases for database router."""
    
    def setUp(self):
        self.router = DatabaseRouter()
    
    def test_route_app_labels(self):
        """Test that route app labels are correctly configured."""
        expected_labels = {
            'accounts': 'accounts',
            'clinical': 'clinical',
            'research': 'research',
            # Django system apps routed to accounts database
            'auth': 'accounts',
            'contenttypes': 'accounts',
            'sessions': 'accounts',
            'admin': 'accounts',
            'token_blacklist': 'accounts',
        }
        self.assertEqual(self.router.route_app_labels, expected_labels)
    
    def test_db_for_read(self):
        """Test database routing for read operations."""
        # Create mock models
        accounts_model = MagicMock()
        accounts_model._meta.app_label = 'accounts'
        
        clinical_model = MagicMock()
        clinical_model._meta.app_label = 'clinical'
        
        research_model = MagicMock()
        research_model._meta.app_label = 'research'
        
        unknown_model = MagicMock()
        unknown_model._meta.app_label = 'unknown'
        
        # Test routing
        self.assertEqual(self.router.db_for_read(accounts_model), 'accounts')
        self.assertEqual(self.router.db_for_read(clinical_model), 'clinical')
        self.assertEqual(self.router.db_for_read(research_model), 'research')
        self.assertIsNone(self.router.db_for_read(unknown_model))
    
    def test_db_for_write(self):
        """Test database routing for write operations."""
        # Create mock models
        accounts_model = MagicMock()
        accounts_model._meta.app_label = 'accounts'
        
        clinical_model = MagicMock()
        clinical_model._meta.app_label = 'clinical'
        
        research_model = MagicMock()
        research_model._meta.app_label = 'research'
        
        # Test routing
        self.assertEqual(self.router.db_for_write(accounts_model), 'accounts')
        self.assertEqual(self.router.db_for_write(clinical_model), 'clinical')
        self.assertEqual(self.router.db_for_write(research_model), 'research')
    
    def test_allow_relation_same_database(self):
        """Test allowing relations within the same database."""
        # Create mock objects in same database
        obj1 = MagicMock()
        obj1._state.db = 'clinical'
        
        obj2 = MagicMock()
        obj2._state.db = 'clinical'
        
        result = self.router.allow_relation(obj1, obj2)
        self.assertTrue(result)
    
    def test_allow_relation_cross_database_valid(self):
        """Test allowing valid cross-database relations."""
        # Clinical <-> Accounts (for Tier)
        clinical_obj = MagicMock()
        clinical_obj._state.db = 'clinical'
        
        accounts_obj = MagicMock()
        accounts_obj._state.db = 'accounts'
        
        result = self.router.allow_relation(clinical_obj, accounts_obj)
        self.assertTrue(result)
        
        # Clinical <-> Research (for ETL)
        research_obj = MagicMock()
        research_obj._state.db = 'research'
        
        result = self.router.allow_relation(clinical_obj, research_obj)
        self.assertTrue(result)
    
    def test_allow_relation_outside_managed_databases(self):
        """Test relations outside managed databases."""
        # Object outside managed databases
        external_obj = MagicMock()
        external_obj._state.db = 'external'
        
        clinical_obj = MagicMock()
        clinical_obj._state.db = 'clinical'
        
        result = self.router.allow_relation(external_obj, clinical_obj)
        self.assertIsNone(result)
    
    def test_allow_migrate_correct_database(self):
        """Test allowing migrations on correct database."""
        # Should allow app migrations on correct database
        result = self.router.allow_migrate('accounts', 'accounts', 'User')
        self.assertTrue(result)
        
        result = self.router.allow_migrate('clinical', 'clinical', 'Encounter')
        self.assertTrue(result)
        
        result = self.router.allow_migrate('research', 'research', 'VisitOccurrence')
        self.assertTrue(result)
    
    def test_allow_migrate_wrong_database(self):
        """Test preventing migrations on wrong database."""
        # Should not allow app migrations on wrong database
        result = self.router.allow_migrate('clinical', 'accounts', 'User')
        self.assertFalse(result)
        
        result = self.router.allow_migrate('research', 'clinical', 'Encounter')
        self.assertFalse(result)
        
        result = self.router.allow_migrate('accounts', 'research', 'VisitOccurrence')
        self.assertFalse(result)
    
    def test_allow_migrate_unknown_app(self):
        """Test migration routing for unknown apps."""
        # Unknown app should default to accounts database
        result = self.router.allow_migrate('accounts', 'unknown_app', 'UnknownModel')
        self.assertTrue(result)
        
        result = self.router.allow_migrate('clinical', 'unknown_app', 'UnknownModel')
        self.assertFalse(result)


class TierPermissionsTest(TestCase):
    """Test cases for tier-based permissions."""
    
    def setUp(self):
        self.organization = baker.make(Organization, name="Test Hospital")
        self.tier_1 = baker.make(Tier, tier_name="Tier 1", level=1)
        self.tier_2 = baker.make(Tier, tier_name="Tier 2", level=2)
        self.tier_3 = baker.make(Tier, tier_name="Tier 3", level=3)
        
        # Create users with different tier levels
        self.user_tier1 = User.objects.create_user(
            username='tier1user',
            email='tier1@example.com',
            password='testpass123'
        )
        self.profile_tier1 = baker.make(
            Profile,
            user=self.user_tier1,
            tier=self.tier_1,
            organization=self.organization
        )
        
        self.user_tier2 = User.objects.create_user(
            username='tier2user',
            email='tier2@example.com',
            password='testpass123'
        )
        self.profile_tier2 = baker.make(
            Profile,
            user=self.user_tier2,
            tier=self.tier_2,
            organization=self.organization
        )
        
        self.user_tier3 = User.objects.create_user(
            username='tier3user',
            email='tier3@example.com',
            password='testpass123'
        )
        self.profile_tier3 = baker.make(
            Profile,
            user=self.user_tier3,
            tier=self.tier_3,
            organization=self.organization
        )
        
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
    
    def test_filter_queryset_by_user_tier_tier1(self):
        """Test queryset filtering for tier 1 user."""
        queryset = Tier.objects.all()
        
        filtered = filter_queryset_by_user_tier(
            queryset, self.user_tier1, "level__lte"
        )
        
        # Tier 1 user should only see tier 1
        accessible_levels = [tier.level for tier in filtered]
        self.assertEqual(accessible_levels, [1])
    
    def test_filter_queryset_by_user_tier_tier2(self):
        """Test queryset filtering for tier 2 user."""
        queryset = Tier.objects.all()
        
        filtered = filter_queryset_by_user_tier(
            queryset, self.user_tier2, "level__lte"
        )
        
        # Tier 2 user should see tier 1 and 2
        accessible_levels = sorted([tier.level for tier in filtered])
        self.assertEqual(accessible_levels, [1, 2])
    
    def test_filter_queryset_by_user_tier_tier3(self):
        """Test queryset filtering for tier 3 user."""
        queryset = Tier.objects.all()
        
        filtered = filter_queryset_by_user_tier(
            queryset, self.user_tier3, "level__lte"
        )
        
        # Tier 3 user should see all tiers
        accessible_levels = sorted([tier.level for tier in filtered])
        self.assertEqual(accessible_levels, [1, 2, 3])
    
    def test_filter_queryset_by_user_tier_superuser(self):
        """Test queryset filtering for superuser."""
        queryset = Tier.objects.all()
        
        filtered = filter_queryset_by_user_tier(
            queryset, self.superuser, "level__lte"
        )
        
        # Superuser should see all tiers
        accessible_levels = sorted([tier.level for tier in filtered])
        self.assertEqual(accessible_levels, [1, 2, 3])
    
    def test_filter_queryset_by_user_tier_no_profile(self):
        """Test queryset filtering for user without profile."""
        user_no_profile = User.objects.create_user(
            username='noprofile',
            email='noprofile@example.com',
            password='testpass123'
        )
        
        queryset = Tier.objects.all()
        
        filtered = filter_queryset_by_user_tier(
            queryset, user_no_profile, "level__lte"
        )
        
        # User without profile should see nothing
        self.assertEqual(filtered.count(), 0)
    
    def test_filter_queryset_by_user_tier_custom_field(self):
        """Test queryset filtering with custom related field."""
        queryset = Tier.objects.all()
        
        # Test with different field name
        filtered = filter_queryset_by_user_tier(
            queryset, self.user_tier2, "level__lte"
        )
        
        # Should work the same way
        accessible_levels = sorted([tier.level for tier in filtered])
        self.assertEqual(accessible_levels, [1, 2])


class BaseAuthenticatedViewSetTest(APITestCase):
    """Test cases for BaseAuthenticatedViewSet."""
    
    def setUp(self):
        self.organization = baker.make(Organization, name="Test Hospital")
        self.tier_1 = baker.make(Tier, tier_name="Tier 1", level=1)
        self.tier_2 = baker.make(Tier, tier_name="Tier 2", level=2)
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = baker.make(
            Profile,
            user=self.user,
            tier=self.tier_2,
            organization=self.organization
        )
        
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
    
    def test_has_access_to_tier_regular_user(self):
        """Test tier access for regular user."""
        viewset = BaseAuthenticatedViewSet()
        
        # User should have access to tier 1 and 2
        self.assertTrue(viewset.has_access_to_tier(self.user, self.tier_1))
        self.assertTrue(viewset.has_access_to_tier(self.user, self.tier_2))
        
        # Create tier 3 for testing
        tier_3 = baker.make(Tier, tier_name="Tier 3", level=3)
        self.assertFalse(viewset.has_access_to_tier(self.user, tier_3))
    
    def test_has_access_to_tier_superuser(self):
        """Test tier access for superuser."""
        viewset = BaseAuthenticatedViewSet()
        
        # Superuser should have access to all tiers
        self.assertTrue(viewset.has_access_to_tier(self.superuser, self.tier_1))
        self.assertTrue(viewset.has_access_to_tier(self.superuser, self.tier_2))
        
        tier_3 = baker.make(Tier, tier_name="Tier 3", level=3)
        self.assertTrue(viewset.has_access_to_tier(self.superuser, tier_3))
    
    def test_has_access_to_tier_no_profile(self):
        """Test tier access for user without profile."""
        user_no_profile = User.objects.create_user(
            username='noprofile',
            email='noprofile@example.com',
            password='testpass123'
        )
        
        viewset = BaseAuthenticatedViewSet()
        
        # User without profile should have no access
        self.assertFalse(viewset.has_access_to_tier(user_no_profile, self.tier_1))
        self.assertFalse(viewset.has_access_to_tier(user_no_profile, self.tier_2))


class HasAccessToEncounterTest(TestCase):
    """Test cases for HasAccessToEncounter permission."""
    
    def setUp(self):
        self.organization = baker.make(Organization, name="Test Hospital")
        self.tier_1 = baker.make(Tier, tier_name="Tier 1", level=1)
        self.tier_2 = baker.make(Tier, tier_name="Tier 2", level=2)
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = baker.make(
            Profile,
            user=self.user,
            tier=self.tier_2,
            organization=self.organization
        )
        
        self.permission = HasAccessToEncounter()
    
    def test_has_object_permission_encounter_access(self):
        """Test object permission for encounter access."""
        # Create mock encounter
        encounter = MagicMock()
        encounter.tier = self.tier_1  # User has access to tier 1
        
        # Create mock request and view
        request = MagicMock()
        request.user = self.user
        
        view = MagicMock()
        view.has_access_to_tier.return_value = True
        
        # Should have access
        result = self.permission.has_object_permission(request, view, encounter)
        self.assertTrue(result)
        
        # Verify view method was called
        view.has_access_to_tier.assert_called_once_with(self.user, self.tier_1)
    
    def test_has_object_permission_encounter_no_access(self):
        """Test object permission for encounter without access."""
        # Create mock encounter
        encounter = MagicMock()
        encounter.tier = self.tier_2
        
        # Create mock request and view
        request = MagicMock()
        request.user = self.user
        
        view = MagicMock()
        view.has_access_to_tier.return_value = False
        
        # Should not have access
        result = self.permission.has_object_permission(request, view, encounter)
        self.assertFalse(result)
    
    def test_has_object_permission_unsupported_object(self):
        """Test object permission for unsupported object type."""
        # Create mock unsupported object
        unsupported_obj = MagicMock()
        unsupported_obj.__class__.__name__ = 'UnsupportedModel'
        
        # Create mock request and view
        request = MagicMock()
        request.user = self.user
        
        view = MagicMock()
        
        # Should return False for unsupported objects
        result = self.permission.has_object_permission(request, view, unsupported_obj)
        self.assertFalse(result)


class PublicPermissionsTest(TestCase):
    """Test cases for public permissions."""
    
    def test_is_read_only_permission(self):
        """Test IsReadOnly permission."""
        permission = IsReadOnly()
        
        # Create mock request and view
        request = MagicMock()
        view = MagicMock()
        
        # Should allow GET requests
        request.method = 'GET'
        result = permission.has_permission(request, view)
        self.assertTrue(result)
        
        # Should allow HEAD requests
        request.method = 'HEAD'
        result = permission.has_permission(request, view)
        self.assertTrue(result)
        
        # Should allow OPTIONS requests
        request.method = 'OPTIONS'
        result = permission.has_permission(request, view)
        self.assertTrue(result)
        
        # Should deny POST requests
        request.method = 'POST'
        result = permission.has_permission(request, view)
        self.assertFalse(result)
        
        # Should deny PUT requests
        request.method = 'PUT'
        result = permission.has_permission(request, view)
        self.assertFalse(result)
        
        # Should deny DELETE requests
        request.method = 'DELETE'
        result = permission.has_permission(request, view)
        self.assertFalse(result)
        
        # Should deny PATCH requests
        request.method = 'PATCH'
        result = permission.has_permission(request, view)
        self.assertFalse(result)
