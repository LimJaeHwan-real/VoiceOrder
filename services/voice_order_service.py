from __future__ import annotations

from difflib import SequenceMatcher
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
    "아이스 아메리카노": ["아아", "아이스아메리카노", "차가운아메리카노"],
    "핫 아메리카노": ["뜨아", "핫아메리카노", "따뜻한아메리카노", "뜨거운아메리카노"],
    "아이스 카페라떼": ["아이스라떼", "아이스카페라떼", "차가운라떼"],
    "핫 카페라떼": ["핫라떼", "핫카페라떼", "따뜻한라떼"],
    "아이스 바닐라라떼": ["아바라", "아이스바닐라라떼"],
    "핫 바닐라라떼": ["핫바닐라라떼", "따뜻한바닐라라떼"],
    "아이스 카라멜마키아또": ["아이스카라멜마키아또", "차가운카라멜마키아또"],
    "핫 카라멜마키아또": ["핫카라멜마키아또", "따뜻한카라멜마키아또"],
    "블루베리스무디": ["블루베리 스무디"],
    "딸기라떼": ["딸기 라떼"],
    "녹차라떼": ["녹차 라떼", "말차라떼", "말차 라떼"],
    "아이스 레몬에이드": ["아이스레몬에이드", "차가운레몬에이드"],
    "핫 레몬에이드": ["핫레몬에이드", "따뜻한레몬에이드"],
    "아이스 자몽에이드": ["아이스자몽에이드", "차가운자몽에이드"],
    "핫 자몽에이드": ["핫자몽에이드", "따뜻한자몽에이드"],
    "아이스 청포도에이드": ["아이스청포도에이드", "차가운청포도에이드"],
    "핫 청포도에이드": ["핫청포도에이드", "따뜻한청포도에이드"],
}

ICE_KEYWORDS = ["아이스", "차가운", "시원한", "ice", "iced", "차갑"]
HOT_KEYWORDS = ["핫", "따뜻한", "뜨거운", "hot", "warm", "뜨끈한"]

SEGMENT_SPLIT_PATTERN = re.compile(r"(?:이랑|랑|하고|하구|그리고|또|또는|및|,|/|\+)")
CANCEL_KEYWORDS = ["취소", "빼줘", "빼 주", "삭제", "제거", "지워", "빼고", "주문취소"]
TRAILING_FILLER_PATTERN = re.compile(
    r"(추가해줘|추가해 주|추가해|추가|주세요|주세용|줘요|해줘|해 주|먹고싶어|먹고 싶어|마시고싶어|마시고 싶어|부탁해|부탁드립니다)$"
)


def normalize_text(text: str) -> str:
    normalized = re.sub(r"[^0-9a-z가-힣]+", "", (text or "").lower())
    return normalized


def is_cancel_request(text: str) -> bool:
    compact_text = normalize_text(text)
    return any(normalize_text(keyword) in compact_text for keyword in CANCEL_KEYWORDS)


def detect_temperature_hint(text: str) -> str:
    compact_text = normalize_text(text)
    if any(normalize_text(keyword) in compact_text for keyword in ICE_KEYWORDS):
        return "ice"
    if any(normalize_text(keyword) in compact_text for keyword in HOT_KEYWORDS):
        return "hot"
    return ""


def menu_aliases(menu_or_name: Dict | str) -> List[str]:
    if isinstance(menu_or_name, dict):
        menu_name = menu_or_name["name"]
        group_name = menu_or_name.get("group_name") or menu_name
        category = menu_or_name.get("category") or ""
        temperature = menu_or_name.get("temperature") or ""
    else:
        menu_name = menu_or_name
        group_name = menu_name
        category = ""
        temperature = ""

    aliases = {menu_name, menu_name.replace(" ", ""), group_name, group_name.replace(" ", "")}
    aliases.update(MENU_SYNONYMS.get(menu_name, []))

    if temperature == "ice":
        aliases.update(
            {
                f"아이스 {group_name}",
                f"아이스{group_name}",
                f"차가운 {group_name}",
                f"차가운{group_name}",
            }
        )
    if temperature == "hot":
        aliases.update(
            {
                f"핫 {group_name}",
                f"핫{group_name}",
                f"따뜻한 {group_name}",
                f"따뜻한{group_name}",
                f"뜨거운 {group_name}",
                f"뜨거운{group_name}",
            }
        )

    if category in {"coffee", "ade"}:
        aliases.discard(group_name)
        aliases.discard(group_name.replace(" ", ""))

    return sorted({normalize_text(alias) for alias in aliases if alias}, key=len, reverse=True)


