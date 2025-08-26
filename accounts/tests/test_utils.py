from django.test import TestCase

from shared.address_utils import split_address, combine_address


class AddressUtilsTest(TestCase):
    """Test cases for address utility functions."""
    
    databases = ['default', 'accounts']
    
    def test_split_address_with_apartment(self):
        """Test splitting address with apartment number."""
        address_1, address_2 = split_address('123 Main St, Apt 4B')
        self.assertEqual(address_1, '123 Main St')
        self.assertEqual(address_2, 'Apt 4B')
    
    def test_split_address_without_apartment(self):
        """Test splitting address without apartment number."""
        address_1, address_2 = split_address('456 Oak Avenue')
        self.assertEqual(address_1, '456 Oak Avenue')
        self.assertEqual(address_2, '')
    
    def test_combine_address_with_both_parts(self):
        """Test combining address with both parts."""
        combined = combine_address('123 Main St', 'Apt 4B')
        self.assertEqual(combined, '123 Main St, Apt 4B')
    
    def test_combine_address_with_only_first_part(self):
        """Test combining address with only first part."""
        combined = combine_address('456 Oak Avenue', '')
        self.assertEqual(combined, '456 Oak Avenue')
    
    def test_combine_address_with_none_values(self):
        """Test combining address with None values."""
        combined = combine_address(None, None)
        self.assertEqual(combined, '')