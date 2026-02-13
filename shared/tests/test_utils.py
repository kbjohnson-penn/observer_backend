"""
Utility function tests for shared app.
Migrated and expanded from shared/tests.py for better organization.
"""

from datetime import date
from unittest.mock import patch

from django.test import TestCase

from shared.address_utils import combine_address, split_address
from shared.utils import calculate_age


class UtilsTest(TestCase):
    """Test cases for shared utilities."""

    def test_calculate_age_valid_date(self):
        """Test age calculation with valid birth date."""
        # Test with known birth date
        birth_date = date(1990, 1, 1)
        current_date = date(2024, 1, 1)

        # Mock date.today() to return known date
        with patch("shared.utils.date") as mock_date:
            mock_date.today.return_value = current_date
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)

            age = calculate_age(birth_date)
            self.assertEqual(age, 34)

    def test_calculate_age_birthday_not_yet(self):
        """Test age calculation when birthday hasn't occurred this year."""
        birth_date = date(1990, 6, 15)
        current_date = date(2024, 3, 1)  # Before birthday

        with patch("shared.utils.date") as mock_date:
            mock_date.today.return_value = current_date
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)

            age = calculate_age(birth_date)
            self.assertEqual(age, 33)  # Should be one year less

    def test_calculate_age_birthday_passed(self):
        """Test age calculation when birthday has already occurred this year."""
        birth_date = date(1990, 3, 15)
        current_date = date(2024, 6, 1)  # After birthday

        with patch("shared.utils.date") as mock_date:
            mock_date.today.return_value = current_date
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)

            age = calculate_age(birth_date)
            self.assertEqual(age, 34)

    def test_calculate_age_same_birthday(self):
        """Test age calculation on exact birthday."""
        birth_date = date(1990, 3, 15)
        current_date = date(2024, 3, 15)  # Same day

        with patch("shared.utils.date") as mock_date:
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

        with patch("shared.utils.date") as mock_date:
            mock_date.today.return_value = current_date
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)

            age = calculate_age(birth_date)
            self.assertEqual(age, -1)  # Should be negative


class AddressUtilsTest(TestCase):
    """Test cases for address utility functions."""

    def test_split_address_with_comma(self):
        """Test splitting address containing comma."""
        address = "123 Main St, Apt 2B"
        address_1, address_2 = split_address(address)

        self.assertEqual(address_1, "123 Main St")
        self.assertEqual(address_2, "Apt 2B")

    def test_split_address_without_comma(self):
        """Test splitting address without comma."""
        address = "456 Oak Avenue"
        address_1, address_2 = split_address(address)

        self.assertEqual(address_1, "456 Oak Avenue")
        self.assertEqual(address_2, "")

    def test_split_address_empty_input(self):
        """Test splitting empty address."""
        address_1, address_2 = split_address("")
        self.assertEqual(address_1, "")
        self.assertEqual(address_2, "")

        address_1, address_2 = split_address(None)
        self.assertEqual(address_1, "")
        self.assertEqual(address_2, "")

    def test_split_address_multiple_commas(self):
        """Test splitting address with multiple commas."""
        address = "789 Pine Rd, Suite 100, Floor 2"
        address_1, address_2 = split_address(address)

        self.assertEqual(address_1, "789 Pine Rd")
        self.assertEqual(address_2, "Suite 100, Floor 2")

    def test_split_address_whitespace_handling(self):
        """Test splitting address with extra whitespace."""
        address = "  123 Main St  ,  Apt 2B  "
        address_1, address_2 = split_address(address)

        self.assertEqual(address_1, "123 Main St")
        self.assertEqual(address_2, "Apt 2B")

    def test_split_address_max_length(self):
        """Test splitting address with very long components."""
        long_street = "x" * 150  # Longer than 100 chars
        long_apt = "y" * 150
        address = f"{long_street}, {long_apt}"

        address_1, address_2 = split_address(address)

        # Should be truncated to 100 chars
        self.assertEqual(len(address_1), 100)
        self.assertEqual(len(address_2), 100)
        self.assertEqual(address_1, "x" * 100)
        self.assertEqual(address_2, "y" * 100)

    def test_combine_address_both_parts(self):
        """Test combining address with both parts."""
        address_1 = "123 Main St"
        address_2 = "Apt 2B"

        combined = combine_address(address_1, address_2)
        self.assertEqual(combined, "123 Main St, Apt 2B")

    def test_combine_address_first_part_only(self):
        """Test combining address with only first part."""
        address_1 = "456 Oak Avenue"
        address_2 = ""

        combined = combine_address(address_1, address_2)
        self.assertEqual(combined, "456 Oak Avenue")

    def test_combine_address_second_part_only(self):
        """Test combining address with only second part."""
        address_1 = ""
        address_2 = "Suite 100"

        combined = combine_address(address_1, address_2)
        self.assertEqual(combined, "Suite 100")

    def test_combine_address_empty_parts(self):
        """Test combining empty address parts."""
        combined = combine_address("", "")
        self.assertEqual(combined, "")

        combined = combine_address(None, None)
        self.assertEqual(combined, "")

    def test_combine_address_whitespace_only(self):
        """Test combining address with whitespace-only parts."""
        # The combine_address function doesn't strip whitespace, so '   ' is truthy
        combined = combine_address("   ", "")
        self.assertEqual(combined, "   ")  # Whitespace is preserved

        combined = combine_address("", "   ")
        self.assertEqual(combined, "   ")  # Whitespace is preserved

    def test_address_split_combine_roundtrip(self):
        """Test that split and combine operations are consistent."""
        test_addresses = [
            "123 Main St, Apt 2B",
            "456 Oak Avenue",
            "",
            "789 Pine Rd, Suite 100, Floor 2",
        ]

        for original in test_addresses:
            address_1, address_2 = split_address(original)
            recombined = combine_address(address_1, address_2)

            if original:
                # Should be equivalent (may differ in whitespace for multi-comma case)
                self.assertTrue(
                    original == recombined
                    or original.replace(", ", ",").replace(",", ", ") == recombined
                )
            else:
                self.assertEqual(recombined, "")
