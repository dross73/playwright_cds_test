import os  # Used for checking if the logs folder exists and creating it
from playwright.sync_api import sync_playwright  # Playwright's synchronous API
from gui import (
    get_user_input,
)  # Imports your GUI function to get test inputs from the user

country_map = {"US": "United States", "CAN": "Canada", "INTL": "United Kingdom"}

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

                for region in regions_to_try:
                    page.goto(url, timeout=5000)  # Reload page for each region

                    # Add a separator in the logs
                    log("\n" + "-" * 50)
                    log(f"\n--- Inspecting: {url} (Region: {region}) ---")
                    page.wait_for_selector(
                        "body", timeout=5000
                    )  # Make sure it's fully loaded

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
                        if region == "US" and "united states" not in normalized_options:
                            log(f"Skipping {url} - Region US not supported in dropdown")
                            continue
                        elif region == "CAN" and "canada" not in normalized_options:
                            log(
                                f"Skipping {url} - Region CAN not supported in dropdown"
                            )
                            continue
                        elif region == "INTL":
                            # For INTL testing, we want to ensure the dropdown includes *any* country besides US and CAN
                            # First, assume INTL is supported only if the dropdown has other country options
                            intl_supported = any(
                                c
                                for c in normalized_options
                                if c
                                not in [
                                    "united states",
                                    "canada",
                                    "",
                                ]  # Filters out US CAN and blank values
                            )
                            # If there are no other countries, skip testing INTL for this page
                            if not intl_supported:
                                log(
                                    f"Skipping {url} - Region INTL not supported (dropdown only includes US or CAN)"
                                )

                    else:
                        # No dropdown - look for hidden input (used for US or CAN only)
                        country_input = page.query_selector('input[name="cds_country"]')
                        if country_input:
                            value = country_input.get_attribute("value")
                            if value != country_map[region]:
                                log(
                                    f"Skipping {url} - Region {region} not supported (hidden input shows {value})"
                                )
                                continue

                    try:
                        fill_form(page, region)
                    except Exception as e:
                        log(
                            f"Error submitting form for region {region} at {page.url}: {e}"
                        )

            except Exception as e:
                log(f"Failed to inspect {url}: {e}")

        input("\n Press Enter to close the browser...")

        # Close browser when finished with all URLs
        browser.close()


def fill_form(page, region):
    page.wait_for_selector('[name="cds_term_value"]', timeout=5000)
    term_options = page.locator('[name="cds_term_value"]')
    term_count = term_options.count()

    # if no visible term options, continue anyway
    if term_count == 0:
        log("No visible term options found - continuing without checking one")
    else:
        # Define real city/state/zip/postal date based on region
        if region == "US":
            buyer_city = "Ames"
            buyer_state = "IA"
            buyer_zip = "50010"
        elif region == "CAN":
            buyer_city = "Toronto"
            buyer_state = "ON"
            buyer_zip = "M5H2N2"
        else:  # INTL
            buyer_city = "London"
            buyer_postal = "W1A1AA"
            buyer_state = "-"
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

                    # Fill out name and address
                    page.locator('[name="cds_name"]').fill("Dan Ross")
                    page.locator('[name="cds_address_1"]').fill("1234 Street")
                    page.locator('[name="cds_address_2"]').fill("Apt 28")  # optional
                    page.locator('[name="cds_city"]').fill(buyer_city)

                    # Select country before ZIP/postal (some fields only appear after country is selected)
                    if page.query_selector('select[name="cds_country"]'):
                        page.locator('select[name="cds_country"]').select_option(
                            country_map[region]
                        )

                        page.wait_for_timeout(
                            500
                        )  # Allow time for postal fields to appear

                    # Fill ZIP for US/CAN
                    if region in ["US", "CAN"]:
                        if page.query_selector('[name="cds_zip"]'):
                            page.locator('[name="cds_zip"]').fill(buyer_zip)
                        else:
                            log("Skipping page: ZIP field not found for US/CAN")
                            return  # Exit early if zip field is unexpectedly missing

                    # Zip/Postal
                    if region == "INTL":
                        if page.query_selector('[name="cds_postal"]'):
                            postal_field = page.locator(
                                'input[name="cds_postal"]:not([type="hidden"])'
                            )
                            if postal_field.count() == 0:
                                log(
                                    "Skipping page: INTL selected but no visible cds_postal field found"
                                )
                                return
                            postal_field.first.fill(buyer_postal)
                        else:
                            log(
                                "Skipping page: INTL selected but no cds_postal field found"
                            )
                            return  # Exit form fill early.

                    page.locator('[name="cds_email"]').fill("me@home.com")

                    # State/Province for buyer (only for US and CAN)
                    if region in ["US", "CAN"]:
                        if page.query_selector('select[name="cds_state"]'):
                            page.locator('select[name="cds_state"]').select_option(
                                buyer_state
                            )

                    # Fill in Credit card info
                    page.locator('[name="cds_pay_type"]').first.check()
                    page.locator('[name="cds_cc_number"]').fill("4111111111111111")
                    page.locator('select[name="cds_cc_exp_month"]').select_option("02")
                    page.locator('select[name="cds_cc_exp_year"]').select_option("29")

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
                    if (
                        "country" in error_text.lower()
                        and "match" in error_text.lower()
                    ):
                        continue  # Try the next term
                    else:
                        return  # Stop on unrelated error
                else:
                    log(f"Submission successful for region {region}")
                    return  # Stop if successful

    # Gift (donee) fields - only fill if detected
    if page.query_selector('[name="cds_donee1_name"]'):
        if region == "US":
            donee_city = "Des Moines"
            donee_state = "IA"
            donee_zip = "50309"
        elif region == "CAN":
            donee_city = "Montreal"
            donee_state = "QC"
            donee_zip = "H2Y1C6"
        else:  # INTL
            donee_city = "Paris"
            donee_state = "-"
            donee_postal = "75001"
            donee_zip = ""

        # Fill donee info
        page.locator('[name="cds_donee1_name"]').fill("Don Rush")
        page.locator('[name="cds_donee1_address_1"]').fill("5678 Ave")
        page.locator('[name="cds_donee1_address_2"]').fill("Unit B")
        page.locator('[name="cds_donee1_city"]').fill(donee_city)

        # Select donee country (if dropdown exists)
        if page.query_selector('select[name="cds_donee1_country"]'):
            page.locator('select[name="cds_donee1_country"]').select_option(
                country_map[region]
            )
            page.wait_for_timeout(500)

            # Zip/Postal for donee
            if region == "INTL":
                if page.query_selector('[name="cds_donee1_postal"]'):
                    page.locator('[name="cds_donee1_postal"]').fill(donee_postal)
            else:
                if page.query_selector('[name="cds_donee1_zip"]'):
                    page.locator('[name="cds_donee1_zip"]').fill(donee_zip)

            page.locator('[name="cds_donee1_email"]').fill("donnie@home.com")

            # State/Province for donee
            page.locator('select[name="cds_donee1_state"]').select_option(donee_state)

        # Log failure if none of the term options worked


# This runs when the script is launched directly
if __name__ == "__main__":
    # Open the GUI and collect URLs + test options
    user_input = get_user_input()

    # Run the inspection process on the collected URLs
    run_discovery(user_input)
