import re

def is_response_list(response: str, min_items_count: int = 3) -> bool:
    """Helper function to test if response contains a list with at least min_items_count items in it.
    min_items_count cannot be less than 1 as it's nonsensical to have less than 1 item in a list."""

    # Early exit for nonsensical item counts
    if min_items_count < 1:
        return False

    # Check for semicolons - need at least (min_items_count - 1) to form min_items_count list items
    if response.count(';') >= min_items_count - 1:
        return True

    # Check the simple list markers pattern
    simple_markers_pattern = r'^\s*[-*>•◦▪]'
    if len(re.findall(simple_markers_pattern, response, re.MULTILINE)) >= min_items_count:
        return True

    # Check the complex list markers pattern
    complex_markers_pattern = r'^\s*(?:step|phase|stage|part|point|item|number|note|rule|section)*\s*(?:\d+\.\s+|[a-z][.:]\s+)'
    if len(re.findall(complex_markers_pattern, response, re.MULTILINE | re.IGNORECASE)) >= min_items_count:
        return True

    return False

def filter_non_alpha_lower(text):
    "Helper function to filter out non-alphabetic characters and convert to lowercase"
    return ''.join(c for c in text if c.isalpha()).lower()
