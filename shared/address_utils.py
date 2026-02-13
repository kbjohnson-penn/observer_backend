"""
Utility functions for handling address fields.
"""


def split_address(address):
    """
    Split a single address string into address_1 and address_2.

    Args:
        address (str): The full address string

    Returns:
        tuple: (address_1, address_2) where address_2 may be empty
    """
    if not address:
        return "", ""

    # Split address into two parts if it contains a comma
    if "," in address:
        parts = address.split(",", 1)
        address_1 = parts[0].strip()[:100]  # Ensure max length
        address_2 = parts[1].strip()[:100] if len(parts) > 1 else ""
    else:
        address_1 = address.strip()[:100]  # Ensure max length
        address_2 = ""

    return address_1, address_2


def combine_address(address_1, address_2):
    """
    Combine address_1 and address_2 into a single string.

    Args:
        address_1 (str): First line of address
        address_2 (str): Second line of address

    Returns:
        str: Combined address with comma separator if both parts exist
    """
    parts = [part for part in [address_1, address_2] if part]
    return ", ".join(parts) if parts else ""
