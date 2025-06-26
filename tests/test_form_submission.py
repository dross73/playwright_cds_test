# Temporary change to test pull request workflow
# This test file is auto-discovered and run by pytest
# It uses built-in `assert` statements and helper functions from your main code
import sys
import os

# Add the parent directory to sys.path so imports work when running pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import your existing helpers
from discover_fields import make_test_data  # Generate a test data object
from discover_fields import run_test  # Handles field detection and form submission


# Basic smoke test for a working US form submission
def test_us_form_submission() -> None:
    # Examples test URL - working US test page.
    test_url = "https://admin.buysub.com/servlet/OrdersGateway?cds_mag_code=CSI&cds_page_id=283316"

    # Use helper to generate valid US test data (non-gift)
    test_data = make_test_data(region="US", is_gift_page=False)

    # Run your existing form logic — right now this function doesn't return anything meaningful
    result = run_test(test_url, test_data)

    # Assert that the test succeeded
    assert result is True, "Form submission failed - expected success"  # nosec
