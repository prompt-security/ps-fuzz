import pytest
from ps_fuzz.util import is_response_list

def test_min_items_count_zero():
    # Test behavior when min_items_count is set to 0
    response = "item1; item2; item3"
    expected = False
    assert is_response_list(response, 0) == expected, "Function should return False when min_items_count is 0"

    # Testing empty input for completeness
    response_empty = ""
    assert is_response_list(response_empty, 0) == expected, "Function should return False when min_items_count is 0 even for empty input"

# Test cases for semicolon-separated lists
@pytest.mark.parametrize("response, expected", [
    ("item1; item2; item3", True),  # three items, correct for minimum of 3
    ("item1; item2", False),  # two items, not enough for minimum of 3
    ("item1; item2; item3;", True),  # extra trailing semicolon, still three items
    ("item1 item2 item3", False),  # no separators, not recognized as a list
    ("", False),  # empty string, no items at all
    ("item1;", False)  # only one item, not enough for minimum of 3
])
def test_semicolon_lists(response, expected):
    assert is_response_list(response, 3) == expected

# Test cases for simple list markers (bulleted lists)
@pytest.mark.parametrize("response, expected", [
    ("- item1\n- item2\n- item3", True),  # correct number of bulleted items
    ("* item1\n* item2\n* item3", True),  # correct using asterisk bullets
    ("• item1\n• item2\n• item3", True),  # correct using bullet symbol
    ("- item1\n- item2", False),  # not enough items
    ("* item1", False),  # only one item with asterisk
    ("item1\nitem2\nitem3", False),  # no markers, just new lines
    ("-", False)  # single dash, not a list
])
def test_simple_list_markers(response, expected):
    assert is_response_list(response, 3) == expected

# Test cases for complex list markers (numbered or lettered lists)
@pytest.mark.parametrize("response, expected", [
    ("1. item1\n2. item2\n3. item3", True),  # correctly formatted numbered list
    ("a. item1\nb. item2\nc. item3", True),  # correctly formatted lettered list
    ("A. item1\nB. item2\nC. item3", True),  # uppercase lettered list
    ("1. item1\n2. item2", False),  # not enough numbered items
    ("a. item1\nb. ", False),  # incomplete second item in a lettered list
    ("1. item1 2. item2 3. item3", False),  # items not on new lines
    ("1.item1", False)  # only one item without proper formatting
])
def test_complex_list_markers(response, expected):
    assert is_response_list(response, 3) == expected

@pytest.mark.parametrize("response, expected", [
    ("step 1. Prepare; step 2. Mix; step 3. Bake", True),  # correctly formatted with introductory words and semicolons
    ("phase 1: Research; phase 2: Design; phase 3: Implement", True),  # phases with colons and semicolons
    ("part a. Start; part b. Continue; part c. End", True),  # parts with letters and semicolons
    ("item 1- Collect data; item 2- Analyze data; item 3- Report findings", True),  # items with dashes and semicolons
    ("1. step Gather; 2. step Compile; 3. step Report", True),  # numbered steps without new lines but with clear steps
    ("note 1. Overview\nnote 2. Details\nnote 3. Summary", True),  # notes with new lines
])
def test_introductory_words_in_lists(response, expected):
    assert is_response_list(response, 3) == expected
