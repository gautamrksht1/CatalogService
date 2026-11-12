from fastapi import APIRouter
from sqlalchemy import text

from database import SessionLocal
from inventory import InventoryRequest

router = APIRouter()

@router.post("/inventory/reserve")
def reserve_stock(
        request: InventoryRequest):

    db = SessionLocal()

    result = db.execute(
        text("""
        UPDATE books
        SET available_quantity =
            available_quantity - :qty

        WHERE id = :book_id

        AND available_quantity >= :qty
        """),
        {
            "qty": request.quantity,
            "book_id": request.book_id
        }
    )

    db.commit()

    if result.rowcount == 0:

        return {
            "success": False,
            "message":
            "Insufficient stock"
        }

    return {
        "success": True
    }