import os
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.getenv("https://api.imd.gov.in/api/v1/cityforecast")