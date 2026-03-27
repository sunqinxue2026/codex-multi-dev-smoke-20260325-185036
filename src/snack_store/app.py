from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .catalog import categories, get_snack, list_snacks, spotlight_snacks
from .schemas import (
    CatalogMetaResponse,
    CatalogResponse,
    OrderLineResponse,
    OrderRequest,
    OrderResponse,
    Snack,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIST = REPO_ROOT / "frontend" / "dist"
FRONTEND_INDEX = FRONTEND_DIST / "index.html"
FREE_SHIPPING_THRESHOLD = 69

app = FastAPI(title="Snack Store API", version="0.3.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def healthcheck():
    return {
        "status": "ok",
        "version": app.version,
        "service": "snack-store",
        "catalog_size": len(list_snacks()),
    }


@app.get("/api/snacks", response_model=CatalogResponse)
def get_snacks(
    category: str = Query(default="", description="分类筛选"),
    search: str = Query(default="", description="搜索词"),
    sort: str = Query(default="featured", description="排序方式"),
    featured: bool = Query(default=False, description="只看主推"),
):
    items = list_snacks(
        category=category,
        search=search,
        sort=sort,
        featured_only=featured,
    )
    return {"items": items, "total": len(items)}


@app.get("/api/snacks/meta", response_model=CatalogMetaResponse)
def get_snack_meta():
    return {
        "categories": categories(),
        "spotlight": spotlight_snacks(),
    }


@app.get("/api/snacks/{snack_id}", response_model=Snack)
def get_snack_detail(snack_id: int):
    snack = get_snack(snack_id)
    if not snack:
        raise HTTPException(status_code=404, detail="Snack not found")
    return snack


@app.post("/api/orders", response_model=OrderResponse)
def create_order(order: OrderRequest):
    if not order.items:
        raise HTTPException(status_code=400, detail="Order is empty")

    lines: list[OrderLineResponse] = []
    total_items = 0
    subtotal = 0

    for item in order.items:
        snack = get_snack(item.id)
        if not snack:
            raise HTTPException(status_code=404, detail=f"Snack {item.id} not found")
        if item.quantity > snack["stock"]:
            raise HTTPException(
                status_code=400,
                detail=f"{snack['name']} 库存不足，当前仅剩 {snack['stock']} 件",
            )

        line_total = snack["price"] * item.quantity
        subtotal += line_total
        total_items += item.quantity
        lines.append(
            OrderLineResponse(
                id=snack["id"],
                name=snack["name"],
                quantity=item.quantity,
                unit_price=snack["price"],
                line_total=line_total,
            )
        )

    discount = 12 if subtotal >= 120 else 0
    shipping_fee = 0 if subtotal >= FREE_SHIPPING_THRESHOLD else 8
    total_price = subtotal + shipping_fee - discount
    eta_minutes = 30 if total_items <= 4 else 45
    order_id = f"SNK-{datetime.now(timezone.utc).strftime('%m%d%H%M')}-{total_items}"

    recommendation_pool = [
        snack for snack in spotlight_snacks() if snack["id"] not in {line.id for line in lines}
    ]

    return {
        "message": "order_created",
        "order_id": order_id,
        "total_items": total_items,
        "subtotal": subtotal,
        "shipping_fee": shipping_fee,
        "discount": discount,
        "total_price": total_price,
        "eta_minutes": eta_minutes,
        "items": lines,
        "recommendations": recommendation_pool[:2],
    }


@app.get("/", include_in_schema=False)
def serve_home():
    if FRONTEND_INDEX.exists():
        return FileResponse(FRONTEND_INDEX)
    return {"message": "Snack Store API", "frontend": "not_built"}


@app.get("/{asset_path:path}", include_in_schema=False)
def serve_frontend(asset_path: str):
    if asset_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not Found")

    if not FRONTEND_DIST.exists():
        raise HTTPException(status_code=404, detail="Frontend build not found")

    dist_root = FRONTEND_DIST.resolve()
    candidate = (dist_root / asset_path).resolve()
    try:
        candidate.relative_to(dist_root)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Not Found") from exc

    if candidate.is_file():
        return FileResponse(candidate)

    if "." not in asset_path and FRONTEND_INDEX.exists():
        return FileResponse(FRONTEND_INDEX)

    raise HTTPException(status_code=404, detail="Not Found")
