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
    "핫 아메리카노": ["뜨거운 아메리카노", "따뜻한 아메리카노", "뜨아", "핫아메리카노"],
    "카페라떼": ["라떼", "카페 라떼"],
    "바닐라라떼": ["바닐라 라떼", "바닐라라테"],
    "카라멜마키아또": ["카라멜 마키아또", "마키아또"],
    "딸기스무디": ["딸기 스무디", "스무디"],
    "자몽에이드": ["자몽 에이드", "에이드"],
    "생강차": ["생강 차", "진저티"],
    "초코케이크": ["초코 케이크", "케이크"],
    "햄치즈샌드위치": ["햄 치즈 샌드위치", "샌드위치"],
    "블루베리머핀": ["블루베리 머핀", "머핀"],
}

SEGMENT_SPLIT_PATTERN = re.compile(
    r"(?:이랑|랑|하고|하구|그리고|그리구|또|또는|이랑은|이랑요|이랑그거|,|/|\+|및)"
)


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


def split_voice_segments(text: str) -> List[str]:
    raw_segments = SEGMENT_SPLIT_PATTERN.split(text)
    segments = []
    for segment in raw_segments:
        cleaned = segment.strip(" ,.!?~")
        if cleaned:
            segments.append(cleaned)
    return segments or [text.strip()]


def find_order_candidates(text: str, menus: List[Dict]) -> List[Dict]:
    compact_text = normalize_text(text)
    candidates = []

    for menu in menus:
        for alias in menu_aliases(menu["name"]):
            hit_index = compact_text.find(alias)
            if hit_index >= 0:
                candidates.append(
                    {
                        "menu": menu,
                        "alias": alias,
                        "start": hit_index,
                        "end": hit_index + len(alias),
                    }
                )
                break

    candidates.sort(key=lambda item: (-(item["end"] - item["start"]), item["start"]))

    accepted = []
    for candidate in candidates:
        overlaps = any(
            not (candidate["end"] <= existing["start"] or candidate["start"] >= existing["end"])
            for existing in accepted
        )
        if not overlaps:
            accepted.append(candidate)

    return accepted


def extract_unmatched_text(text: str, matches: List[Dict]) -> str:
    compact_text = normalize_text(text)
    if not matches:
        return text.strip()

    consumed = [False] * len(compact_text)
    for match in matches:
        for index in range(match["start"], match["end"]):
            if 0 <= index < len(consumed):
                consumed[index] = True

    remaining = "".join(
        compact_text[index]
        for index in range(len(compact_text))
        if not consumed[index]
    )
    return remaining.strip()


def parse_voice_order_result(text: str, menus: List[Dict]) -> Dict:
    matches: List[Dict] = []
    unmatched_segments: List[str] = []

    for segment in split_voice_segments(text):
        accepted = find_order_candidates(segment, menus)
        compact_segment = normalize_text(segment)

        if not accepted:
            unmatched_segments.append(segment)
            continue

        for candidate in accepted:
            menu = candidate["menu"]
            window_start = max(0, candidate["start"] - 6)
            window_end = min(len(compact_segment), candidate["end"] + 12)
            context = compact_segment[window_start:window_end]
            quantity = extract_quantity(context)

            matches.append(
                {
                    "menu_id": menu["id"],
                    "name": menu["name"],
                    "category": menu["category"],
                    "price": menu["price"],
                    "quantity": quantity,
                    "subtotal": menu["price"] * quantity,
                }
            )

        remaining_text = extract_unmatched_text(segment, accepted)
        if len(remaining_text) >= 2:
            unmatched_segments.append(remaining_text)

    deduped: Dict[int, Dict] = {}
    for item in matches:
        existing = deduped.get(item["menu_id"])
        if existing:
            existing["quantity"] += item["quantity"]
            existing["subtotal"] = existing["price"] * existing["quantity"]
        else:
            deduped[item["menu_id"]] = item

    return {
        "items": list(deduped.values()),
        "remaining_text": " ".join(unmatched_segments).strip(),
    }


def parse_voice_order(text: str, menus: List[Dict]) -> List[Dict]:
    return parse_voice_order_result(text, menus)["items"]
