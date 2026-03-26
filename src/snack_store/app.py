from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .catalog import list_snacks
from .schemas import OrderRequest, OrderResponse, Snack

REPO_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIST = REPO_ROOT / "frontend" / "dist"
FRONTEND_INDEX = FRONTEND_DIST / "index.html"

app = FastAPI(title="Snack Store API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def healthcheck():
    return {"status": "ok", "version": app.version}

@app.get("/api/snacks", response_model=dict[str, list[Snack]])
def get_snacks():
    return {"items": list_snacks()}

@app.post("/api/orders", response_model=OrderResponse)
def create_order(order: OrderRequest):
    total_items = sum(item.quantity for item in order.items)
    return OrderResponse(message="order_created", total_items=total_items)


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
