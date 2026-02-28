import time
from typing import Iterable
import requests

ARAM_QUEUE_ID = 450


class RiotRateLimit(Exception):
    pass


def _get_with_backoff(url, headers, params: dict | None = None, timeout: int = 20) -> requests.Response:
    r = requests.get(url, headers=headers, params=params, timeout=timeout)

    if r.status_code == 429:
        retry_after = int(r.headers.get("Retry-After", "2"))
        time.sleep(max(retry_after + 1, 1))
        raise RiotRateLimit("429 Rate limited")

    r.raise_for_status()
    return r


def fetch_aram_matches_for_puuid(
    region: str,
    api_key: str,
    puuid: str,
    *,
    count: int = 100,
) -> list[str]:
    headers = {"X-Riot-Token": api_key}
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    params = {"queue": ARAM_QUEUE_ID, "count": count}

    for _ in range(5):
        try:
            r = _get_with_backoff(url, headers, params)
            return r.json()
        except RiotRateLimit:
            continue

    r = _get_with_backoff(url, headers, params)
    return r.json()


def enqueue_match_ids(conn, match_ids: Iterable[str], discovered_from_puuid_str: str) -> int:
    inserted = 0
    with conn.cursor() as cur:
        for match_id in match_ids:
            cur.execute(
                """
                INSERT INTO match_queue (match_id, discovered_from_puuid)
                VALUES (%s, %s)
                ON CONFLICT (match_id) DO NOTHING
                """,
                (match_id, discovered_from_puuid_str),
            )
            if cur.rowcount > 0:
                inserted += 1
        conn.commit()
    return inserted


def discover_for_active_accounts(
    conn,
    *,
    region: str,
    api_key: str,
    per_account_count: int = 50,
    limit_accounts: int | None = 5,
    sleep_seconds: float = 0.10,
) -> None:

    with conn.cursor() as cur:
        if limit_accounts is None:
            cur.execute(
                """
                SELECT puuid
                FROM accounts
                WHERE status = 'active'
                ORDER BY last_crawled NULLS FIRST, random();
                """
            )
        else:
            cur.execute(
                """
                SELECT puuid
                FROM accounts
                WHERE status = 'active'
                ORDER BY last_crawled NULLS FIRST, random()
                LIMIT %s;
                """,
                (limit_accounts,),
            )
        puuids = [row[0] for row in cur.fetchall()]

    for puuid in puuids:
        match_ids = fetch_aram_matches_for_puuid(
            region,
            api_key,
            puuid,
            count=per_account_count,
        )

        if not match_ids:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE accounts SET last_crawled = NOW() WHERE puuid = %s;",
                    (puuid,),
                )
            conn.commit()
            continue

        enqueue_match_ids(conn, match_ids, discovered_from_puuid_str=puuid)

        with conn.cursor() as cur:
            cur.execute(
                "UPDATE accounts SET last_crawled = NOW() WHERE puuid = %s;",
                (puuid,),
            )
        conn.commit()