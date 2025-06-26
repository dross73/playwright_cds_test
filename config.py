# Config values are centralized here for easy reuse across the project.
# Sensitive values should be loaded from a .env file (not committed) and accessed via this module,
# keeping business logic clean and secure.
import os
from dotenv import load_dotenv
# Required: will raise KeyError if missing

# Load .env files contents into environment
load_dotenv()

# These are pulled from the .env file
CREDIT_CARD_NUMBER = os.getenv("CREDIT_CARD_NUMBER", "4111111111111111")
CC_EXP_MONTH = os.getenv("CC_EXP_MONTH", "12")
CC_EXP_YEAR = os.getenv("CC_EXP_YEAR", "2030")
CC_CVV = os.getenv("CC_CVV", "123")
