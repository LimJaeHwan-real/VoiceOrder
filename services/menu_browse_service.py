from __future__ import annotations

from difflib import SequenceMatcher
from typing import Dict, List

from services.voice_order_service import menu_aliases, normalize_text

INTENT_KEYWORDS = {
    "coffee": ["커피", "아메리카노", "라떼", "카페", "coffee", "카페인", "진한 커피", "부드러운 커피"],
    "non-coffee": ["논커피", "티", "차", "tea", "음료", "주스", "스무디", "에이드", "차가운 음료", "상큼한 음료"],
    "dessert": ["디저트", "빵", "케이크", "머핀", "간식", "달달한거", "달달한 거", "dessert", "샌드위치", "후식", "먹을거"],
}

TAG_KEYWORDS = {
    "sweet": ["달달", "달콤", "단거", "단 거", "디저트", "sweet", "달달한", "달콤한"],
    "not-sweet": ["안단", "안 단", "안달", "안 달", "덜단", "덜 단", "달지않", "안달아", "안 달아"],
    "savory": ["안달", "안 단", "짭짤", "든든", "식사", "브런치"],
    "iced": ["차가운", "시원한", "아이스", "ice", "iced", "차갑", "차게", "시원하게"],
    "hot": ["따뜻한", "뜨거운", "hot", "warm", "따뜻하게"],
    "fruit": ["과일", "상큼", "fruity", "과일향", "과일 느낌"],
    "refreshing": ["상큼", "청량", "개운", "깔끔", "refreshing"],
    "peach": ["복숭아", "peach"],
    "strawberry": ["딸기", "strawberry"],
    "blueberry": ["블루베리", "blueberry"],
    "grapefruit": ["자몽", "grapefruit"],
    "chocolate": ["초코", "초콜릿", "chocolate"],
    "vanilla": ["바닐라", "vanilla"],
    "caramel": ["카라멜", "caramel"],
    "ginger": ["생강", "ginger"],
    "milk": ["우유", "부드러운", "라떼", "밀크"],
    "coffee": ["커피", "아메리카노", "라떼", "coffee"],
    "smoothie": ["스무디", "smoothie"],
    "dessert": ["디저트", "간식", "빵", "케이크", "머핀", "후식"],
    "sandwich": ["샌드위치", "토스트", "브런치"],
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
    if not categories and not tags:
        return {"categories": [], "tags": []}
    return {
        "categories": list(dict.fromkeys(categories)),
        "tags": list(dict.fromkeys(tags)),
    }


def fuzzy_similarity_score(text: str, menu: Dict) -> float:
    compact_text = normalize_text(text)
    if not compact_text:
        return 0.0

    candidates = [normalize_text(menu["name"])]
    candidates.extend(menu_aliases(menu["name"]))
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
        best_score = max(best_score, SequenceMatcher(None, compact_text, candidate).ratio())
    return best_score


def browse_menus_by_intent(text: str, menus: List[Dict]) -> Dict | None:
    intent = detect_browse_intent(text)
    categories = intent["categories"]
    tags = intent["tags"]
    if not categories and not tags:
        return None

    scored_menus = []
    for menu in menus:
        score = 0
        menu_tags = set(menu.get("tags") or [])
        menu_category = menu.get("category") or ""

        if menu_category in categories:
            score += 4
        for tag in tags:
            if tag in menu_tags:
                score += 3
        if "sweet" in tags and menu_category == "dessert":
            score += 1
        if "not-sweet" in tags and "not-sweet" in menu_tags:
            score += 3
        if "not-sweet" in tags and "sweet" in menu_tags:
            score -= 3
        if "fruit" in tags and {"strawberry", "blueberry", "peach"} & menu_tags:
            score += 1
        if "refreshing" in tags and {"fruit", "ade", "iced"} & menu_tags:
            score += 1
        if "savory" in tags and {"savory", "meal", "sandwich"} & menu_tags:
            score += 2
        if "hot" in tags and "hot" in menu_tags:
            score += 2
        if "iced" in tags and "iced" in menu_tags:
            score += 2

        similarity = fuzzy_similarity_score(text, menu)
        if similarity >= 0.72:
            score += int(similarity * 5)
        if score:
            scored_menus.append((score, similarity, menu))

    if not scored_menus:
        return {
            "mode": "browse",
            "categories": categories,
            "tags": tags,
            "menus": [],
            "title": "원하시는 조건의 메뉴를 아직 준비하지 못했어요.",
            "message": "현재 등록된 메뉴 중에서는 관련 메뉴를 찾지 못했습니다.",
            "scroll_target": categories[0] if categories else None,
        }

    scored_menus.sort(key=lambda entry: (-entry[0], -entry[1], entry[2]["id"]))
    selected = [menu for _, _, menu in scored_menus[:4]]

    if tags and not categories:
        title = "원하시는 느낌과 가까운 메뉴를 보여드릴게요."
    elif categories:
        category_title = {
            "coffee": "커피",
            "non-coffee": "논커피",
            "dessert": "디저트",
        }.get(categories[0], categories[0])
        title = f"{category_title} 메뉴를 보여드릴게요."
    else:
        title = "관련 메뉴를 보여드릴게요."

    return {
        "mode": "browse",
        "categories": categories,
        "tags": tags,
        "menus": selected,
        "title": title,
        "message": "말씀하신 조건과 관련된 메뉴를 추천했습니다.",
        "scroll_target": categories[0] if categories else (selected[0].get("category") if selected else None),
    }
