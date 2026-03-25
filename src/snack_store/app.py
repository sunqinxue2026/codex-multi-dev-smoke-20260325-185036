from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .catalog import list_snacks
from .schemas import OrderRequest, OrderResponse, Snack

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
    return {"status": "ok"}

@app.get("/api/snacks", response_model=dict[str, list[Snack]])
def get_snacks():
    return {"items": list_snacks()}

@app.post("/api/orders", response_model=OrderResponse)
def create_order(order: OrderRequest):
    total_items = sum(item.quantity for item in order.items)
    return OrderResponse(message="order_created", total_items=total_items)
