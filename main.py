from pathlib import Path
import sys
import time

from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from database import SessionLocal, engine
from models import Base, Book
from inventory import InventoryRequest


def ensure_database_ready():
    for _ in range(30):
        try:
            Base.metadata.create_all(bind=engine)
            return
        except OperationalError:
            time.sleep(2)
    raise RuntimeError("Database is not ready")


ensure_database_ready()

app = FastAPI()

@app.get("/books")
def get_books():

    db = SessionLocal()

    books = db.query(Book).all()

    return books

@app.get("/books/{book_id}")
def get_book(book_id:int):

    db = SessionLocal()

    book = db.query(Book)\
             .filter(Book.id == book_id)\
             .first()

    if not book:
        return {"message":"Book Not Found"}

    return book

@app.post("/inventory/reserve")
def reserve_stock(request:InventoryRequest):

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