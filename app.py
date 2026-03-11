from __future__ import annotations

from datetime import datetime

from flask import Flask, jsonify, render_template, request

from db import ensure_database, get_connection
from services.menu_browse_service import browse_menus_by_intent
from services.menu_service import fetch_menus
from services.voice_order_service import parse_voice_order_result

app = Flask(__name__)


def build_pending_option_message(pending_items):
    first_item = pending_items[0]
    group_name = first_item["group_name"]
    quantity = first_item["quantity"]
    count_label = f"{quantity}잔" if quantity > 1 else "1잔"
    action_label = "뺄까요" if first_item.get("action") == "cancel" else "담을까요"
    return f"{group_name} {count_label}은 아이스와 핫 중 어떤 걸로 {action_label}"


@app.route("/")
def index():
    ensure_database()
    return render_template("index.html")


@app.get("/api/menus")
def api_menus():
    return jsonify({"menus": fetch_menus()})


@app.post("/api/menus/browse")
def api_menus_browse():
    payload = request.get_json(silent=True) or {}
    text = (payload.get("text") or "").strip()

    if not text:
        return jsonify({"error": "검색할 음성 또는 텍스트가 비어 있습니다."}), 400

    menus = fetch_menus()
    browse_result = browse_menus_by_intent(text, menus)

    if not browse_result:
        return jsonify(
            {
                "transcript": text,
                "browse_result": None,
                "message": "조건에 맞는 메뉴를 찾지 못했습니다. 다른 키워드로 다시 말씀해 주세요.",
            }
        )

    return jsonify(
        {
            "transcript": text,
            "browse_result": browse_result,
            "message": browse_result["message"],
        }
    )


@app.post("/api/order/voice")
def api_order_voice():
    payload = request.get_json(silent=True) or {}
    text = (payload.get("text") or "").strip()

    if not text:
        return jsonify({"error": "음성 인식 텍스트가 비어 있습니다."}), 400

    menus = fetch_menus()
    order_result = parse_voice_order_result(text, menus)
    items = order_result["items"]
    cancel_items = order_result["cancel_items"]
    pending_items = order_result["pending_items"]
    remaining_text = order_result["remaining_text"]
    total_price = sum(item["subtotal"] for item in items)
    browse_text = remaining_text if (items or cancel_items) else (remaining_text or text)
    browse_result = browse_menus_by_intent(browse_text, menus) if (browse_text and not pending_items) else None

    if not items and not cancel_items and not pending_items:
        return jsonify(
            {
                "transcript": text,
                "items": [],
                "cancel_items": [],
                "pending_items": [],
                "total_price": 0,
                "browse_result": browse_result,
                "message": (
                    browse_result["message"]
                    if browse_result
                    else "일치하는 메뉴를 찾지 못했습니다. 다시 말씀해 주세요."
                ),
            }
        )

    if pending_items and not items and not cancel_items:
        return jsonify(
            {
                "transcript": text,
                "items": [],
                "cancel_items": [],
                "pending_items": pending_items,
                "total_price": 0,
                "browse_result": None,
                "message": build_pending_option_message(pending_items),
            }
        )

    if cancel_items:
        return jsonify(
            {
                "transcript": text,
                "items": items,
                "cancel_items": cancel_items,
                "pending_items": pending_items,
                "total_price": 0,
                "browse_result": browse_result if not items and not pending_items else None,
                "message": (
                    f"메뉴를 반영했고, {build_pending_option_message(pending_items)}"
                    if pending_items
                    else "담을 메뉴와 취소할 메뉴를 함께 확인했습니다."
                    if items
                    else "장바구니에서 뺄 메뉴를 확인했습니다."
                ),
            }
        )

    return jsonify(
        {
            "transcript": text,
            "items": items,
            "cancel_items": [],
            "pending_items": pending_items,
            "total_price": total_price,
            "browse_result": browse_result if not pending_items else None,
            "message": (
                build_pending_option_message(pending_items)
                if pending_items
                else
                "메뉴를 장바구니에 담고 관련 메뉴도 함께 보여주고 있습니다."
                if browse_result
                else "메뉴를 장바구니에 담았습니다."
            ),
        }
    )


@app.post("/api/order/confirm")
def api_order_confirm():
    payload = request.get_json(silent=True) or {}
    items = payload.get("items") or []
    order_channel = (payload.get("order_channel") or "touch").strip() or "touch"
    service_mode = (payload.get("service_mode") or "").strip() or None
    payment_method = (payload.get("payment_method") or "").strip() or None

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
            """
            INSERT INTO Orders (total_price, created_at, order_channel, service_mode, payment_method)
            VALUES (?, ?, ?, ?, ?)
            """,
            (total_price, created_at, order_channel, service_mode, payment_method),
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
