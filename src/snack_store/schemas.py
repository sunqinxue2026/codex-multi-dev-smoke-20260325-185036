from pydantic import BaseModel, Field


class Snack(BaseModel):
    id: int
    name: str
    category: str
    price: int
    stock: int
    image: str
    rating: float
    featured: bool
    spicy_level: int
    origin: str
    description: str
    tags: list[str]


class CategorySummary(BaseModel):
    name: str
    count: int


class CatalogResponse(BaseModel):
    items: list[Snack]
    total: int


class CatalogMetaResponse(BaseModel):
    categories: list[CategorySummary]
    spotlight: list[Snack]


class OrderItem(BaseModel):
    id: int
    quantity: int = Field(..., ge=1, le=20)


class OrderRequest(BaseModel):
    items: list[OrderItem]


class OrderLineResponse(BaseModel):
    id: int
    name: str
    quantity: int
    unit_price: int
    line_total: int


class OrderResponse(BaseModel):
    message: str
    order_id: str
    total_items: int
    subtotal: int
    shipping_fee: int
    discount: int
    total_price: int
    eta_minutes: int
    items: list[OrderLineResponse]
    recommendations: list[Snack]
