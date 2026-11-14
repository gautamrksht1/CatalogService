import os
from urllib.parse import quote

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_HOST = os.getenv("DB_HOST", "mysql")
DB_NAME = os.getenv("DB_NAME", "bookcatalog")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
if not DB_PASSWORD:
    raise RuntimeError("DB_PASSWORD environment variable must be set")
DB_PASSWORD = quote(DB_PASSWORD, safe="")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)