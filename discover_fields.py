# Used for checking if the logs folder exists and creating it
import os

# sync_playwright launches the browser; Page represents a single browser tab
from playwright.sync_api import (
    sync_playwright,
    Page,
)

# For specifying user_input as a dictionary with string keys and any type of values
from typing import (
    Dict,
    Any,
)

# Import the TestData model and Address class used to structure form input.
# These Pydantic models ensure all test data is well-defined and validated before use.
from test_data import TestData, Address

# Import credit card test values from config.py.
# These are stored separately from the main code to keep sensitive data organized and secure.
from config import CREDIT_CARD_NUMBER, CC_EXP_MONTH, CC_EXP_YEAR, CC_CVV

# Imports your GUI function to get test inputs from the user
from gui import (
    get_user_input,
)

# For structured logging to file and console
import logging

logging.basicConfig(
    filename="logs/field_log.txt",  # Log file path
    level=logging.INFO,  # Log messages at INFO level and above
    format="%(asctime)s - %(levelname)s - %(message)s",  # Timestamp, level, message
    filemode="w",  # Overwrite log file each run (or change to "a" to append)
)


# Immutable sets of country names for region sets.
US_COUNTRIES = frozenset(["united states"])
CAN_COUNTRIES = frozenset(["canada"])
# Not currently used. Reserved in case we need to explicitly check INTL countries later.
INTL_COUNTRIES = frozenset(["united kingdom"])


# Helper to map region code to full country name
def get_country_name(region: str) -> str:
    if region == "US":
        return "United States"
    elif region == "CAN":
        return "Canada"
    else:
        return "United Kingdom"


# Ensure the log folder exists
os.makedirs("logs", exist_ok=True)


""" # This function inspects a single page and logs its form elements
def inspect_page(page: Page, url: str) -> None:
    log(f"\n--- Inspecting: {url} ---")  # Start of a new URL block in the log

    # Navigate to the URL. Timeout is 15 seconds (15000 ms)
    page.goto(url, timeout=15000)

    # Check if the page has a gift recipient field
    has_gift_fields = page.query_selector('[name="cds_donee1_name"]') is not None

    # Wait for the body tag to make sure the page has loaded
    page.wait_for_selector("body", timeout=5000)

    # Find all the input fields on the page and log their type, name, and ID
    for el in page.query_selector_all("input"):
        el_type = (
            el.get_attribute("type") or "text"
        )  # Default to text if type is missing
        el_name = el.get_attribute("name")
        el_id = el.get_attribute("id")
        # log(f"Input - type: {el_type}, name: {el_name}, id: {el_id}")

    # Find all <select> dropdowns and log their name and ID
    for el in page.query_selector_all("select"):
        el_name = el.get_attribute("name")
        el_id = el.get_attribute("id")
        # log(f"Select - name: {el_name}, id: {el_id}")

    # Find all <textarea> fields and log their name and ID
    for el in page.query_selector_all("textarea"):
        el_name = el.get_attribute("name")
        el_id = el.get_attribute("id")
        # log(f"Textarea - name : {el_name}, id: {el_id}")

    # Find all <button> tags and <input type="submit"> elements (form submitters)
    for el in page.query_selector_all("button, input[type=submit]"):
        tag = el.evaluate("el => el.tagName.toLowerCase()")

        try:
            # For buttons, try to get visible text; for inputs, get the value
            if tag == "button":
                label = el.inner_text()
            else:
                label = el.get_attribute("value") or ""
        except Exception:
            label = "[unreadable]"

        # log(f"Button - tag: {tag}, label: {label}")

    return """


