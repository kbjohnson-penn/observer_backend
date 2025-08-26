"""
Validator tests for shared app.
Migrated from shared/tests.py for better organization.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import date, datetime

from shared.validators import (
    validate_phone_number, validate_numeric, validate_time,
    validate_field, validate_address
)


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
        # Test whitespace only - this actually passes since it strips to empty
        # validate_field('   ')  # This is allowed
        
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
        
        # Test whitespace only - this actually passes since it strips to empty
        # validate_address('   ')  # This is allowed
        
        # Test too long
        with self.assertRaises(ValidationError):
            validate_address('x' * 201)
        
        # Test invalid characters
        with self.assertRaises(ValidationError):
            validate_address('123 Main St @ Invalid$')