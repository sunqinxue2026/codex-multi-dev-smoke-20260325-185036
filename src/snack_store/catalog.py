from __future__ import annotations

from copy import deepcopy

SNACKS = [
    {
        "id": 1,
        "name": "海盐黄油薯片",
        "category": "膨化精选",
        "price": 16,
        "stock": 38,
        "image": "🥔",
        "rating": 4.8,
        "featured": True,
        "spicy_level": 0,
        "origin": "北海道",
        "description": "厚切波浪薯片配海盐黄油粉，入口酥脆、咸香平衡。",
        "tags": ["热销", "办公室常备", "轻咸"],
    },
    {
        "id": 2,
        "name": "抹茶夹心曲奇",
        "category": "烘焙甜点",
        "price": 22,
        "stock": 26,
        "image": "🍪",
        "rating": 4.9,
        "featured": True,
        "spicy_level": 0,
        "origin": "京都",
        "description": "微苦抹茶搭配牛乳夹心，层次细腻，适合下午茶。",
        "tags": ["新品", "人气下午茶", "抹茶控"],
    },
    {
        "id": 3,
        "name": "草莓气泡软糖",
        "category": "糖果果脯",
        "price": 12,
        "stock": 52,
        "image": "🍓",
        "rating": 4.6,
        "featured": False,
        "spicy_level": 0,
        "origin": "静冈",
        "description": "外层细砂包裹果汁软芯，酸甜清爽，越嚼越有果香。",
        "tags": ["低负担", "果味", "儿童友好"],
    },
    {
        "id": 4,
        "name": "芝士玉米棒",
        "category": "膨化精选",
        "price": 18,
        "stock": 19,
        "image": "🌽",
        "rating": 4.5,
        "featured": False,
        "spicy_level": 1,
        "origin": "名古屋",
        "description": "空气感膨化口感配浓郁芝士粉，追剧时最容易停不下来。",
        "tags": ["追剧必备", "浓郁芝士", "轻辣"],
    },
    {
        "id": 5,
        "name": "炭烧海苔脆片",
        "category": "轻食海味",
        "price": 14,
        "stock": 41,
        "image": "🌿",
        "rating": 4.7,
        "featured": True,
        "spicy_level": 0,
        "origin": "釜山",
        "description": "海苔与糙米脆片轻烘焙，口感酥薄，咬下去带一点海盐回甘。",
        "tags": ["低卡", "海味", "轻食"],
    },
    {
        "id": 6,
        "name": "焦糖坚果燕麦杯",
        "category": "轻食海味",
        "price": 20,
        "stock": 17,
        "image": "🥣",
        "rating": 4.4,
        "featured": False,
        "spicy_level": 0,
        "origin": "首尔",
        "description": "燕麦、杏仁和腰果混合焦糖浆，脆感与饱腹感都很在线。",
        "tags": ["早餐友好", "坚果", "饱腹"],
    },
    {
        "id": 7,
        "name": "青柠椒盐鱿鱼圈",
        "category": "轻食海味",
        "price": 26,
        "stock": 14,
        "image": "🦑",
        "rating": 4.8,
        "featured": True,
        "spicy_level": 2,
        "origin": "高雄",
        "description": "青柠清香和椒盐微辣组合，海味明显，适合作为夜宵零嘴。",
        "tags": ["下酒", "海鲜风味", "微辣"],
    },
    {
        "id": 8,
        "name": "黑糖麻薯夹心派",
        "category": "烘焙甜点",
        "price": 24,
        "stock": 21,
        "image": "🥮",
        "rating": 4.7,
        "featured": False,
        "spicy_level": 0,
        "origin": "台中",
        "description": "黑糖香气浓厚，咬开后有柔软麻薯夹心，甜度适中。",
        "tags": ["软糯", "黑糖", "分享装"],
    },
]


def clone_snack(snack: dict) -> dict:
    return deepcopy(snack)


def list_snacks(
    *,
    category: str = "",
    search: str = "",
    sort: str = "featured",
    featured_only: bool = False,
) -> list[dict]:
    items = [clone_snack(snack) for snack in SNACKS]

    if category and category != "全部":
        items = [item for item in items if item["category"] == category]

    if search:
        keyword = search.strip().lower()
        items = [
            item
            for item in items
            if keyword in item["name"].lower()
            or keyword in item["description"].lower()
            or any(keyword in tag.lower() for tag in item["tags"])
        ]

    if featured_only:
        items = [item for item in items if item["featured"]]

    if sort == "price_asc":
        items.sort(key=lambda item: (item["price"], -item["rating"]))
    elif sort == "price_desc":
        items.sort(key=lambda item: (-item["price"], -item["rating"]))
    elif sort == "rating":
        items.sort(key=lambda item: (-item["rating"], item["price"]))
    elif sort == "stock":
        items.sort(key=lambda item: (-item["stock"], -item["rating"]))
    else:
        items.sort(
            key=lambda item: (
                not item["featured"],
                -item["rating"],
                item["price"],
            )
        )

    return items


def get_snack(snack_id: int) -> dict | None:
    for snack in SNACKS:
        if snack["id"] == snack_id:
            return clone_snack(snack)
    return None


def categories() -> list[dict]:
    counts: dict[str, int] = {}
    for snack in SNACKS:
        counts[snack["category"]] = counts.get(snack["category"], 0) + 1
    return [
        {"name": name, "count": counts[name]}
        for name in sorted(counts)
    ]


def spotlight_snacks() -> list[dict]:
    return [
        clone_snack(snack)
        for snack in sorted(
            SNACKS,
            key=lambda item: (not item["featured"], -item["rating"], item["price"]),
        )[:3]
    ]
