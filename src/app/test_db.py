import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv('POSTGRES_DATABASE_URL')
print(DATABASE_URL)