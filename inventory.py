from pydantic import BaseModel

class InventoryRequest(BaseModel):
    book_id: int
    quantity: int