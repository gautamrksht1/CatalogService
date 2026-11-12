from sqlalchemy import *
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Book(Base):

    __tablename__ = "books"

    id = Column(Integer, primary_key=True)

    title = Column(String(150))

    author = Column(String(100))

    price = Column(Float)

    available_quantity = Column(Integer)