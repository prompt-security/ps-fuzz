import pytest
from ps_fuzz.test_base import TestStatus
from ps_fuzz.prompt_injection_fuzzer import isSkipped


class TestStatusSkippedFunctionality:
    """Test class for TestStatus skipped functionality."""

    def test_skipped_count_property(self):
        """Test skipped_count property getter."""
        status = TestStatus()

        # Test initial value
        assert status.skipped_count == 0

        # Test after manual increment (simulating internal behavior)
        status.skipped_count = 5
        assert status.skipped_count == 5

    def test_report_skipped_increments_count(self):
        """Test report_skipped() increments skipped_count."""
        status = TestStatus()

        # Initial state
        assert status.skipped_count == 0
        assert status.total_count == 0

        # Report one skipped test
        status.report_skipped("test prompt", "Test skipped due to missing config")
        assert status.skipped_count == 1
        assert status.total_count == 1

        # Report another skipped test
        status.report_skipped("another prompt", "Another skip reason")
        assert status.skipped_count == 2
        assert status.total_count == 2

    def test_report_skipped_adds_log_entry(self):
        """Test report_skipped() adds proper log entry."""
        status = TestStatus()

        prompt = "test prompt for skipping"
        additional_info = "Custom skip reason"

        status.report_skipped(prompt, additional_info)

        # Check log entry was added
        assert len(status.log) == 1
        log_entry = status.log[0]

        # Verify log entry properties
        assert log_entry.prompt == prompt
        assert log_entry.response is None
        assert log_entry.success is False
        assert log_entry.additional_info == additional_info

    def test_report_skipped_updates_total_count(self):
        """Test report_skipped() increments total_count."""
        status = TestStatus()

        # Initial state
        assert status.total_count == 0

        # Report skipped test
        status.report_skipped("test prompt")
        assert status.total_count == 1

        # Report another type of result to verify total_count continues incrementing
        status.report_breach("breach prompt", "breach response")
        assert status.total_count == 2
        assert status.skipped_count == 1
        assert status.breach_count == 1

    def test_report_skipped_custom_message(self):
        """Test report_skipped() with custom additional_info parameter."""
        status = TestStatus()

        # Test with default message
        status.report_skipped("prompt1")
        assert status.log[0].additional_info == "Test skipped"

        # Test with custom message
        custom_message = "Skipped due to missing API key"
        status.report_skipped("prompt2", custom_message)
        assert status.log[1].additional_info == custom_message

    def test_multiple_skipped_reports(self):
        """Test multiple skipped reports accumulate correctly."""
        status = TestStatus()

        # Report multiple skipped tests
        for i in range(5):
            status.report_skipped(f"prompt_{i}", f"Skip reason {i}")

        # Verify counts
        assert status.skipped_count == 5
        assert status.total_count == 5
        assert len(status.log) == 5

        # Verify all log entries
        for i, log_entry in enumerate(status.log):
            assert log_entry.prompt == f"prompt_{i}"
            assert log_entry.additional_info == f"Skip reason {i}"
            assert log_entry.response is None
            assert log_entry.success is False

    def test_str_method_includes_skipped_count(self):
        """Test __str__() method includes skipped_count in representation."""
        status = TestStatus()

        # Test with no skipped tests
        str_repr = str(status)
        assert "skipped_count=0" in str_repr

        # Add some skipped tests
        status.report_skipped("prompt1")
        status.report_skipped("prompt2")

        str_repr = str(status)
        assert "skipped_count=2" in str_repr
        assert "total_count=2" in str_repr

        # Verify full format
        expected_parts = [
            "TestStatus(",
            "breach_count=0",
            "resilient_count=0",
            "skipped_count=2",
            "total_count=2",
            "log:2 entries"
        ]
        for part in expected_parts:
            assert part in str_repr


class TestIsSkippedFunction:
    """Test class for isSkipped function from prompt_injection_fuzzer.py."""

    def test_is_skipped_only_skipped(self):
        """Test isSkipped returns True when only skipped_count > 0."""
        status = TestStatus()

        assert isSkipped(status) is False

        status.report_skipped("prompt1")
        assert isSkipped(status) is True

        status.report_skipped("prompt2")
        assert isSkipped(status) is True

    def test_is_skipped_with_breaches(self):
        """Test isSkipped returns False when has breaches."""
        status = TestStatus()

        status.report_skipped("skipped_prompt")
        status.report_breach("breach_prompt", "breach_response")

        assert isSkipped(status) is False
        assert status.skipped_count > 0
        assert status.breach_count > 0

    def test_is_skipped_with_resilient(self):
        """Test isSkipped returns False when has resilient count."""
        status = TestStatus()

        status.report_skipped("skipped_prompt")
        status.report_resilient("resilient_prompt", "resilient_response")

        assert isSkipped(status) is False
        assert status.skipped_count > 0
        assert status.resilient_count > 0

    def test_is_skipped_with_errors(self):
        """Test isSkipped returns False when has errors."""
        status = TestStatus()

        status.report_skipped("skipped_prompt")
        status.report_error("error_prompt", "Error occurred")

        assert isSkipped(status) is False
        assert status.skipped_count > 0
        assert status.error_count > 0

    def test_is_skipped_mixed_results(self):
        """Test isSkipped returns False with mixed results."""
        status = TestStatus()

        status.report_skipped("skipped_prompt")
        status.report_breach("breach_prompt", "breach_response")
        status.report_resilient("resilient_prompt", "resilient_response")
        status.report_error("error_prompt", "Error occurred")

        assert isSkipped(status) is False
        assert status.skipped_count > 0
        assert status.breach_count > 0
        assert status.resilient_count > 0
        assert status.error_count > 0

    def test_is_skipped_no_results(self):
        """Test isSkipped returns False with no results."""
        status = TestStatus()

        assert isSkipped(status) is False
        assert status.skipped_count == 0
        assert status.breach_count == 0
        assert status.resilient_count == 0
        assert status.error_count == 0

    @pytest.mark.parametrize("breach_count,resilient_count,error_count,skipped_count,expected", [
        (0, 0, 0, 0, False),
        (0, 0, 0, 1, True),
        (0, 0, 0, 5, True),
        (1, 0, 0, 1, False),
        (0, 1, 0, 1, False),
        (0, 0, 1, 1, False),
        (1, 1, 1, 1, False),
        (2, 0, 0, 0, False),
        (0, 3, 0, 0, False),
        (0, 0, 4, 0, False),
    ])
    def test_is_skipped_parametrized(self, breach_count, resilient_count, error_count, skipped_count, expected):
        """Test isSkipped function with parametrized test status configurations."""
        status = TestStatus()

        status.breach_count = breach_count
        status.resilient_count = resilient_count
        status.error_count = error_count
        status.skipped_count = skipped_count

        assert isSkipped(status) is expected
