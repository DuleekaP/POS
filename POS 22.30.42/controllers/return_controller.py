from firebase_config import db
from controllers.product_controller import update_stock

def process_return(order_id, product_id, return_quantity, store_location):
    try:
        # Verify order exists
        order_ref = db.collection("orders").document(order_id)
        order = order_ref.get()
        if not order.exists():
            raise ValueError(f"Order with ID '{order_id}' does not exist.")

        # Update stock
        update_stock(product_id, return_quantity, store_location)

        # Log the return
        return_ref = db.collection("returns")
        return_id = return_ref.document().id
        return_data = {
            "order_id": order_id,
            "product_id": product_id,
            "return_quantity": return_quantity,
            "store_location": store_location,
            "date": db.SERVER_TIMESTAMP,
        }
        return_ref.document(return_id).set(return_data)
        return return_id
    except Exception as e:
        raise e