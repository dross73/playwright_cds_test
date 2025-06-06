# Config values are centralized here for easy reuse across the project.
# Sensitive values should be loaded from a .env file (not committed) and accessed via this module,
# keeping business logic clean and secure.
import os
from dotenv import load_dotenv
# Required: will raise KeyError if missing

# Load .env files contents into environment
load_dotenv()

# These are pulled from the .env file
CREDIT_CARD_NUMBER = os.environ["CREDIT_CARD_NUMBER"]
CC_EXP_MONTH = os.environ["CC_EXP_MONTH"]
CC_EXP_YEAR = os.environ["CC_EXP_YEAR"]
CC_CVV = os.environ["CC_CVV"]
