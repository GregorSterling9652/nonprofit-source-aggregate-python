"""Aggregate nonprofit source pages into a small, testable service."""

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List


@dataclass(frozen=True)
class Nonprofit:
    name: str
    mission: str
    source_url: str


def choose_listing(records: Iterable[Nonprofit], query: str) -> List[Nonprofit]:
    """Keep records that contain the requested topic in name or mission."""
    needle = query.casefold().strip()
    return [
        record
        for record in records
        if needle in record.name.casefold() or needle in record.mission.casefold()
    ]


def make_source_payload(url: str, query: str) -> Dict[str, str]:
    return {"url": url, "query": query}

