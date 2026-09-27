from fastapi import FastAPI
from app.agent.database import session
from app.agent import database_models
app = FastAPI()

@app.get("/")
def root():
    return {"server":"ok"}
@app.get("/products")
def get_products():
    try:
        db = session()
        products = db.query(database_models.Product).all()
    finally:
        db.close()
    return products
