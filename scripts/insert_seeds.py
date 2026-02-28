import json
import psycopg2
import os
from dotenv import load_dotenv
from src.config.paths import DATA_DIR

load_dotenv()
DATABASE_URL = os.environ["DATABASE_URL"]

with open(DATA_DIR / "aram_seeds.json") as f:
    seeds = json.load(f)

puuids = seeds["puuids"]

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

for puuid in puuids:
    cur.execute(
        """
        INSERT INTO accounts (puuid, status, depth)
        VALUES (%s, 'active', 0)
        ON CONFLICT (puuid) DO UPDATE
        SET status = 'active',
            depth = 0;
        """,
        (puuid,),
    )
conn.commit()
cur.close()
conn.close()