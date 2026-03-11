from __future__ import annotations

from difflib import SequenceMatcher
from typing import Dict, List

from services.voice_order_service import menu_aliases, normalize_text

CATEGORY_TITLES = {
    "coffee": "커피",
    "beverage": "베버리지",
    "tea": "티",
    "ade": "에이드",
}

INTENT_KEYWORDS = {
    "coffee": [
        "커피",
        "아메리카노",
        "라떼",
        "마키아또",
        "카페",
        "coffee",
        "카페인",
    ],
    "beverage": [
        "베버리지",
        "스무디",
        "논커피",
        "딸기라떼",
        "녹차라떼",
        "차가운 음료",
        "달달한 음료",
        "beverage",
    ],
    "tea": [
        "티",
        "차",
        "tea",
        "캐모마일",
        "녹차",
        "유자차",
        "따뜻한 차",
    ],
    "ade": [
        "에이드",
        "ade",
        "자몽",
        "레몬",
        "청포도",
        "상큼한 음료",
    ],
}

TAG_KEYWORDS = {
    "sweet": ["달달", "달콤", "단거", "단 거", "sweet", "달달한", "달콤한"],
    "not-sweet": ["안단", "안 단", "안달", "안 달", "덜단", "덜 단", "안달아", "안 달아"],
    "iced": ["아이스", "차가운", "시원한", "ice", "iced", "차갑", "시원하게"],
    "hot": ["핫", "따뜻한", "뜨거운", "hot", "warm", "따뜻하게"],
    "fruit": ["과일", "상큼", "fruity", "과일향", "과일 향"],
    "strawberry": ["딸기", "strawberry"],
    "blueberry": ["블루베리", "blueberry"],
    "grapefruit": ["자몽", "grapefruit"],
    "lemon": ["레몬", "lemon"],
    "grape": ["청포도", "grape"],
    "vanilla": ["바닐라", "vanilla"],
    "caramel": ["카라멜", "caramel"],
    "milk": ["우유", "라떼", "밀크", "milk"],
    "smoothie": ["스무디", "smoothie"],
    "tea": ["차", "티", "tea"],
    "coffee": ["커피", "아메리카노", "라떼", "coffee"],
    "citrus": ["시트러스", "감귤", "유자", "citrus"],
    "refreshing": ["상큼", "청량", "개운", "refreshing"],
}


def detect_browse_intent(text: str) -> Dict:
    compact_text = normalize_text(text)
    categories = [
        category
        for category, keywords in INTENT_KEYWORDS.items()
        if any(normalize_text(keyword) in compact_text for keyword in keywords)
    ]
    tags = [
        tag
        for tag, keywords in TAG_KEYWORDS.items()
        if any(normalize_text(keyword) in compact_text for keyword in keywords)
    ]
    return {
        "categories": list(dict.fromkeys(categories)),
        "tags": list(dict.fromkeys(tags)),
    }


def fuzzy_similarity_score(text: str, menu: Dict) -> float:
    compact_text = normalize_text(text)
    if not compact_text:
        return 0.0

    candidates = [normalize_text(menu["name"]), normalize_text(menu.get("group_name") or menu["name"])]
    candidates.extend(menu_aliases(menu))
    candidates.extend(normalize_text(tag) for tag in menu.get("tags") or [])
    if menu.get("description"):
        candidates.append(normalize_text(menu["description"]))

    best_score = 0.0
    for candidate in candidates:
        if not candidate:
            continue
        if compact_text in candidate or candidate in compact_text:
            best_score = max(best_score, 0.92)
            continue
        best_score = max(
            best_score,
            SequenceMatcher(None, compact_text, candidate).ratio(),
        )
    return best_score


def score_menu(text: str, menu: Dict, categories: List[str], tags: List[str]) -> tuple[int, float]:
    score = 0
    menu_tags = set(menu.get("tags") or [])
    menu_category = menu.get("category") or ""
    similarity = fuzzy_similarity_score(text, menu)

    if menu_category in categories:
        score += 5

    for tag in tags:
        if tag in menu_tags:
            score += 3

    if "iced" in tags and menu.get("temperature") == "ice":
        score += 2
    if "hot" in tags and menu.get("temperature") == "hot":
        score += 2
    if "fruit" in tags and {"strawberry", "blueberry", "grapefruit", "lemon", "grape"} & menu_tags:
        score += 1
    if "refreshing" in tags and {"fruit", "citrus", "ade", "iced"} & menu_tags:
        score += 1
    if "not-sweet" in tags and "sweet" in menu_tags:
        score -= 2
    if "coffee" in tags and menu_category == "coffee":
        score += 1
    if "tea" in tags and menu_category == "tea":
        score += 1

    if similarity >= 0.7:
        score += int(similarity * 5)

    return score, similarity


def browse_menus_by_intent(text: str, menus: List[Dict]) -> Dict | None:
    compact_text = normalize_text(text)
    if not compact_text:
        return None

    intent = detect_browse_intent(text)
    categories = intent["categories"]
    tags = intent["tags"]
    scored_menus = []

    for menu in menus:
        score, similarity = score_menu(text, menu, categories, tags)
        if score > 0 or similarity >= 0.78:
            scored_menus.append((score, similarity, menu))

    if not scored_menus:
        return None

    scored_menus.sort(key=lambda entry: (-entry[0], -entry[1], entry[2]["sort_order"], entry[2]["id"]))
    selected = [menu for _, _, menu in scored_menus]
    result_count = len(selected)

    if categories:
        title = f"{CATEGORY_TITLES.get(categories[0], categories[0])} 메뉴로 필터링했어요."
    elif tags:
        title = "말씀하신 조건에 맞춰 메뉴를 골라봤어요."
    else:
        title = "말씀하신 메뉴와 비슷한 항목을 모아봤어요."

    return {
        "mode": "browse",
        "categories": categories,
        "tags": tags,
        "menus": selected,
        "result_count": result_count,
        "title": title,
        "message": f"조건에 맞는 메뉴 {result_count}개를 아래 메뉴판에서 보여주고 있습니다.",
        "scroll_target": categories[0] if categories else (selected[0].get("category") if selected else None),
    }
