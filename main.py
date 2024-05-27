from fastapi import FastAPI, Depends, HTTPException, Request, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.orm import Session
from typing import List
from datetime import date
import shemas
import database
import json

app = FastAPI()

templates = Jinja2Templates(directory="templates")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    food_items = db.query(database.FoodItem).all()
    purchase_history = db.query(database.PurchaseHistory).all()
    return templates.TemplateResponse("index.html", {"request": request, "food_items": food_items, "purchase_history": purchase_history})

@app.post("/food_items/", response_model=shemas.FoodItem)
def create_food_item(food_item: shemas.FoodItem, db: Session = Depends(get_db)):
    db_food_item = database.FoodItem(name=food_item.name, quantity=food_item.quantity)
    db.add(db_food_item)
    db.commit()
    db.refresh(db_food_item)
    return db_food_item.__dict__

@app.get("/food_items/", response_model=List[shemas.FoodItem])
def read_food_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    food_items = db.query(database.FoodItem).offset(skip).limit(limit).all()
    return [food_item.__dict__ for food_item in food_items]

@app.put("/food_items/{id}", response_model=shemas.FoodItem)
def update_food_item(id: int, food_item: shemas.FoodItem, db: Session = Depends(get_db)):
    db_food_item = db.query(database.FoodItem).filter(database.FoodItem.id == id).first()
    if not db_food_item:
        raise HTTPException(status_code=404, detail="Food item not found")
    db_food_item.name = food_item.name
    db_food_item.quantity = food_item.quantity
    db.commit()
    db.refresh(db_food_item)
    return db_food_item.__dict__

@app.delete("/food_items/{id}", response_model=shemas.FoodItem)
def delete_food_item(id: int, db: Session = Depends(get_db)):
    db_food_item = db.query(database.FoodItem).filter(database.FoodItem.id == id).first()
    if not db_food_item:
        raise HTTPException(status_code=404, detail="Food item not found")
    db.delete(db_food_item)
    db.commit()
    return db_food_item.__dict__

@app.post("/food_items/upload_receipt")
async def upload_receipt(file: UploadFile = File(...), db: Session = Depends(get_db)):
    food_items = db.query(database.FoodItem).all()
    if not food_items:
        raise HTTPException(status_code=404, detail="No food items found")
    
    items = [{"id": item.id, "name": item.name, "quantity": item.quantity} for item in food_items]
    purchase_date = date.today()
    receipt_content = await file.read()
    
    db_purchase_history = database.PurchaseHistory(
        purchase_date=purchase_date, 
        items=json.dumps(items), 
        receipt=receipt_content
    )
    
    db.add(db_purchase_history)
    db.query(database.FoodItem).delete()
    db.commit()
    return {"message": "Receipt uploaded and food items archived successfully"}

@app.get("/purchase_history/{id}/receipt", response_class=Response)
def get_purchase_receipt(id: int, db: Session = Depends(get_db)):
    db_purchase_history = db.query(database.PurchaseHistory).filter(database.PurchaseHistory.id == id).first()
    if not db_purchase_history or not db_purchase_history.receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return Response(content=db_purchase_history.receipt, media_type="application/pdf")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)