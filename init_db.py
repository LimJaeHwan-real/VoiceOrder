from __future__ import annotations

import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "kiosk.db"

SEED_MENUS = [
    {
        "name": "아이스 아메리카노",
        "price": 3000,
        "category": "coffee",
        "image_url": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=80",
        "tags": ["coffee", "iced", "bitter", "classic"],
        "description": "시원하고 깔끔한 기본 커피",
    },
    {
        "name": "핫 아메리카노",
        "price": 3000,
        "category": "coffee",
        "image_url": "https://images.unsplash.com/photo-1517701604599-bb29b565090c?auto=format&fit=crop&w=900&q=80",
        "tags": ["coffee", "hot", "bitter", "classic"],
        "description": "따뜻하게 즐기는 기본 커피",
    },
    {
        "name": "카페라떼",
        "price": 3800,
        "category": "coffee",
        "image_url": "https://images.unsplash.com/photo-1521017432531-fbd92d768814?auto=format&fit=crop&w=900&q=80",
        "tags": ["coffee", "milk", "smooth", "soft"],
        "description": "우유가 들어간 부드러운 커피",
    },
    {
        "name": "바닐라라떼",
        "price": 4300,
        "category": "coffee",
        "image_url": "https://images.unsplash.com/photo-1570968915860-54d5c301fa9f?auto=format&fit=crop&w=900&q=80",
        "tags": ["coffee", "milk", "sweet", "vanilla"],
        "description": "달콤한 바닐라 향이 더해진 라떼",
    },
    {
        "name": "카라멜마키아또",
        "price": 4500,
        "category": "coffee",
        "image_url": "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?auto=format&fit=crop&w=900&q=80",
        "tags": ["coffee", "sweet", "caramel", "milk"],
        "description": "카라멜 풍미가 살아있는 달콤한 커피",
    },
    {
        "name": "딸기스무디",
        "price": 4800,
        "category": "non-coffee",
        "image_url": "https://images.unsplash.com/photo-1502741338009-cac2772e18bc?auto=format&fit=crop&w=900&q=80",
        "tags": ["fruit", "strawberry", "sweet", "iced", "smoothie"],
        "description": "달콤하고 시원한 과일 스무디",
    },
    {
        "name": "자몽에이드",
        "price": 4700,
        "category": "non-coffee",
        "image_url": "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=900&q=80",
        "tags": ["fruit", "grapefruit", "ade", "iced", "refreshing"],
        "description": "상큼하고 청량한 자몽 에이드",
    },
    {
        "name": "생강차",
        "price": 4200,
        "category": "non-coffee",
        "image_url": "https://images.unsplash.com/photo-1515823064-d6e0c04616a7?auto=format&fit=crop&w=900&q=80",
        "tags": ["tea", "hot", "ginger", "warm"],
        "description": "따뜻하게 즐기는 향긋한 생강차",
    },
    {
        "name": "초코케이크",
        "price": 5200,
        "category": "dessert",
        "image_url": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=900&q=80",
        "tags": ["dessert", "sweet", "chocolate", "cake"],
        "description": "진한 초콜릿 풍미의 달콤한 케이크",
    },
    {
        "name": "햄치즈샌드위치",
        "price": 5900,
        "category": "dessert",
        "image_url": "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?auto=format&fit=crop&w=900&q=80",
        "tags": ["savory", "sandwich", "ham", "cheese", "meal"],
        "description": "든든하게 즐길 수 있는 짭짤한 샌드위치",
    },
    {
        "name": "블루베리머핀",
        "price": 3200,
        "category": "dessert",
        "image_url": "https://images.unsplash.com/photo-1607958996333-41aef7caefaa?auto=format&fit=crop&w=900&q=80",
        "tags": ["dessert", "sweet", "blueberry", "bakery", "muffin"],
        "description": "가볍게 즐기기 좋은 달콤한 머핀",
    },
]


def ensure_menu_columns(cursor: sqlite3.Cursor) -> None:
    columns = {row[1] for row in cursor.execute("PRAGMA table_info(Menu)").fetchall()}
    if "category" not in columns:
        cursor.execute("ALTER TABLE Menu ADD COLUMN category TEXT")
    if "tags" not in columns:
        cursor.execute("ALTER TABLE Menu ADD COLUMN tags TEXT")
    if "description" not in columns:
        cursor.execute("ALTER TABLE Menu ADD COLUMN description TEXT")


def initialize_database(db_path: Path = DEFAULT_DB_PATH) -> None:
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS Menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            price INTEGER NOT NULL,
            image_url TEXT,
            category TEXT,
            tags TEXT,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS Orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_price INTEGER NOT NULL,
            created_at TIMESTAMP NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Order_Items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            menu_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES Orders (id),
            FOREIGN KEY (menu_id) REFERENCES Menu (id)
        );
        """
    )

    ensure_menu_columns(cursor)

    serialized_menus = [
        {
            **menu,
            "tags": json.dumps(menu["tags"], ensure_ascii=False),
        }
        for menu in SEED_MENUS
    ]

    cursor.executemany(
        """
        INSERT INTO Menu (name, price, image_url, category, tags, description)
        VALUES (:name, :price, :image_url, :category, :tags, :description)
        ON CONFLICT(name) DO UPDATE SET
            price = excluded.price,
            image_url = excluded.image_url,
            category = excluded.category,
            tags = excluded.tags,
            description = excluded.description
        """,
        serialized_menus,
    )

    connection.commit()
    connection.close()


if __name__ == "__main__":
    initialize_database()
    print(f"Database initialized at {DEFAULT_DB_PATH}")
