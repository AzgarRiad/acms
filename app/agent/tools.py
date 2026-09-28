"""
Tool functions the LLM can call.
Uses CSV files + pandas instead of a database.
"""

import json
import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data"

PRODUCTS_FILE = DATA_DIR / "products.csv"
ORDERS_FILE = DATA_DIR / "orders.csv"


def get_product_info(product_name: str) -> str:
    """Get the price of a GPU/PC product by name from the local product dataset.

    Args:
        product_name: Full or partial product name to search for,
                      e.g. 'RTX 5070 Ti'.

    Returns:
        str: A JSON string with matching products and their prices.
    """
    try:
        products = pd.read_csv(PRODUCTS_FILE)

        # Convert name column to string in case CSV contains unexpected values
        products["name"] = products["name"].astype(str)

        matches = products[
            products["name"].str.contains(
                product_name,
                case=False,
                na=False,
                regex=False
            )
        ]

        if matches.empty:
            return json.dumps({
                "error": f"No product found matching '{product_name}'"
            })

        results = [
            {
                "Product_Name": row["name"],
                "Price": float(row["price"])
            }
            for _, row in matches.iterrows()
        ]

        return json.dumps(results)

    except Exception as e:
        return json.dumps({
            "error": f"Failed to search products: {str(e)}"
        })


def get_products() -> list[dict]:
    """Gets all the available products.

    Returns:
        A list of products with id, name, category, and price.
    """
    try:
        products = pd.read_csv(PRODUCTS_FILE)

        return [
            {
                "id": int(row["id"]),
                "name": row["name"],
                "category": row["category"],
                "price": float(row["price"]),
            }
            for _, row in products.iterrows()
        ]

    except Exception as e:
        return [
            {
                "status": "error",
                "message": f"Failed to load products: {str(e)}"
            }
        ]


def add_order(
    customer_name: str,
    product_name: str,
    quantity: int
) -> dict:
    """Takes order from the customer.

    Args:
        customer_name: Customer name who wants to order.
        product_name: Name of the product that the customer wants to order.
        quantity: How many units the customer wants to order.
    """

    try:
        # Read existing orders
        if ORDERS_FILE.exists():
            orders = pd.read_csv(ORDERS_FILE)
        else:
            orders = pd.DataFrame(
                columns=[
                    "id",
                    "customer_name",
                    "product_name",
                    "quantity"
                ]
            )

        # Generate new order ID
        if orders.empty:
            order_id = 1
        else:
            order_id = int(orders["id"].max()) + 1

        # Create new order
        new_order = pd.DataFrame([{
            "id": order_id,
            "customer_name": customer_name,
            "product_name": product_name,
            "quantity": quantity,
        }])

        # Add order to existing orders
        orders = pd.concat(
            [orders, new_order],
            ignore_index=True
        )

        # Save back to CSV
        ORDERS_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        orders.to_csv(
            ORDERS_FILE,
            index=False
        )

        return {
            "status": "success",
            "order_id": order_id,
            "customer_name": customer_name,
            "product_name": product_name,
            "quantity": quantity,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to save order: {str(e)}"
        }


AVAILABLE_TOOLS = {
    "get_product_info": get_product_info,
    "add_order": add_order,
    "get_products": get_products,
}