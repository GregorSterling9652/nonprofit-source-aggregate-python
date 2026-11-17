"""Application-shaped entry point for one nonprofit collection run."""

import json
import os
from typing import Any, Dict, List

from infrai_client import InfraiClient
from nonprofit_aggregator import Nonprofit, choose_listing, make_source_payload


def collect(query: str, sources: List[str]) -> Dict[str, Any]:
    client = InfraiClient()
    queued = [client.queue_publish("nonprofit-sources", make_source_payload(url, query)) for url in sources]
    search = client.web_search(query)
    listings = [
        Nonprofit(item.get("title", ""), item.get("snippet", ""), item.get("url", ""))
        for item in search.get("data", {}).get("results", [])
    ]
    selected = choose_listing(listings, query)
    return {
        "query": query,
        "queued_sources": len(queued),
        "listings": [record.__dict__ for record in selected],
    }


def scrape_source(url: str) -> Dict[str, Any]:
    """Worker step: fetch one queued source without changing the selection rule."""
    return InfraiClient().web_scrape(url)


if __name__ == "__main__":
    query = os.environ.get("NONPROFIT_QUERY", "food access")
    sources = [item for item in os.environ.get("NONPROFIT_SOURCES", "https://example.org").split(",") if item]
    print(json.dumps(collect(query, sources), indent=2))
