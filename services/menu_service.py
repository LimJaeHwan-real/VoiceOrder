from __future__ import annotations

import json
from typing import Dict, List

from db import get_connection


def fetch_menus() -> List[Dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                name,
                price,
                image_url,
                category,
                tags,
                description,
                group_name,
                temperature,
                sort_order
            FROM Menu
            WHERE COALESCE(is_active, 1) = 1
            ORDER BY COALESCE(sort_order, 0), id
            """
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
        menu["group_name"] = menu.get("group_name") or menu["name"]
        menu["temperature"] = menu.get("temperature") or ""
        menu["sort_order"] = int(menu.get("sort_order") or 0)
        menus.append(menu)
    return menus
