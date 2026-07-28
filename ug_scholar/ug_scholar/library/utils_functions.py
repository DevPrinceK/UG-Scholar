import csv
import re
from pathlib import Path
from types import SimpleNamespace

from accounts.models import UserLog
from api.providers.serpapi import SerpApiProvider


def get_author_ids(csv_file=None) -> list:
    """Extract Scholar IDs and local metadata from a CSV upload."""

    if csv_file is None:
        csv_path = Path(__file__).with_name("one-100.csv")
        raw = csv_path.read_bytes()
    else:
        raw = csv_file.read() if hasattr(csv_file, "read") else csv_file
    if isinstance(raw, str):
        text = raw
    else:
        for encoding in ("utf-8-sig", "cp1252", "latin1"):
            try:
                text = raw.decode(encoding)
                break
            except UnicodeDecodeError:
                continue

    reader = csv.DictReader(text.splitlines())
    required = {"scholar", "email", "college", "school", "department", "rank"}
    missing = required.difference(reader.fieldnames or [])
    if missing:
        raise ValueError(f"CSV is missing required columns: {', '.join(sorted(missing))}")

    author_relevant_info = []
    for record in reader:
        match = re.search(r'user=([\w-]+)', str(record["scholar"]))
        raw_id = (record.get("scholar") or "").strip()
        author_id = match.group(1) if match else raw_id
        if not re.fullmatch(r"[\w-]+", author_id):
            continue
        author_relevant_info.append(
            {
                "author_id": author_id,
                "email": (record.get("email") or "").strip(),
                "college": (record.get("college") or "").strip(),
                "school": (record.get("school") or "").strip(),
                "department": (record.get("department") or "").strip(),
                "rank": (record.get("rank") or "").strip(),
                "name": (record.get("name") or "").strip() or None,
            }
        )
    return author_relevant_info



def scrape_author_data(author_id: str = "Tpwr9vwAAAAJ") -> dict:
    """Backward-compatible SerpAPI adapter used by legacy callers."""

    profile = SimpleNamespace(
        scholar_id=author_id,
        source_author_id=author_id,
        data_source="google_scholar",
        orcid=None,
    )
    return SerpApiProvider().fetch_author(profile)



def log_user_action(user, action):
    '''logs user actions'''
    UserLog.objects.create(user=user, action=action)
    return True
