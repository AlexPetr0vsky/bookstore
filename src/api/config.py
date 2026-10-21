import os
from dotenv import load_dotenv

load_dotenv()


class APIConfig:
    BASE_URL = os.getenv("BASE_URL", "http://localhost:5001")
    API_URL = os.getenv("API_URL", f"{BASE_URL}/api")
    TIMEOUT = int(os.getenv("TIMEOUT", 30))
    HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"


api_config = APIConfig()
