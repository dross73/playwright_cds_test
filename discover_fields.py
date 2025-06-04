import os  # Used for checking if the logs folder exists and creating it
from playwright.sync_api import sync_playwright  # Playwright's synchronous API
from test_data import TestData, Address
from config import CREDIT_CARD_NUMBER, CC_EXP_MONTH, CC_EXP_YEAR, CC_CVV

from gui import (
    get_user_input,
)  # Imports your GUI function to get test inputs from the user


# Immutable sets of country names for region sets.
US_COUNTRIES = frozenset(["united states"])
CAN_COUNTRIES = frozenset(["canada"])
# Not currently used. Reserved in case we need to explicitly check INTL countries later.
INTL_COUNTRIES = frozenset(["united kingdom"])


# Helper to map region code to full country name
def get_country_name(region):
    return "United States" if region == "US" else "Canada" if region == "CAN" else "United Kingdom"


# This is the path where we'll store the inspection results
LOG_FILE = "logs/field_log.txt"

# Ensure the log folder exists
os.makedirs("logs", exist_ok=True)


# A helper function to write log entries to both the terminal and a file
def log(text):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")  # Write to file
    print(text)  # Also print to terminal


""" # This function inspects a single page and logs its form elements
def inspect_page(page, url):
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
            ),
            donee=(
                Address(
                    name="Don Rush",
                    address1="5678 Ave",
                    city="Des Moines",
                    state="IA",
                    zip="50309",
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
            ),
            donee=(
                Address(
                    name="Don Rush",
                    address1="5678 Ave",
                    city="Montreal",
                    state="QC",
                    zip="H2Y1C6",
                    country="Canada",
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
            ),
            donee=(
                Address(
                    name="Don Rush",
                    address1="5678 Ave",
                    city="Paris",
                    postal="75001",
                    country="France",
                )
                if is_gift_page
                else None
            ),
        )
    else:
        raise ValueError(f"Unsupported region: {region}")


# This is the main loop that runs after collecting GUI input
def run_discovery(user_input):
    # Grab the list of URLs from the GUI return data
    urls = user_input["urls"]

    # Clear out any old log files before running new tests
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

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
                    log("")
                    log("=" * 60)
                    log(f"Inspecting: {url}")
                    log(f"Region: {region}")

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
                            log(f"Skipping {url} - Region US not supported in dropdown")
                            continue
                        elif region == "CAN" and not any(
                            opt in CAN_COUNTRIES for opt in normalized_options
                        ):
                            log(f"Skipping {url} - Region CAN not supported in dropdown")
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
                                log(
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
                                log(
                                    f"Skipping {url} - Region US not supported (hidden in put shows {value})"
                                )
                                continue
                            elif region == "CAN" and normalized not in CAN_COUNTRIES:
                                log(
                                    f"Skipping {url} - Region CAN not supported (hidden input shows {value})"
                                )
                                continue
                            elif region == "INTL" and normalized in US_COUNTRIES | CAN_COUNTRIES:
                                log(
                                    f"Skipping {url} - Region INTL not supported (hidden input shows {value})"
                                )
                                continue

                    try:
                        # This regions passed all checks and is being tested
                        region_status[region] = "Tested"

                        # Create a test data object for the current region
                        is_gift_page = page.query_selector('[name="cds_donee1_name"]') is not None

                        test_data = make_test_data(region, is_gift_page)

                        # Pass the full model to fill_form
                        fill_form(page, test_data)

                    except Exception as e:
                        log(f"Error submitting form for region {region} at {page.url}: {e}")

                # After trying all regions, log a quick summary for this URL
                log("Region summary for this URL:")
                for r, status in region_status.items():
                    log(f"  {r}: {status}")

            except Exception as e:
                log(f"Failed to inspect {url}: {e}")

        input("\n Press Enter to close the browser...")

        # Close browser when finished with all URLs
        browser.close()


def fill_form(page, test_data):
    region = test_data.region
    page.wait_for_selector('[name="cds_term_value"]', timeout=5000)
    term_options = page.locator('[name="cds_term_value"]')
    term_count = term_options.count()

    # if no visible term options, continue anyway
    if term_count == 0:
        log("No visible term options found - continuing without checking one")
    else:
        # Find all visible and enabled cds_term_value inputs
        valid_terms = page.locator(
            'input[name="cds_term_value"]:not([disabled]):not([type="hidden"])'
        )
        term_count = valid_terms.count()

        # If there are no selectable terms, we'll try submitting anyway later
        if term_count == 0:
            log("No selectable offers found - proceeding without selecting one")
        else:
            for i in range(term_count):
                try:
                    option = valid_terms.nth(i)
                    option.check(timeout=500)
                    log(f"Tried selecting term index {i} for region {region}")

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
                            log("Skipping page: ZIP field not found for US/CAN")
                            return  # Exit early if zip field is unexpectedly missing

                    # Zip/Postal
                    if region == "INTL" and buyer.postal:
                        if page.query_selector('[name="cds_postal"]'):
                            postal_field = page.locator(
                                'input[name="cds_postal"]:not([type="hidden"])'
                            )
                            if postal_field.count() == 0:
                                log(
                                    "Skipping page: INTL selected but no visible cds_postal field found"
                                )
                                return
                            postal_field.first.fill(buyer.postal)
                        else:
                            log("Skipping page: INTL selected but no cds_postal field found")
                            return  # Exit form fill early.

                    page.locator('[name="cds_email"]').fill("me@home.com")

                    # State/Province for buyer (only for US and CAN)
                    if region in ["US", "CAN"] and buyer.state:
                        if page.query_selector('select[name="cds_state"]'):
                            page.locator('select[name="cds_state"]').select_option(buyer.state)

                    # Fill in Credit card info
                    page.locator('[name="cds_pay_type"]').first.check()
                    page.locator('[name="cds_cc_number"]').fill(CREDIT_CARD_NUMBER)

                    page.locator('select[name="cds_cc_exp_month"]').select_option(CC_EXP_MONTH)
                    page.locator('select[name="cds_cc_exp_year"]').select_option(CC_EXP_YEAR)

                    # Fill CVV if the field exists
                    if page.query_selector('[name="cds_cc_security_code"]'):
                        page.locator('[name="cds_cc)security_code"]').fill(CC_CVV)
                    else:
                        log("Skipping CVV: cds_cc_security_code not found on page")

                    # Log the region just before submission
                    log(f"Submitting form for region {region} at URL: {page.url}")

                    # Click the order button
                    page.locator('[name="send"]').click()

                    # Wait a few seconds to observe confirmation page
                    page.wait_for_timeout(3000)  # waits 3 seconds

                except Exception as e:
                    log(f"Skipping term index {i} : not checkable ({e})")
                    continue

                # Check for error messages after submission
                if page.query_selector(".error"):
                    error_text = page.locator(".error").inner_text()
                    log(f"Submission error detected for region {region}: {error_text}")
                    if "country" in error_text.lower() and "match" in error_text.lower():
                        continue  # Try the next term
                    else:
                        return  # Stop on unrelated error
                else:
                    log(f"Submission successful for region {region}")
                    return  # Stop if successful

    # Gift (donee) fields — only fill if detected and test_data includes a donee
    if test_data.donee and page.query_selector('[name="cds_donee1_name"]'):
        donee = test_data.donee

        page.locator('[name="cds_donee1_name"]').fill(donee.name)
        page.locator('[name="cds_donee1_address_1"]').fill(donee.address1)
        page.locator('[name="cds_donee1_address_2"]').fill("Unit B")  # optional for now
        page.locator('[name="cds_donee1_city"]').fill(donee.city)

        # Select donee country (if dropdown exists)
        if donee.country and page.query_selector('select[name="cds_donee1_country"]'):
            page.locator('select[name="cds_donee1_country"]').select_option(donee.country)
            page.wait_for_timeout(500)

        # Zip/Postal for donee
        if donee.postal and page.query_selector('[name="cds_donee1_postal"]'):
            page.locator('[name="cds_donee1_postal"]').fill(donee.postal)

        if donee.zip and page.query_selector('[name="cds_donee1_zip"]'):
            page.locator('[name="cds_donee1_zip"]').fill(donee.zip)

        # Email for donee (static placeholder for now)
        page.locator('[name="cds_donee1_email"]').fill("donnie@home.com")

        # State/Province for donee
        if donee.state and page.query_selector('select[name="cds_donee1_state"]'):
            page.locator('select[name="cds_donee1_state"]').select_option(donee.state)


# This runs when the script is launched directly
if __name__ == "__main__":
    # Open the GUI and collect URLs + test options
    user_input = get_user_input()

    # Run the inspection process on the collected URLs
    run_discovery(user_input)
