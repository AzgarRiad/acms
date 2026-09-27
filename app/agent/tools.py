"""
Tool functions the LLM can call.
"""
import json
from app.agent.database import session
from app.agent.database_models import Product, Order
def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()


def get_product_info(product_name: str) -> str: #db: Session = Depends(get_db)
    """Get the price of a GPU/PC product by name from the local product dataset.

    Args:
        product_name: Full or partial product name to search for, e.g. 'RTX 5070 Ti'.

    Returns:
        str: A JSON string with matching products and their prices.
    """
    try:
        db = session()
        matches = (
            db.query(Product)
            .filter(Product.name.ilike(f"%{product_name}%"))
            .all()
        )
    finally:
        db.close()
 
    if not matches:
        return json.dumps({"error": f"No product found matching '{product_name}'"})
 
    results = [
        {"Product_Name": row.name, "Price": float(row.price)}
        for row in matches
    ]
    return json.dumps(results)

def get_products() -> list[dict]:
    """Gets all the available products.

    Returns:
        A list of products with id, name, category, price.
    """#, and stock quantity.
    db = session()
    try:
        products = db.query(Product).all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "category": p.category,
                "price": float(p.price)
                #"stock_quantity": p.stock_quantity,
            }
            for p in products
        ]
    finally:
        db.close()

def add_order(customer_name: str, product_name: str, quantity: int) -> dict:
    """Takes order from the customer
    
    Args: 
        customer_name: Takes customer name who wants to order.
        product_name: Name of the product that the customer wants to order.
        Quantity: How many does the customer wants to order.
    """
    db = session()
    try:
        order = Order(
            customer_name=customer_name,
            product_name=product_name,
            quantity=quantity,
        )
        db.add(order)
        db.commit()
        db.refresh(order)  # loads generated fields like id

        return {
            "status": "success",
            "order_id": order.id,
            "customer_name": order.customer_name,
            "product_name": order.product_name,
            "quantity": order.quantity,
        }
    except Exception as e:
        db.rollback()  # undo the partial transaction
        return {"status": "error", "message": f"Failed to save order: {e}"}
    finally:
        db.close()  # always release the connectio

AVAILABLE_TOOLS = {
    "get_product_info": get_product_info,
    "add_order": add_order,
    "get_products": get_products
}