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
    "아이스 카라멜마키아또": ["아이스카라멜마키아또", "차가운카라멜마키아또", "카라멜마끼야또", "카라멜마끼아또", "카라멜마키야또"],
    "핫 카라멜마키아또": ["핫카라멜마키아또", "따뜻한카라멜마키아또", "핫카라멜마끼야또", "핫카라멜마끼아또", "핫카라멜마키야또"],
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

ICE_KEYWORDS = ["아이스", "나이스", "차가운", "시원한", "ice", "iced", "차갑"]
HOT_KEYWORDS = ["핫", "따뜻한", "뜨거운", "hot", "warm", "뜨끈한"]
GLOBAL_TEMPERATURE_KEYWORDS = ["전부", "모두", "다", "전부다", "모두다"]

SEGMENT_SPLIT_PATTERN = re.compile(r"(?:이랑|랑|하고|하구|그리고|및|,|/|\+)")
QUANTITY_BOUNDARY_PATTERN = re.compile(
    r"((?:\d+\s*(?:잔|개|컵)?|열두|열한|열|아홉|여덟|일곱|여섯|다섯|네|세|두|한|하나|둘|셋|넷)(?:\s*(?:잔|개|컵))?)\s+"
)
CANCEL_KEYWORDS = ["취소", "빼줘", "빼 주", "삭제", "제거", "지워", "빼고", "주문취소"]
TRAILING_FILLER_PATTERN = re.compile(
    r"(추가해줘|추가해 주|추가해|추가|주세요|주세용|줘요|해줘|해 주|먹고싶어|먹고 싶어|마시고싶어|마시고 싶어|부탁해요|부탁해|부탁드립니다)$"
)
LEADING_FILLER_PATTERN = re.compile(
    r"^(주문할게요|주문할게|주문이요|주문좀|주문 좀|저기요|저는요|그러면|그냥|일단|저기|저요|혹시|근데|아니|제가|저는|나는|음|어)+"
)
NOISE_PHRASES = [
    "그냥",
    "혹시",
    "그러면",
    "그럼",
    "일단",
    "저기",
    "저기요",
    "주문할게요",
    "주문할게",
    "주문이요",
    "먹고싶은데",
    "먹고 싶은데",
    "마시고싶은데",
    "마시고 싶은데",
    "해주세요",
    "해 주세요",
    "부탁해요",
    "부탁합니다",
]
QUANTITY_TOKEN_PATTERN = re.compile(
    r"(\d+\s*(?:잔|개|컵)?|열두|열한|열|아홉|여덟|일곱|여섯|다섯|네|세|두|한|하나|둘|셋|넷)(?:\s*(?:잔|개|컵))?"
)
TRAILING_PARTICLE_PATTERN = re.compile(r"(은|는|이|가|을|를|와|과|도|만|으로|로|에|에서|께|한테)+$")


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


def detect_global_temperature_hint(text: str) -> str:
    compact_text = normalize_text(text)
    if not any(normalize_text(keyword) in compact_text for keyword in GLOBAL_TEMPERATURE_KEYWORDS):
        return ""

    has_ice = any(normalize_text(keyword) in compact_text for keyword in ICE_KEYWORDS)
    has_hot = any(normalize_text(keyword) in compact_text for keyword in HOT_KEYWORDS)
    if has_ice and not has_hot:
        return "ice"
    if has_hot and not has_ice:
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
    normalized_text = QUANTITY_BOUNDARY_PATTERN.sub(r"\1|", text)
    raw_segments = []
    for chunk in SEGMENT_SPLIT_PATTERN.split(normalized_text):
        raw_segments.extend(chunk.split("|"))
    segments = []
    for segment in raw_segments:
        cleaned = segment.strip(" ,.!?~")
        if cleaned:
            segments.append(cleaned)

    merged_segments = []
    for segment in segments:
        if merged_segments and is_cancel_directive_only(segment):
            merged_segments[-1] = f"{merged_segments[-1]} {segment}".strip()
        else:
            merged_segments.append(segment)

    return merged_segments or [text.strip()]


def is_cancel_directive_only(text: str) -> bool:
    stripped_segment = normalize_text(text)
    for keyword in CANCEL_KEYWORDS:
        stripped_segment = stripped_segment.replace(normalize_text(keyword), "")
    for filler in ["해줘", "해주세요", "해주", "줘", "주세", "좀", "만", "요"]:
        stripped_segment = stripped_segment.replace(normalize_text(filler), "")
    return is_cancel_request(text) and not stripped_segment


