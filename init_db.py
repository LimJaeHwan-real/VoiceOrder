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
        "image_url": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=80",
        "category": "coffee",
        "tags": ["coffee", "iced", "bitter", "classic"],
        "description": "시원하고 깔끔한 기본 커피",
    },
    {
        "name": "카페라떼",
        "price": 3800,
        "image_url": "https://images.unsplash.com/photo-1521017432531-fbd92d768814?auto=format&fit=crop&w=900&q=80",
        "category": "coffee",
        "tags": ["coffee", "milk", "smooth", "soft"],
        "description": "우유가 들어간 부드러운 커피",
    },
    {
        "name": "딸기 스무디",
        "price": 4500,
        "image_url": "https://images.unsplash.com/photo-1502741338009-cac2772e18bc?auto=format&fit=crop&w=900&q=80",
        "category": "tea",
        "tags": ["fruit", "strawberry", "sweet", "iced", "smoothie"],
        "description": "달콤하고 시원한 과일 스무디",
    },
    {
        "name": "초코 케이크",
        "price": 5200,
        "image_url": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=900&q=80",
        "category": "snack",
        "tags": ["dessert", "sweet", "chocolate", "cake"],
        "description": "진한 초콜릿 풍미의 달콤한 케이크",
    },
    {
        "name": "블루베리 머핀",
        "price": 2800,
        "image_url": "https://images.unsplash.com/photo-1607958996333-41aef7caefaa?auto=format&fit=crop&w=900&q=80",
        "category": "snack",
        "tags": ["dessert", "sweet", "blueberry", "bakery", "muffin"],
        "description": "가볍게 즐기기 좋은 달콤한 머핀",
    },
]


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

    existing_columns = {
        row[1] for row in cursor.execute("PRAGMA table_info(Menu)").fetchall()
    }
    if "category" not in existing_columns:
        cursor.execute("ALTER TABLE Menu ADD COLUMN category TEXT")
    if "tags" not in existing_columns:
        cursor.execute("ALTER TABLE Menu ADD COLUMN tags TEXT")
    if "description" not in existing_columns:
        cursor.execute("ALTER TABLE Menu ADD COLUMN description TEXT")

    cursor.executemany(
        """
        INSERT OR IGNORE INTO Menu (name, price, image_url, category, tags, description)
        VALUES (:name, :price, :image_url, :category, :tags, :description)
        """,
        [
            {
                **menu,
                "tags": json.dumps(menu["tags"], ensure_ascii=False),
            }
            for menu in SEED_MENUS
        ],
    )

    cursor.executemany(
        """
        UPDATE Menu
        SET price = :price,
            image_url = :image_url,
            category = :category,
            tags = :tags,
            description = :description
        WHERE name = :name
        """,
        [
            {
                **menu,
                "tags": json.dumps(menu["tags"], ensure_ascii=False),
            }
            for menu in SEED_MENUS
        ],
    )

    connection.commit()
    connection.close()


if __name__ == "__main__":
    initialize_database()
    print(f"Database initialized at {DEFAULT_DB_PATH}")
