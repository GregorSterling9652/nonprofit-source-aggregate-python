import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from nonprofit_aggregator import Nonprofit, choose_listing


def test_listing_selection_keeps_food_access_missions():
    records = [
        Nonprofit("Harbor Pantry", "food access for families", "https://harbor.example"),
        Nonprofit("River Arts", "free public workshops", "https://river.example"),
    ]

    result = choose_listing(records, "FOOD ACCESS")

    assert [record.name for record in result] == ["Harbor Pantry"]

