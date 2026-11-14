from pathlib import Path
import sys
import time

from fastapi import FastAPI
from pydantic import BaseModel, Field
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

class BookCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    author: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)
    available_quantity: int = Field(ge=0)


@app.post("/books", status_code=201)
def create_book(request: BookCreateRequest):
    db = SessionLocal()
    try:
        book = Book(
            title=request.title.strip(),
            author=request.author.strip(),
            price=request.price,
            available_quantity=request.available_quantity,
        )
        db.add(book)
        db.commit()
        db.refresh(book)
        return {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "price": book.price,
            "available_quantity": book.available_quantity,
        }
    finally:
        db.close()

@app.get("/books")
def get_books():
    db = SessionLocal()
    try:
        return db.query(Book).all()
    finally:
        db.close()

@app.get("/books/{book_id}")
def get_book(book_id:int):
    db = SessionLocal()
    try:
        book = db.query(Book)\
                 .filter(Book.id == book_id)\
                 .first()

        if not book:
            return {"message":"Book Not Found"}

        return book
    finally:
        db.close()

@app.post("/inventory/reserve")
def reserve_stock(request:InventoryRequest):
    db = SessionLocal()
    try:
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
                "message": "Insufficient stock"
            }

        return {
            "success": True
        }
    finally:
        db.close()