def trim_segment_noise(text: str) -> str:
    cleaned = text.strip()
    while cleaned:
        updated = LEADING_FILLER_PATTERN.sub("", cleaned).strip(" ,.!?~")
        if updated == cleaned:
            break
        cleaned = updated
    while cleaned:
        updated = TRAILING_FILLER_PATTERN.sub("", cleaned).strip(" ,.!?~")
        if updated == cleaned:
            break
        cleaned = updated
    compact_cleaned = normalize_text(cleaned)
    for phrase in NOISE_PHRASES:
        normalized_phrase = normalize_text(phrase)
        if normalized_phrase:
            compact_cleaned = compact_cleaned.replace(normalized_phrase, "")
    return compact_cleaned or cleaned


def strip_quantity_tokens(text: str) -> str:
    return QUANTITY_TOKEN_PATTERN.sub("", text).strip()


def cleanup_remaining_text(text: str) -> str:
    cleaned = normalize_text(strip_quantity_tokens(text))
    for keyword in CANCEL_KEYWORDS:
        cleaned = cleaned.replace(normalize_text(keyword), "")
    for keyword in ICE_KEYWORDS + HOT_KEYWORDS + GLOBAL_TEMPERATURE_KEYWORDS:
        cleaned = cleaned.replace(normalize_text(keyword), "")
    for filler in [
        "추가", "추가해", "추가해줘", "주세요", "줘", "해줘", "주고", "하고", "해", "좀",
        "말고", "그리고", "그냥", "부탁", "부탁해요", "전부", "모두", "다",
    ]:
        cleaned = cleaned.replace(normalize_text(filler), "")

    previous = None
    while cleaned and previous != cleaned:
        previous = cleaned
        cleaned = TRAILING_PARTICLE_PATTERN.sub("", cleaned)
    return cleaned.strip()


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


def merge_candidates(*candidate_lists: List[Dict]) -> List[Dict]:
    merged = []
    for candidate_list in candidate_lists:
        merged.extend(candidate_list)

    merged.sort(key=lambda item: (-(item["end"] - item["start"]), item["start"]))

    accepted = []
    for candidate in merged:
        overlaps = any(
            not (candidate["end"] <= existing["start"] or candidate["start"] >= existing["end"])
            for existing in accepted
        )
        if not overlaps:
            accepted.append(candidate)
    return accepted


def default_temperature_for_menu(menu: Dict) -> str:
    category = menu.get("category") or ""
    if category in {"coffee", "ade", "beverage"}:
        return "ice"
    if category == "tea":
        return "hot"
    return menu.get("temperature") or ""


def menus_for_group(group_name: str, menus: List[Dict]) -> List[Dict]:
    return [
        menu
        for menu in menus
        if normalize_text(menu.get("group_name") or menu["name"]) == group_name
    ]


def temperature_options_for_group(group_name: str, menus: List[Dict]) -> List[Dict]:
    group_menus = menus_for_group(group_name, menus)
    order = {"ice": 0, "hot": 1}
    return sorted(
        [
            {
                "menu_id": menu["id"],
                "name": menu["name"],
                "temperature": menu.get("temperature") or "",
                "price": menu["price"],
                "category": menu["category"],
            }
            for menu in group_menus
        ],
        key=lambda option: (order.get(option["temperature"], 9), option["menu_id"]),
    )


def menu_for_option(option: Dict, menus: List[Dict]) -> Dict | None:
    return next((menu for menu in menus if menu["id"] == option["menu_id"]), None)


def temperature_option_for_hint(group_name: str, menus: List[Dict], temperature_hint: str) -> Dict | None:
    if not temperature_hint:
        return None
    return next(
        (
            option
            for option in temperature_options_for_group(group_name, menus)
            if option["temperature"] == temperature_hint
        ),
        None,
    )


def find_group_name_candidates(text: str, menus: List[Dict], temperature_hint: str = "") -> List[Dict]:
    compact_text = normalize_text(text)
    group_candidates = []
    seen_groups = set()

    normalized_groups = sorted(
        {
            normalize_text(menu.get("group_name") or menu["name"])
            for menu in menus
            if menu.get("group_name") or menu.get("name")
        },
        key=len,
        reverse=True,
    )

    for group_name in normalized_groups:
        if not group_name or group_name in seen_groups:
            continue
        hit_index = compact_text.find(group_name)
        if hit_index < 0:
            continue

        group_options = temperature_options_for_group(group_name, menus)
        if not group_options:
            continue

        candidate = {
            "alias": group_name,
            "start": hit_index,
            "end": hit_index + len(group_name),
        }
        if len(group_options) > 1 and temperature_hint:
            resolved_option = temperature_option_for_hint(group_name, menus, temperature_hint)
            resolved_menu = menu_for_option(resolved_option, menus) if resolved_option else None
            if not resolved_menu:
                continue
            candidate["menu"] = resolved_menu
        elif len(group_options) > 1:
            candidate["pending_options"] = group_options
            candidate["group_name"] = group_options[0]["name"].replace("아이스 ", "").replace("핫 ", "")
            candidate["category"] = group_options[0]["category"]
        else:
            selected_menu = menu_for_option(group_options[0], menus)
            if not selected_menu:
                continue
            candidate["menu"] = selected_menu

        group_candidates.append(candidate)
        seen_groups.add(group_name)

    group_candidates.sort(key=lambda item: (-(item["end"] - item["start"]), item["start"]))

    accepted = []
    for candidate in group_candidates:
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
    compact_text = normalize_text(strip_quantity_tokens(text) or text)
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
        best_candidate["menu"] = None
        best_candidate["group_name"] = menu.get("group_name") or menu["name"]
        best_candidate["category"] = menu.get("category") or ""
        best_candidate["pending_options"] = temperature_options_for_group(
            normalize_text(menu.get("group_name") or menu["name"]),
            menus,
        )

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
    return cleanup_remaining_text(remaining)


