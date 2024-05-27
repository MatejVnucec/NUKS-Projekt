from pydantic import BaseModel
from typing import Optional
from datetime import date

class FoodItem(BaseModel):
    id: Optional[int]
    name: str
    quantity: int
    receipt: Optional[bytes]

class PurchaseHistory(BaseModel):
    id: Optional[int]
    purchase_date: date
    items: list[FoodItem]
    receipt: Optional[bytes]