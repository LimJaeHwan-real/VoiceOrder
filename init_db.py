from __future__ import annotations

import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "kiosk.db"

SEED_MENUS = [
    {
        "name": "아이스 아메리카노",
        "group_name": "아메리카노",
        "temperature": "ice",
        "price": 3000,
        "category": "coffee",
        "sort_order": 10,
        "image_url": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=80",
        "tags": ["coffee", "americano", "iced", "classic", "bitter", "caffeine"],
        "description": "차갑고 깔끔하게 즐기는 기본 커피",
        "is_active": 1,
    },
    {
        "name": "핫 아메리카노",
        "group_name": "아메리카노",
        "temperature": "hot",
        "price": 3000,
        "category": "coffee",
        "sort_order": 10,
        "image_url": "https://images.unsplash.com/photo-1517701604599-bb29b565090c?auto=format&fit=crop&w=900&q=80",
        "tags": ["coffee", "americano", "hot", "classic", "bitter", "caffeine"],
        "description": "따뜻하고 진한 향이 살아 있는 기본 커피",
        "is_active": 1,
    },
    {
        "name": "아이스 카페라떼",
        "group_name": "카페라떼",
        "temperature": "ice",
        "price": 3800,
        "category": "coffee",
        "sort_order": 20,
        "image_url": "https://images.unsplash.com/photo-1521017432531-fbd92d768814?auto=format&fit=crop&w=900&q=80",
        "tags": ["coffee", "latte", "milk", "iced", "soft", "caffeine"],
        "description": "우유 풍미가 부드럽게 어우러지는 차가운 라떼",
        "is_active": 1,
    },
    {
        "name": "핫 카페라떼",
        "group_name": "카페라떼",
        "temperature": "hot",
        "price": 3800,
        "category": "coffee",
        "sort_order": 20,
        "image_url": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=900&q=80",
        "tags": ["coffee", "latte", "milk", "hot", "soft", "caffeine"],
        "description": "우유와 에스프레소가 부드럽게 어우러지는 따뜻한 라떼",
        "is_active": 1,
    },
    {
        "name": "아이스 바닐라라떼",
        "group_name": "바닐라라떼",
        "temperature": "ice",
        "price": 4300,
        "category": "coffee",
        "sort_order": 30,
        "image_url": "https://images.unsplash.com/photo-1570968915860-54d5c301fa9f?auto=format&fit=crop&w=900&q=80",
        "tags": ["coffee", "latte", "vanilla", "sweet", "iced", "milk"],
        "description": "달콤한 바닐라 향이 살아 있는 시그니처 라떼",
        "is_active": 1,
    },
    {
        "name": "핫 바닐라라떼",
        "group_name": "바닐라라떼",
        "temperature": "hot",
        "price": 4300,
        "category": "coffee",
        "sort_order": 30,
        "image_url": "https://images.unsplash.com/photo-1517701550927-30cf4ba1f4d0?auto=format&fit=crop&w=900&q=80",
        "tags": ["coffee", "latte", "vanilla", "sweet", "hot", "milk"],
        "description": "따뜻하고 달콤한 바닐라 향이 퍼지는 라떼",
        "is_active": 1,
    },
    {
        "name": "아이스 카라멜마키아또",
        "group_name": "카라멜마키아또",
        "temperature": "ice",
        "price": 4500,
        "category": "coffee",
        "sort_order": 40,
        "image_url": "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?auto=format&fit=crop&w=900&q=80",
        "tags": ["coffee", "caramel", "sweet", "iced", "milk", "dessert-like"],
        "description": "달콤한 카라멜 풍미가 살아 있는 차가운 커피",
        "is_active": 1,
    },
    {
        "name": "핫 카라멜마키아또",
        "group_name": "카라멜마키아또",
        "temperature": "hot",
        "price": 4500,
        "category": "coffee",
        "sort_order": 40,
        "image_url": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=900&q=80",
        "tags": ["coffee", "caramel", "sweet", "hot", "milk", "dessert-like"],
        "description": "달콤한 카라멜 향이 풍부한 따뜻한 커피",
        "is_active": 1,
    },
    {
        "name": "블루베리스무디",
        "group_name": "블루베리스무디",
        "temperature": "ice",
        "price": 4800,
        "category": "beverage",
        "sort_order": 50,
        "image_url": "https://images.unsplash.com/photo-1502741338009-cac2772e18bc?auto=format&fit=crop&w=900&q=80",
        "tags": ["beverage", "iced", "smoothie", "fruit", "blueberry", "sweet", "cold"],
        "description": "블루베리 풍미가 진하게 살아 있는 아이스 스무디",
        "is_active": 1,
    },
    {
        "name": "딸기라떼",
        "group_name": "딸기라떼",
        "temperature": "ice",
        "price": 4700,
        "category": "beverage",
        "sort_order": 60,
        "image_url": "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=900&q=80",
        "tags": ["beverage", "iced", "fruit", "strawberry", "milk", "sweet", "cold"],
        "description": "딸기와 우유가 어우러진 달콤한 아이스 라떼",
        "is_active": 1,
    },
    {
        "name": "녹차라떼",
        "group_name": "녹차라떼",
        "temperature": "ice",
        "price": 4600,
        "category": "beverage",
        "sort_order": 70,
        "image_url": "https://images.unsplash.com/photo-1515823064-d6e0c04616a7?auto=format&fit=crop&w=900&q=80",
        "tags": ["beverage", "iced", "matcha", "milk", "sweet", "cold", "green-tea"],
        "description": "부드러운 우유와 녹차 향이 어우러진 아이스 라떼",
        "is_active": 1,
    },
    {
        "name": "캐모마일",
        "group_name": "캐모마일",
        "temperature": "hot",
        "price": 3900,
        "category": "tea",
        "sort_order": 80,
        "image_url": "https://images.unsplash.com/photo-1544787219-7f47ccb76574?auto=format&fit=crop&w=900&q=80",
        "tags": ["tea", "hot", "calm", "floral", "chamomile", "not-sweet"],
        "description": "은은한 꽃향기로 편안하게 즐기는 따뜻한 티",
        "is_active": 1,
    },
    {
        "name": "녹차",
        "group_name": "녹차",
        "temperature": "hot",
        "price": 3900,
        "category": "tea",
        "sort_order": 90,
        "image_url": "https://images.unsplash.com/photo-1464305795204-6f5bbfc7fb81?auto=format&fit=crop&w=900&q=80",
        "tags": ["tea", "hot", "green-tea", "calm", "not-sweet"],
        "description": "깔끔하고 담백한 풍미가 좋은 따뜻한 녹차",
        "is_active": 1,
    },
    {
        "name": "유자차",
        "group_name": "유자차",
        "temperature": "hot",
        "price": 4200,
        "category": "tea",
        "sort_order": 100,
        "image_url": "https://images.unsplash.com/photo-1515823064-d6e0c04616a7?auto=format&fit=crop&w=900&q=80",
        "tags": ["tea", "hot", "citrus", "yuzu", "sweet", "calm"],
        "description": "상큼한 유자 향을 따뜻하게 즐기는 티",
        "is_active": 1,
    },
    {
        "name": "아이스 레몬에이드",
        "group_name": "레몬에이드",
        "temperature": "ice",
        "price": 4500,
        "category": "ade",
        "sort_order": 110,
        "image_url": "https://images.unsplash.com/photo-1497534446932-c925b458314e?auto=format&fit=crop&w=900&q=80",
        "tags": ["ade", "iced", "lemon", "citrus", "refreshing", "fruit", "cold"],
        "description": "레몬 향이 톡 쏘는 상큼한 아이스 에이드",
        "is_active": 1,
    },
    {
        "name": "핫 레몬에이드",
        "group_name": "레몬에이드",
        "temperature": "hot",
        "price": 4500,
        "category": "ade",
        "sort_order": 110,
        "image_url": "https://images.unsplash.com/photo-1556881286-fc6915169721?auto=format&fit=crop&w=900&q=80",
        "tags": ["ade", "hot", "lemon", "citrus", "refreshing", "fruit"],
        "description": "따뜻하게 즐기는 레몬 베이스 에이드",
        "is_active": 1,
    },
    {
        "name": "아이스 자몽에이드",
        "group_name": "자몽에이드",
        "temperature": "ice",
        "price": 4700,
        "category": "ade",
        "sort_order": 120,
        "image_url": "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=900&q=80",
        "tags": ["ade", "iced", "grapefruit", "fruit", "refreshing", "citrus", "cold"],
        "description": "자몽 풍미가 시원하게 살아 있는 에이드",
        "is_active": 1,
    },
    {
        "name": "핫 자몽에이드",
        "group_name": "자몽에이드",
        "temperature": "hot",
        "price": 4700,
        "category": "ade",
        "sort_order": 120,
        "image_url": "https://images.unsplash.com/photo-1542444459-db63c530c981?auto=format&fit=crop&w=900&q=80",
        "tags": ["ade", "hot", "grapefruit", "fruit", "citrus", "refreshing"],
        "description": "자몽 향을 따뜻하게 즐기는 에이드",
        "is_active": 1,
    },
    {
        "name": "아이스 청포도에이드",
        "group_name": "청포도에이드",
        "temperature": "ice",
        "price": 4700,
        "category": "ade",
        "sort_order": 130,
        "image_url": "https://images.unsplash.com/photo-1623065422902-30a2d299bbe4?auto=format&fit=crop&w=900&q=80",
        "tags": ["ade", "iced", "grape", "fruit", "refreshing", "sweet", "cold"],
        "description": "청포도의 산뜻한 풍미가 살아 있는 아이스 에이드",
        "is_active": 1,
    },
    {
        "name": "핫 청포도에이드",
        "group_name": "청포도에이드",
        "temperature": "hot",
        "price": 4700,
        "category": "ade",
        "sort_order": 130,
        "image_url": "https://images.unsplash.com/photo-1515823064-d6e0c04616a7?auto=format&fit=crop&w=900&q=80",
        "tags": ["ade", "hot", "grape", "fruit", "refreshing", "sweet"],
        "description": "청포도의 달콤함을 따뜻하게 즐기는 에이드",
        "is_active": 1,
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
    if "group_name" not in columns:
        cursor.execute("ALTER TABLE Menu ADD COLUMN group_name TEXT")
    if "temperature" not in columns:
        cursor.execute("ALTER TABLE Menu ADD COLUMN temperature TEXT")
    if "sort_order" not in columns:
        cursor.execute("ALTER TABLE Menu ADD COLUMN sort_order INTEGER DEFAULT 0")
    if "is_active" not in columns:
        cursor.execute("ALTER TABLE Menu ADD COLUMN is_active INTEGER DEFAULT 1")


def ensure_order_columns(cursor: sqlite3.Cursor) -> None:
    columns = {row[1] for row in cursor.execute("PRAGMA table_info(Orders)").fetchall()}
    if "order_channel" not in columns:
        cursor.execute("ALTER TABLE Orders ADD COLUMN order_channel TEXT")
    if "service_mode" not in columns:
        cursor.execute("ALTER TABLE Orders ADD COLUMN service_mode TEXT")
    if "payment_method" not in columns:
        cursor.execute("ALTER TABLE Orders ADD COLUMN payment_method TEXT")


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
            description TEXT,
            group_name TEXT,
            temperature TEXT,
            sort_order INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS Orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_price INTEGER NOT NULL,
            created_at TIMESTAMP NOT NULL,
            order_channel TEXT,
            service_mode TEXT,
            payment_method TEXT
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
    ensure_order_columns(cursor)

    serialized_menus = [
        {
            **menu,
            "tags": json.dumps(menu["tags"], ensure_ascii=False),
        }
        for menu in SEED_MENUS
    ]

    cursor.executemany(
        """
        INSERT INTO Menu (
            name,
            price,
            image_url,
            category,
            tags,
            description,
            group_name,
            temperature,
            sort_order,
            is_active
        )
        VALUES (
            :name,
            :price,
            :image_url,
            :category,
            :tags,
            :description,
            :group_name,
            :temperature,
            :sort_order,
            :is_active
        )
        ON CONFLICT(name) DO UPDATE SET
            price = excluded.price,
            image_url = excluded.image_url,
            category = excluded.category,
            tags = excluded.tags,
            description = excluded.description,
            group_name = excluded.group_name,
            temperature = excluded.temperature,
            sort_order = excluded.sort_order,
            is_active = excluded.is_active
        """,
        serialized_menus,
    )

    seed_names = [menu["name"] for menu in SEED_MENUS]
    placeholders = ", ".join("?" for _ in seed_names)
    cursor.execute(
        f"UPDATE Menu SET is_active = 0 WHERE name NOT IN ({placeholders})",
        seed_names,
    )

    connection.commit()
    connection.close()


if __name__ == "__main__":
    initialize_database()
    print(f"Database initialized at {DEFAULT_DB_PATH}")