def parse_voice_order_result(text: str, menus: List[Dict]) -> Dict:
    matches: List[Dict] = []
    cancel_matches: List[Dict] = []
    pending_items: List[Dict] = []
    unavailable_items: List[Dict] = []
    unmatched_segments: List[str] = []
    global_temperature_hint = detect_global_temperature_hint(text)

    for segment in split_voice_segments(text):
        segment = trim_segment_noise(segment)
        if not segment:
            continue

        segment_is_cancel = is_cancel_request(segment)
        segment_temperature_hint = detect_temperature_hint(segment) or global_temperature_hint
        accepted = find_order_candidates(segment, menus)
        compact_segment = normalize_text(segment)
        group_candidates = find_group_name_candidates(segment, menus, segment_temperature_hint)
        accepted = merge_candidates(accepted, group_candidates)

        if not accepted:
            fuzzy_candidate = fuzzy_match_menu(segment, menus)
            if fuzzy_candidate is None:
                unmatched_segments.append(segment)
                continue
            accepted = [fuzzy_candidate]

        for candidate in accepted:
            window_start = max(0, candidate["start"] - 6)
            window_end = min(len(compact_segment), candidate["end"] + 12)
            context = compact_segment[window_start:window_end]
            quantity = extract_quantity(context)

            if candidate.get("pending_options"):
                pending_items.append(
                    {
                        "group_name": candidate.get("group_name") or "",
                        "category": candidate.get("category") or "",
                        "quantity": quantity,
                        "action": "cancel" if segment_is_cancel else "add",
                        "options": candidate["pending_options"],
                    }
                )
                continue

            menu = candidate["menu"]
            if (
                segment_temperature_hint
                and (menu.get("temperature") or "")
                and (menu.get("temperature") or "") != segment_temperature_hint
                and not group_has_temperature_choices(menu, menus)
            ):
                unavailable_items.append(
                    {
                        "group_name": menu.get("group_name") or menu["name"],
                        "requested_temperature": segment_temperature_hint,
                        "available_temperature": menu.get("temperature") or "",
                        "quantity": quantity,
                        "action": "cancel" if segment_is_cancel else "add",
                    }
                )
                continue

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
        if len(remaining_text) >= 2 and not is_cancel_directive_only(remaining_text):
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

    def dedupe_pending(items: List[Dict]) -> List[Dict]:
        deduped: Dict[str, Dict] = {}
        for item in items:
            key = f"{item['action']}:{normalize_text(item['group_name'])}"
            existing = deduped.get(key)
            if existing:
                existing["quantity"] += item["quantity"]
            else:
                deduped[key] = {
                    "group_name": item["group_name"],
                    "category": item["category"],
                    "quantity": item["quantity"],
                    "action": item["action"],
                    "options": item["options"],
                }
        return list(deduped.values())

    def dedupe_unavailable(items: List[Dict]) -> List[Dict]:
        deduped: Dict[str, Dict] = {}
        for item in items:
            key = f"{item['action']}:{normalize_text(item['group_name'])}:{item['requested_temperature']}"
            existing = deduped.get(key)
            if existing:
                existing["quantity"] += item["quantity"]
            else:
                deduped[key] = dict(item)
        return list(deduped.values())

    return {
        "items": dedupe_items(matches),
        "cancel_items": dedupe_items(cancel_matches),
        "pending_items": dedupe_pending(pending_items),
        "unavailable_items": dedupe_unavailable(unavailable_items),
        "remaining_text": " ".join(unmatched_segments).strip(),
    }


def parse_voice_order(text: str, menus: List[Dict]) -> List[Dict]:
    return parse_voice_order_result(text, menus)["items"]
