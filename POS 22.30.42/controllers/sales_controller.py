from controllers.product_controller import update_stock

def record_sale(product_id, quantity_sold):
    """Record a sale and reduce stock quantity."""
    try:
        update_stock(product_id, -quantity_sold)
        print(f"Sale recorded for product ID '{product_id}'. Quantity sold: {quantity_sold}.")
    except Exception as e:
        print(f"Error recording sale: {e}")