def make_test_data(region: str, is_gift_page: bool) -> TestData:
    if region == "US":
        return TestData(
            region="US",
            term_index=0,
            buyer=Address(
                name="Dan Ross",
                address1="1234 Street",
                city="Ames",
                state="IA",
                zip="50010",
                country="United States",
                email="me@home.com",
            ),
            donee=(
                Address(
                    name="Don Rush",
                    address1="5678 Ave",
                    city="Des Moines",
                    state="IA",
                    zip="50309",
                    country="United States",
                    email="me@home.com",
                )
                if is_gift_page
                else None
            ),
        )
    elif region == "CAN":
        return TestData(
            region="CAN",
            term_index=0,
            buyer=Address(
                name="Dan Ross",
                address1="1234 Street",
                city="Toronto",
                state="ON",
                zip="M5H2N2",
                country="Canada",
                email="me@home.com",
            ),
            donee=(
                Address(
                    name="Don Rush",
                    address1="5678 Ave",
                    city="Montreal",
                    state="QC",
                    zip="H2Y1C6",
                    country="Canada",
                    email="me@home.com",
                )
                if is_gift_page
                else None
            ),
        )
    elif region == "INTL":
        return TestData(
            region="INTL",
            term_index=0,
            buyer=Address(
                name="Dan Ross",
                address1="1234 Street",
                city="London",
                postal="W1A1AA",
                country="United Kingdom",
                email="me@home.com",
            ),
            donee=(
                Address(
                    name="Don Rush",
                    address1="5678 Ave",
                    city="Paris",
                    postal="75001",
                    country="France",
                    email="me@home.com",
                )
                if is_gift_page
                else None
            ),
        )
    else:
        raise ValueError(f"Unsupported region: {region}")


# This is the main loop that runs after collecting GUI input
def run_discovery(user_input: Dict[str, Any]) -> None:
    # Grab the list of URLs from the GUI return data
    urls = user_input["urls"]

    # Start Playwright and launch the browser (Chromium in visible mode)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Loop through each user-provided URL and inspect it
        for url in urls:
            try:
                # Determine if the page has gift fields
                regions_to_try = ["US", "CAN", "INTL"]
                region_status = {r: "Skipped" for r in regions_to_try}

                for region in regions_to_try:
                    page.goto(url, timeout=5000)  # Reload page for each region

                    # Add a separator in the logs
                    # Write a visual separator and header for this URL/region inspection
                    logging.info("\n" + "=" * 60)
                    logging.info(f"Inspecting: {url}")
                    logging.info(f"Region: {region}")

                    page.wait_for_selector("body", timeout=5000)  # Make sure it's fully loaded

                    # Check which regions the page supports based on the cds_country field
                    country_selector = page.query_selector('select[name="cds_country"]')
                    if country_selector:
                        # Page uses a dropdown - get all visible country options
                        options = [
                            opt.get_attribute("value")
                            for opt in country_selector.query_selector_all("option")
                        ]

                        # Normalize options to lowercase for comparison
                        normalized_options = [opt.lower() for opt in options if opt]

                        # Check if the current region is supported based on country presence
                        if region == "US" and not any(
                            opt in US_COUNTRIES for opt in normalized_options
                        ):
                            logging.warning(f"Skipping {url} - Region US not supported in dropdown")

                            continue
                        elif region == "CAN" and not any(
                            opt in CAN_COUNTRIES for opt in normalized_options
                        ):
                            logging.warning(
                                f"Skipping {url} - Region CAN not supported in dropdown"
                            )
                            continue
                        elif region == "INTL":
                            # For INTL testing, we want to ensure the dropdown includes *any* country besides US and CAN
                            # First, assume INTL is supported only if the dropdown has other country options
                            intl_supported = any(
                                opt not in US_COUNTRIES | CAN_COUNTRIES
                                for opt in normalized_options
                            )
                            # If there are no other countries, skip testing INTL for this page
                            if not intl_supported:
                                logging.warning(
                                    f"Skipping {url} - Region INTL not supported (dropdown only includes US or CAN)"
                                )
                                continue

                    else:
                        # No dropdown - look for hidden input (used for US or CAN only)
                        country_input = page.query_selector('input[name="cds_country"]')
                        if country_input:
                            value = country_input.get_attribute("value")
                            normalized = value.lower().strip() if value else ""

                            # Check region match using frozensets
                            if region == "US" and normalized not in US_COUNTRIES:
                                logging.warning(
                                    f"Skipping {url} - Region US not supported (hidden in put shows {value})"
                                )
                                continue
                            elif region == "CAN" and normalized not in CAN_COUNTRIES:
                                logging.warning(
                                    f"Skipping {url} - Region CAN not supported (hidden input shows {value})"
                                )
                                continue
                            elif region == "INTL" and normalized in US_COUNTRIES | CAN_COUNTRIES:
                                logging.warning(
                                    f"Skipping {url} - Region INTL not supported (hidden input shows {value})"
                                )
                                continue

                    try:
                        # This regions passed all checks and is being tested
                        region_status[region] = "Tested"

                        # Create a test data object for the current region
                        is_gift_page = (
                            True  # Always generate donee data; we'll decide later if it's used
                        )

                        test_data = make_test_data(region, is_gift_page)

                        # Pass the full model to fill_form
                        fill_form(page, test_data)

                    except Exception as e:
                        logging.error(
                            f"Error submitting form for region {region} at {page.url}: {e}"
                        )

                # After trying all regions, log a quick summary for this URL
                logging.info("Region summary for this URL:")
                for r, status in region_status.items():
                    logging.info(f"  {r}: {status}")

            except Exception as e:
                logging.error(f"Failed to inspect {url}: {e}")

        input("\n Press Enter to close the browser...")

        # Close browser when finished with all URLs
        browser.close()


