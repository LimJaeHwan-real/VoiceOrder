from __future__ import annotations

import os
import re
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from flask import Flask, jsonify, render_template, request

from init_db import initialize_database

BASE_DIR = Path(__file__).resolve().parent


def resolve_db_path() -> Path:
    configured_path = os.getenv("KIOSK_DB_PATH")
    if configured_path:
        return Path(configured_path)

    if os.getenv("VERCEL"):
        return Path(tempfile.gettempdir()) / "kiosk.db"

    return BASE_DIR / "kiosk.db"


DB_PATH = resolve_db_path()

app = Flask(__name__)

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


def ensure_database() -> None:
    initialize_database(DB_PATH)


def get_connection() -> sqlite3.Connection:
    ensure_database()
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def fetch_menus() -> List[Dict]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT id, name, price, image_url, category FROM Menu WHERE category IS NOT NULL ORDER BY id"
        ).fetchall()
    return [dict(row) for row in rows]


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

    for word, value in sorted(KOREAN_NUMBER_MAP.items(), key=lambda item: len(item[0]), reverse=True):
        if word in snippet:
            return value
    return 1


def parse_voice_order(text: str, menus: List[Dict]) -> List[Dict]:
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

    matches: List[Dict] = []
    for candidate in accepted:
        menu = candidate["menu"]
        window_start = max(0, candidate["start"] - 6)
        window_end = min(len(compact_text), candidate["end"] + 12)
        context = compact_text[window_start:window_end]
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

    deduped: Dict[int, Dict] = {}
    for item in matches:
        existing = deduped.get(item["menu_id"])
        if existing:
            existing["quantity"] += item["quantity"]
            existing["subtotal"] = existing["price"] * existing["quantity"]
        else:
            deduped[item["menu_id"]] = item

    return list(deduped.values())


@app.route("/")
def index():
    ensure_database()
    return render_template("index.html")


@app.get("/api/menus")
def api_menus():
    return jsonify({"menus": fetch_menus()})


@app.post("/api/order/voice")
def api_order_voice():
    payload = request.get_json(silent=True) or {}
    text = (payload.get("text") or "").strip()

    if not text:
        return jsonify({"error": "음성 인식 텍스트가 비어 있습니다."}), 400

    items = parse_voice_order(text, fetch_menus())
    total_price = sum(item["subtotal"] for item in items)

    if not items:
        return jsonify(
            {
                "transcript": text,
                "items": [],
                "total_price": 0,
                "message": "메뉴를 찾지 못했습니다. 다시 말씀해 주세요.",
            }
        ), 200

    return jsonify(
        {
            "transcript": text,
            "items": items,
            "total_price": total_price,
            "message": "주문 후보를 장바구니에 담았습니다.",
        }
    )


@app.post("/api/order/confirm")
def api_order_confirm():
    payload = request.get_json(silent=True) or {}
    items = payload.get("items") or []

    if not items:
        return jsonify({"error": "주문할 상품이 없습니다."}), 400

    menus = {menu["id"]: menu for menu in fetch_menus()}
    normalized_items = []
    total_price = 0

    for item in items:
        menu_id = int(item.get("menu_id", 0))
        quantity = int(item.get("quantity", 0))

        if menu_id not in menus or quantity <= 0:
            return jsonify({"error": "유효하지 않은 주문 항목이 포함되어 있습니다."}), 400

        menu = menus[menu_id]
        subtotal = menu["price"] * quantity
        total_price += subtotal
        normalized_items.append(
            {
                "menu_id": menu_id,
                "quantity": quantity,
                "price": menu["price"],
            }
        )

    created_at = datetime.utcnow().isoformat(timespec="seconds")

    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO Orders (total_price, created_at) VALUES (?, ?)",
            (total_price, created_at),
        )
        order_id = cursor.lastrowid

        cursor.executemany(
            "INSERT INTO Order_Items (order_id, menu_id, quantity) VALUES (?, ?, ?)",
            [
                (order_id, item["menu_id"], item["quantity"])
                for item in normalized_items
            ],
        )
        connection.commit()

    return jsonify(
        {
            "order_id": order_id,
            "total_price": total_price,
            "created_at": created_at,
            "message": "주문이 저장되었습니다.",
        }
    )


if __name__ == "__main__":
    ensure_database()
    app.run(debug=True, host="0.0.0.0", port=5000)
