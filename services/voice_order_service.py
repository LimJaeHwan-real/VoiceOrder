from __future__ import annotations

import re
from typing import Dict, List

KOREAN_NUMBER_MAP = {
    "열두": 12,
    "열한": 11,
    "열": 10,
    "아홉": 9,
    "여덟": 8,
    "일곱": 7,
    "여섯": 6,
    "다섯": 5,
    "네": 4,
    "세": 3,
    "두": 2,
    "한": 1,
    "하나": 1,
    "둘": 2,
    "셋": 3,
    "넷": 4,
}

MENU_SYNONYMS = {
    "아이스 아메리카노": ["아메리카노", "아아", "아이스아메리카노"],
    "카페라떼": ["라떼", "카페 라떼"],
    "딸기 스무디": ["스무디", "딸기스무디"],
    "초코 케이크": ["케이크", "초코케이크"],
    "블루베리 머핀": ["머핀", "블루베리머핀"],
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", "", text.lower())


def menu_aliases(menu_name: str) -> List[str]:
    aliases = {menu_name, menu_name.replace(" ", "")}
    aliases.update(MENU_SYNONYMS.get(menu_name, []))
    return sorted({normalize_text(alias) for alias in aliases}, key=len, reverse=True)


def extract_quantity(snippet: str) -> int:
    digit_match = re.search(r"(\d+)\s*(잔|개|컵)?", snippet)
    if digit_match:
        return max(1, int(digit_match.group(1)))

    for word, value in sorted(
        KOREAN_NUMBER_MAP.items(), key=lambda item: len(item[0]), reverse=True
    ):
        if word in snippet:
            return value
    return 1


def parse_voice_order(text: str, menus: List[Dict]) -> List[Dict]:
    compact_text = normalize_text(text)
    matches: List[Dict] = []

    for menu in menus:
        alias_hit = None
        hit_index = -1

        for alias in menu_aliases(menu["name"]):
            hit_index = compact_text.find(alias)
            if hit_index >= 0:
                alias_hit = alias
                break

        if alias_hit is None:
            continue

        window_start = max(0, hit_index - 6)
        window_end = min(len(compact_text), hit_index + len(alias_hit) + 12)
        context = compact_text[window_start:window_end]
        quantity = extract_quantity(context)

        matches.append(
            {
                "menu_id": menu["id"],
                "name": menu["name"],
                "price": menu["price"],
                "quantity": quantity,
                "subtotal": menu["price"] * quantity,
            }
        )

    deduped: Dict[int, Dict] = {}
    for item in matches:
        existing = deduped.get(item["menu_id"])
        if existing:
            existing["quantity"] += item["quantity"]
            existing["subtotal"] = existing["price"] * existing["quantity"]
        else:
            deduped[item["menu_id"]] = item

    return list(deduped.values())
