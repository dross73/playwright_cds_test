# BaseModel is the core class that lets us define data models with validation.
from pydantic import BaseModel

# Field is used to add validation rules (like regex) and metadata to model fields.
from pydantic import Field

# Option[X] mean the field can either be type X or None (i.e. it's not required).
from typing import Optional

import json  # Used for pretty-printing model data


# Define a base address structure using Pydantic
# This will be reused for both the buyer and the donee (gift recipient).
class Address(BaseModel):
    name: str
    address1: str
    city: str
    state: Optional[str] = None
    zip: Optional[str] = None
    postal: Optional[str] = None
    country: Optional[str] = "US"


# Main test data container for a single form submission test.
class TestData(BaseModel):
    region: str = Field(..., pattern="^(US|CAN|INTL)$")  # Must be one of: US, CAN, or INTL
    term_index: int = 0  # Dropdown index for term/value (defaults to 0)
    buyer: Address
    donee: Optional[Address] = None  # Gift recipient info, only used on gift pages


# These example test cases are not used in automation but are kept as templates
# for how TestData is structured, useful for debugging, documentation, or future tests.
# Create an example US test case using the TestData model.
us_test = TestData(
    region="US",
    term_index=0,
    buyer=Address(
        name="John Doe",
        address1="123 Main St",
        city="Des Moines",
        state="IA",
        zip="50309",
    ),
)


# Create an example Canada test case.
can_test = TestData(
    region="CAN",
    term_index=1,
    buyer=Address(
        name="Sarah Maple",
        address1="456 Maple Rd",
        city="Toronto",
        state="ON",  # Province — required for CAN
        zip="M5H 2N2",  # Some Canadian forms may use 'zip' or 'postal'
        country="CA",
    ),
)

# Create an example International test case.
intl_test = TestData(
    region="INTL",
    term_index=2,
    buyer=Address(
        name="Alex Müller",
        address1="789 Europa Strasse",
        city="Berlin",
        postal="10115",  # Postal code used for INTL instead of zip
        country="DE",
    ),
)

# Create an example gift test case (US region).
gift_test = TestData(
    region="US",
    term_index=0,
    buyer=Address(
        name="Buyer Person",
        address1="123 Buyer St",
        city="Chicago",
        state="IL",
        zip="60601",
    ),
    donee=Address(
        name="Gift Recipient",
        address1="789 Gift Ave",
        city="Springfield",
        state="IL",
        zip="62704",
    ),
)


# Dump the gift test case as a plain Python dictionary.
gift_dict = gift_test.model_dump()

# Print them out to verify structure
print(json.dumps(us_test.model_dump(), indent=4))
print(json.dumps(can_test.model_dump(), indent=4))
print(json.dumps(intl_test.model_dump(), indent=4))
print(json.dumps(gift_test.model_dump(), indent=4))