def extract_quantity(snippet: str) -> int:
    digit_match = re.search(r"(\d+)\s*(잔|개|컵)?", snippet)
    if digit_match:
        return max(1, int(digit_match.group(1)))

    for word, value in sorted(KOREAN_NUMBER_MAP.items(), key=lambda item: len(item[0]), reverse=True):
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


def trim_segment_noise(text: str) -> str:
    cleaned = text.strip()
    while cleaned:
        updated = TRAILING_FILLER_PATTERN.sub("", cleaned).strip(" ,.!?~")
        if updated == cleaned:
            break
        cleaned = updated
    return cleaned


def find_order_candidates(text: str, menus: List[Dict]) -> List[Dict]:
    compact_text = normalize_text(text)
    candidates = []

    for menu in menus:
        for alias in menu_aliases(menu):
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


def group_has_temperature_choices(menu: Dict, menus: List[Dict]) -> bool:
    group_name = menu.get("group_name") or menu["name"]
    temperatures = {
        item.get("temperature") or ""
        for item in menus
        if (item.get("group_name") or item["name"]) == group_name
    }
    return len({temp for temp in temperatures if temp}) > 1


def fuzzy_match_menu(text: str, menus: List[Dict], threshold: float = 0.82) -> Dict | None:
    compact_text = normalize_text(text)
    if not compact_text or len(compact_text) <= 2:
        return None

    temperature_hint = detect_temperature_hint(text)
    best_candidate = None
    second_best_score = 0.0

    for menu in menus:
        for alias in menu_aliases(menu):
            score = SequenceMatcher(None, compact_text, alias).ratio()
            if compact_text in alias or alias in compact_text:
                score = max(score, 0.9)
            if best_candidate is None or score > best_candidate["score"]:
                second_best_score = best_candidate["score"] if best_candidate else second_best_score
                best_candidate = {
                    "menu": menu,
                    "alias": alias,
                    "start": 0,
                    "end": len(compact_text),
                    "score": score,
                }
            elif score > second_best_score:
                second_best_score = score

    if best_candidate is None or best_candidate["score"] < threshold:
        return None

    menu = best_candidate["menu"]
    if group_has_temperature_choices(menu, menus) and not temperature_hint:
        return None

    if second_best_score and abs(best_candidate["score"] - second_best_score) < 0.04:
        return None

    return best_candidate


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
    cancel_matches: List[Dict] = []
    unmatched_segments: List[str] = []

    for segment in split_voice_segments(text):
        segment = trim_segment_noise(segment)
        if not segment:
            continue

        segment_is_cancel = is_cancel_request(segment)
        accepted = find_order_candidates(segment, menus)
        compact_segment = normalize_text(segment)

        if not accepted:
            fuzzy_candidate = fuzzy_match_menu(segment, menus)
            if fuzzy_candidate is None:
                unmatched_segments.append(segment)
                continue
            accepted = [fuzzy_candidate]

        for candidate in accepted:
            menu = candidate["menu"]
            window_start = max(0, candidate["start"] - 6)
            window_end = min(len(compact_segment), candidate["end"] + 12)
            context = compact_segment[window_start:window_end]
            quantity = extract_quantity(context)

            target_list = cancel_matches if segment_is_cancel else matches
            target_list.append(
                {
                    "menu_id": menu["id"],
                    "name": menu["name"],
                    "group_name": menu.get("group_name") or menu["name"],
                    "temperature": menu.get("temperature") or "",
                    "category": menu["category"],
                    "price": menu["price"],
                    "quantity": quantity,
                    "subtotal": menu["price"] * quantity,
                }
            )

        remaining_text = extract_unmatched_text(segment, accepted)
        if len(remaining_text) >= 2:
            unmatched_segments.append(remaining_text)

    def dedupe_items(items: List[Dict]) -> List[Dict]:
        deduped: Dict[int, Dict] = {}
        for item in items:
            existing = deduped.get(item["menu_id"])
            if existing:
                existing["quantity"] += item["quantity"]
                existing["subtotal"] = existing["price"] * existing["quantity"]
            else:
                deduped[item["menu_id"]] = item
        return list(deduped.values())

    return {
        "items": dedupe_items(matches),
        "cancel_items": dedupe_items(cancel_matches),
        "remaining_text": " ".join(unmatched_segments).strip(),
    }


def parse_voice_order(text: str, menus: List[Dict]) -> List[Dict]:
    return parse_voice_order_result(text, menus)["items"]
