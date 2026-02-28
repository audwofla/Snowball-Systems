import os
import psycopg2
from dotenv import load_dotenv

from src.crawling.discovery import discover_for_active_accounts

load_dotenv()

API_KEY = os.getenv("API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

def main():
    with psycopg2.connect(DATABASE_URL) as conn:
        discover_for_active_accounts(
            conn,
            region="americas",
            api_key=API_KEY,
            per_account_count=50,
            limit_accounts=25,   
            sleep_seconds=0.10,
        )

if __name__ == "__main__":
    main()