def fill_form(page: Page, test_data: TestData) -> None:
    region = test_data.region
    # Try selecting both self and gift subscription terms (if present).
    # Some page may only have one or the other, or both.
    # This allows us to support self-only, and mixed pages.

    # Look for a standard self-subscription term radio button
    self_term = page.query_selector(
        'input[name="cds_term_value"]:not([disabled]):not([type="hidden"])'
    )
    if self_term:
        try:
            # Attempt to check the self-subscription radio button
            self_term.check(timeout=500)
            logging.info("Selected self-subscription term (cds_term_value)")

            logging.info("Selected self-subscription term (cds_term_value)")

            # Attempt to select a gift term checkbox if present
            gift_term_checkbox = page.query_selector('input[name="cds_donee1_term_value"]')
            if gift_term_checkbox:
                try:
                    gift_term_checkbox.check()
                    logging.info("Checked gift term checkbox (cds_donee1_term_value)")
                    page.wait_for_timeout(1000)  # Let UI reveal gift fields
                except Exception as e:
                    logging.warning(f"Failed to check gift term checkbox: {e}")

        except Exception as e:
            # If checking fails, log the error and continue
            logging.warning(f"Could not select the self-subscription term: {e}")

    # Attempt to select a gift subscription term — can be dropdown, checkbox, or radio input.
    # These usually follow the pattern: cds_donee1_term_value, cds_donee2_term_value, etc.
    gift_term_elements = page.query_selector_all(
        '[name^="cds_donee"][name$="_term_value"]:not([disabled]):not([type="hidden"])'
    )

    # Try each matching gift term until one can be selected
    for term in gift_term_elements:
        try:
            tag = term.evaluate("el => el.tagName.toLowerCase()")
            input_type = term.get_attribute("type") or ""

            if tag == "select":
                term.select_option(index=0)
                logging.info(f"Selected gift term from dropdown: {term.get_attribute('name')}")
                page.wait_for_timeout(500)
                break  # Stop after successful selection
            elif input_type in ["checkbox", "radio"]:
                term.check()
                logging.info(f"Checked gift term input: {term.get_attribute('name')}")
                page.wait_for_timeout(500)
                break  # Stop after successful selection
        except Exception as e:
            logging.warning(f"Could not select gift term ({term.get_attribute('name')}): {e}")

    # Fill out donee fields if test_data includes a gift recipient
    if test_data.donee:
        # Check that the donee name field is now visible before attempting to fill
        if page.query_selector('[name="cds_donee1_name"]'):
            donee = test_data.donee

            donee_name = page.locator('[name="cds_donee1_name"]')

            try:
                donee_name.wait_for(
                    state="visible", timeout=3000
                )  # Wait max 3 seconds for visibility
                donee_name.fill(donee.name, timeout=1000)  # Timeout after 1 second if not editable
            except Exception:
                logging.warning("Gift name field never became visible — skipping donee fill")
                return

            page.locator('[name="cds_donee1_address_1"]').fill(donee.address1)
            page.locator('[name="cds_donee1_address_2"]').fill("Unit 7")  # optional
            page.locator('[name="cds_donee1_city"]').fill(donee.city)

            # For CAN/US use cds_donee1_zip, for INTL use cds_donee1_postal
            if region in ["US", "CAN"] and donee.zip:
                if page.query_selector('[name="cds_donee1_zip"]'):
                    page.locator('[name="cds_donee1_zip"]').fill(donee.zip)
                else:
                    logging.warning("Donee ZIP field not found — skipping ZIP for donee")

            if region == "INTL" and donee.postal:
                if page.query_selector('[name="cds_donee1_postal"]'):
                    page.locator('[name="cds_donee1_postal"]').fill(donee.postal)
                else:
                    logging.warning("Donee POSTAL field not found — skipping postal for donee")

            if donee.email and page.query_selector('[name="cds_donee1_email"]'):
                page.locator('[name="cds_donee1_email"]').fill(donee.email)
            else:
                logging.info("Skipping donee email: not found or not provided")
            # Select donee country if dropdown exists
            if page.query_selector('select[name="cds_donee1_country"]') and donee.country:
                try:
                    gift_country_dropdown = page.locator('select[name="cds_donee1_country"]')

                    # Wait until the dropdown is visible
                    page.wait_for_selector(
                        'select[name="cds_donee1_country"]', state="visible", timeout=3000
                    )
                    page.wait_for_timeout(500)  # Give time for animation to fully complete

                    # Wait up to 2 seconds total for options to appear
                    for _ in range(10):
                        options = gift_country_dropdown.locator("option").all()
                        if len(options) > 1:
                            break
                        page.wait_for_timeout(200)
                    else:
                        logging.warning("Gift country dropdown never populated with options")

                    gift_country_dropdown.select_option(donee.country)
                    logging.info(f"Selected donee country: {donee.country}")

                except Exception as e:
                    logging.warning(f"Failed to select donee country: {e}")

            # Set state if it's a US/CAN region and dropdown exists
            if region in ["US", "CAN"] and donee.state:
                try:
                    donee_state_dropdown = page.locator('select[name="cds_donee1_state"]')
                    donee_state_dropdown.wait_for(state="visible", timeout=1000)

                    # Get all option values once
                    values = [
                        opt.get_attribute("value")
                        for opt in donee_state_dropdown.locator("option").all()
                    ]
                    if not any(val and val.upper() == donee.state for val in values):
                        logging.warning(
                            f"Donee state '{donee.state}' not found in dropdown — skipping"
                        )
                        return

                    donee_state_dropdown.select_option(donee.state)
                except Exception:
                    logging.warning("Skipping donee state: not visible or not selectable")

            logging.info("Filled donee (gift recipient) fields")
        else:
            logging.info("Gift form not visible — skipping donee field fill")

    # Fill out buyer name and address using test_data
    buyer = test_data.buyer
    page.locator('[name="cds_name"]').fill(buyer.name)
    page.locator('[name="cds_address_1"]').fill(buyer.address1)
    page.locator('[name="cds_address_2"]').fill("Apt 28")  # optional
    page.locator('[name="cds_city"]').fill(buyer.city)

    # Select country before ZIP/postal (some fields only appear after country is selected)
    if page.query_selector('select[name="cds_country"]') and buyer.country:
        page.locator('select[name="cds_country"]').select_option(buyer.country)

        page.wait_for_timeout(500)  # Allow time for postal fields to appear

    # Fill ZIP for US/CAN
    if region in ["US", "CAN"] and buyer.zip:
        if page.query_selector('[name="cds_zip"]'):
            page.locator('[name="cds_zip"]').fill(buyer.zip)
        else:
            logging.warning("Skipping page: ZIP field not found for US/CAN")
            return  # Exit early if zip field is unexpectedly missing

    # Zip/Postal
    if region == "INTL" and buyer.postal:
        if page.query_selector('[name="cds_postal"]'):
            postal_field = page.locator('input[name="cds_postal"]:not([type="hidden"])')
            if postal_field.count() == 0:
                logging.warning(
                    "Skipping page: INTL selected but no visible cds_postal field found"
                )
                return
            postal_field.first.fill(buyer.postal)
        else:
            logging.warning("Skipping page: INTL selected but no cds_postal field found")
            return  # Exit form fill early.

    page.locator('[name="cds_email"]').fill(buyer.email)

    # State/Province for buyer (only for US and CAN)
    if region in ["US", "CAN"] and buyer.state:
        try:
            buyer_state_dropdown = page.locator('select[name="cds_state"]')
            buyer_state_dropdown.wait_for(state="visible", timeout=1000)

            values = [
                opt.get_attribute("value") for opt in buyer_state_dropdown.locator("option").all()
            ]
            if not any(val and val.upper() == buyer.state for val in values):
                logging.warning(f"Buyer state '{buyer.state}' not found in dropdown — skipping")
                return

            buyer_state_dropdown.select_option(buyer.state)
        except Exception:
            logging.warning("Skipping buyer state: not visible or not selectable")

    # Fill in Credit card info
    # Handle payment method: dropdown or radio
    pay_type_selector = page.query_selector('[name="cds_pay_type"]')
    if pay_type_selector:
        tag = pay_type_selector.evaluate("el => el.tagName.toLowerCase()")

        if tag == "select":
            try:
                pay_type_selector.select_option("2")  # Visa
                logging.info("Selected payment type from dropdown: Visa (2)")
            except Exception as e:
                logging.warning(f"Failed to select Visa from payment dropdown: {e}")  # nosec B608: false positive, not SQL

        elif tag == "input":
            try:
                radios = page.locator('[name="cds_pay_type"]')
                checked_radio = radios.locator(":checked")

                if checked_radio.count() > 0:
                    logging.info("Payment radio already selected — skipping selection")
                else:
                    visa_radio = page.query_selector('[name="cds_pay_type"][value="2"]')
                    if visa_radio:
                        visa_radio.check()
                        logging.info("Checked Visa radio button (value=2)")
                    else:
                        radios.first.check()
                        logging.info("Checked first available payment radio as fallback")
            except Exception as e:
                logging.warning(f"Failed to handle payment radio buttons: {e}")

        else:
            logging.warning(f"cds_pay_type tag not supported: {tag}")

    else:
        logging.warning("cds_pay_type not found on page")

    page.locator('[name="cds_cc_number"]').fill(CREDIT_CARD_NUMBER)

    page.locator('select[name="cds_cc_exp_month"]').select_option(CC_EXP_MONTH)
    page.locator('select[name="cds_cc_exp_year"]').select_option(CC_EXP_YEAR)

    # Fill CVV if the field exists
    if page.query_selector('[name="cds_cc_security_code"]'):
        page.locator('[name="cds_cc_security_code"]').fill(CC_CVV)
    else:
        logging.warning("Skipping CVV: cds_cc_security_code not found on page")

    # Log the region just before submission
    logging.info(f"Submitting form for region {region} at URL: {page.url}")

    # Click the order button
    page.locator('[name="send"]').click()

    # Wait a few seconds to observe confirmation page
    page.wait_for_timeout(3000)  # waits 3 seconds

    # Check for error messages after submission
    if page.query_selector(".error"):
        error_text = page.locator(".error").inner_text()
        logging.error(f"Submission error detected for region {region}: {error_text}")
        if "country" in error_text.lower() and "match" in error_text.lower():
            return  # Try the next term
        else:
            return  # Stop on unrelated error
    else:
        logging.info(f"Submission successful for region {region}")
        return  # Stop if successful


def run_test(url: str, test_data: TestData) -> bool:
    """
    Entry point for pytest to run a single form submission test.
    Uses Playwright to submit the form using provided test data.
    Returns True if submission appears successful, False otherwise.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(url, timeout=10000)

            fill_form(page, test_data)

            # Very basic success check — customize later if needed
            if page.url != url:
                return True
            else:
                return False
    except Exception as e:
        print(f"run_test() failed: {e}")
        return False


# This runs when the script is launched directly
if __name__ == "__main__":
    # Open the GUI and collect URLs + test options
    user_input = get_user_input()

    # Run the inspection process on the collected URLs
    run_discovery(user_input)
