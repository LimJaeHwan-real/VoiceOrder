from __future__ import annotations

import json
from typing import Dict, List

from db import get_connection


def fetch_menus() -> List[Dict]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT id, name, price, image_url, category, tags, description FROM Menu ORDER BY id"
        ).fetchall()

    menus = []
    for row in rows:
        menu = dict(row)
        raw_tags = menu.get("tags") or "[]"
        try:
            menu["tags"] = json.loads(raw_tags)
        except json.JSONDecodeError:
            menu["tags"] = []
        menu["category"] = menu.get("category") or "coffee"
        menu["description"] = menu.get("description") or ""
        menus.append(menu)
    return menus
