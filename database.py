from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import json

DATABASE_URL = "sqlite:///./mydotabase.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class FoodItem(Base):
    __tablename__ = "food_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    quantity = Column(Integer)
    receipt = Column(LargeBinary)

class PurchaseHistory(Base):
    __tablename__ = "purchase_history"
    id = Column(Integer, primary_key=True, index=True)
    purchase_date = Column(Date)
    items = Column(String)  # We'll store JSON serialized items
    receipt = Column(LargeBinary)

Base.metadata.create_all(bind=engine)