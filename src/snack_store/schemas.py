from pydantic import BaseModel

class Snack(BaseModel):
    id: int
    name: str
    price: int
    stock: int
    image: str

class OrderItem(BaseModel):
    id: int
    quantity: int

class OrderRequest(BaseModel):
    items: list[OrderItem]

class OrderResponse(BaseModel):
    message: str
    total_items: int
