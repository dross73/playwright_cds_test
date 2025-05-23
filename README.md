# Playwright Form Testing Tool

## Purpose
This tool automates testing of magazine subscription/order forms across multiple page types and regions (US, CAN, INTL). It fills in forms based on field detection and logs whether submissions succeed. This saves QC teams time and reduces manual test effort.

## How It Works

### 1. Launching the Tool
When you run the script:

```bash
python discover_fields.py
```

- It opens a **Tkinter GUI** (via `gui.py`)
- It collects:
  - A list of **page URLs** (one per line)
  - Region to test (**US**, **CAN**, **INTL**, or **ALL**) *(currently overridden internally to always test all regions)*
  - Other config data (payment type is currently collected but unused)

### 2. Processing Each URL
For each URL:
- The page is opened with **Playwright**
- For each region (`US`, `CAN`, `INTL`):
  - It checks if the region is supported:
    - Uses `<select name="cds_country">` when available
    - Falls back to `<input name="cds_country">` if the dropdown is absent
    - INTL support is only skipped if **no countries besides US and CAN are present**
  - If the region is supported:
    - It fills out the form fields
    - Attempts to submit using one term at a time (`cds_term_value` inputs)
    - Logs success or errors (e.g., “country mismatch” errors trigger a retry with the next term)

## 3. Form Filling Logic
For supported regions:
- Fills **buyer name/address/email**
- Selects region-specific address fields:
  - **US/CAN**: fills `cds_zip`, selects `cds_state`
  - **INTL**: fills `cds_postal`, sets dummy state if required
- Selects and fills the first available **term** (`cds_term_value`)
- Fills **credit card data** using test values:
  - Card: `4111111111111111`
  - Exp: `02/29`
- Submits the form
- If applicable, fills **gift recipient ("donee") fields** using realistic values (only when detected)

## Log Output
All results are written to:

```
logs/field_log.txt
```

The log includes:
- URL tested
- Region attempted
- Whether submission was successful or skipped
- Any errors encountered
- Term retry attempts (and reasons for skipping a term)

## File Structure
```
discover_fields.py      # Main script
gui.py                  # Tkinter interface for user input
.vscode/settings.json   # (Optional) VS Code interpreter config
.venv/                  # Project-specific virtual environment
logs/field_log.txt      # Generated test logs
```

## Supported Features
- Multi-region support (US, CAN, INTL)
- Region auto-skipping based on form field content
- Postal/ZIP and address detection based on country
- Gift form support (donee logic only triggered when gift fields are present)
- Multiple term option retries if one fails
- Clean output logs for each run
- Modular, future-proofed structure (e.g., payment type input can be wired in later)
