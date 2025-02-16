from firebase_config import db


#----------------------------------#
   #----- Admin Activities -----#
#----------------------------------#


# Add a product
def add_product_with_custom_id(product_id, product_data):
    db.collection("products").document(product_id).set(product_data)

# Get all products
def get_all_products():
    docs = db.collection("products").stream()
    return {doc.id: doc.to_dict() for doc in docs}

# Delete a product
def delete_product(product_id):
    db.collection("products").document(product_id).delete()

# Update a product
def update_product(product_id, updated_data):
    db.collection("products").document(product_id).update(updated_data)

# Update stock
def update_stock(product_id, quantity_change, store_location):
    """
    Update the stock quantity for a specific store.

    :param product_id: ID of the product to update.
    :param quantity_change: The amount to increase or decrease the stock.
    :param store_location: The store location ('Store 1' or 'Store 2').
    :return: None or raises an exception on error.
    """
    try:
        store_key = f"quantity_{store_location.lower().replace(' ', '_')}"
        if store_location not in ["Store 1", "Store 2"]:
            raise ValueError(f"Invalid store location '{store_location}'.")

        product_ref = db.collection("products").document(product_id)
        product = product_ref.get()
        if not product.exists:
            raise ValueError(f"Product with ID '{product_id}' does not exist.")

        product_data = product.to_dict()

        # Validate store key exists
        if store_key not in product_data:
            raise KeyError(f"Store key '{store_key}' does not exist in product data.")

        # Update the stock
        current_quantity = product_data[store_key]
        new_quantity = current_quantity + quantity_change
        if new_quantity < 0:
            raise ValueError(f"Insufficient stock in {store_location}. Current stock: {current_quantity}.")

        product_ref.update({store_key: new_quantity})
    except Exception as e:
        raise e

def deduct_stock(product_id, quantity_change, store_location):
    """
    Update the stock quantity for a specific store.

    :param product_id: ID of the product to update.
    :param quantity_change: The amount to increase or decrease the stock.
    :param store_location: The store location ('Store 1' or 'Store 2').
    :return: None or raises an exception on error.
    """
    try:
        store_key = f"quantity_{store_location.lower().replace(' ', '_')}"
        product_ref = db.collection("products").document(product_id)
        product = product_ref.get()
        if not product.exists:
            raise ValueError(f"Product with ID '{product_id}' does not exist.")

        product_data = product.to_dict()

        # Validate store key exists
        if store_key not in product_data:
            raise KeyError(f"Store key '{store_key}' does not exist in product data.")

        # Update the stock
        current_quantity = product_data[store_key]
        new_quantity = int(current_quantity) - quantity_change
        if new_quantity < 0:
            raise ValueError(f"Insufficient stock in {store_location}. Current stock: {current_quantity}.")

        product_ref.update({store_key: new_quantity})
    except Exception as e:
        raise e


def add_stock_in_order(stock_order_data):
    #"""
    #Adds a stock-in order to the database and updates product quantities.

    #Args:
    #    stock_order_data (dict): Contains details about the stock-in order.
    #        Example:
    #        {
    #            "order_id": "20250105123456-INV001",
    #            "total_price_after_discount": 1500.0,
    #            "items": [
    #                {
    #                    "product_id": "P001",
    #                    "name": "Product Name",
    #                    "unit_price": 100.0,
    #                    "total_quantity": 10,
    #                    "quantity_store_1": 5,
    #                    "quantity_store_2": 5,
    #                },
    #                ...
    #            ]
    #        }
    #"""
    try:
        # Save stock-in order
        orders_ref = db.collection("stock_in_orders")
        orders_ref.document(stock_order_data["order_id"]).set(stock_order_data)

        # Update product quantities
        for item in stock_order_data["items"]:
            product_id = item["product_id"]
            qty_store_1 = item["quantity_store_1"]
            qty_store_2 = item["quantity_store_2"]

            # Reference the product document
            product_ref = db.collection("products").document(product_id)
            product = product_ref.get()

            if product.exists:
                product_data = product.to_dict()

                # Get current quantities or default to 0 if not present
                current_qty_store_1 = product_data.get("quantity_store_1")
                current_qty_store_2 = product_data.get("quantity_store_2")
                # Calculate new quantities
                new_qty_store_1 = int(current_qty_store_1) + int(qty_store_1)
                new_qty_store_2 = int(current_qty_store_2) + int(qty_store_2)
                # Update the product document with new quantities
                product_ref.update({
                    "quantity_store_1": int(new_qty_store_1),
                    "quantity_store_2": int(new_qty_store_2),
                })
            else:
                print(f"Product ID {product_id} not found in the database. Skipping update.")

        print(f"Stock-in order {stock_order_data['order_id']} added successfully!")

    except Exception as e:
        print(f"Error adding stock-in order: {e}")
        raise
#----------------------------------#
 #----- Cashier Activities -----#
#----------------------------------#


# Fetch all products for display
def fetch_all_products():
    """Fetch all products to display in the cashier application."""
    docs = db.collection("products").stream()
    return {doc.id: doc.to_dict() for doc in docs}

# Fetch orders
def fetch_orders(time_filter=None):
    """
    Fetch orders based on a time filter.
    
    :param time_filter: None (today), 'last_week', 'last_month' for filtering.
    :return: List of orders.
    """
    orders_ref = db.collection("orders")
    query = orders_ref

    if time_filter == "last_week":
        # Example: Filter based on timestamp (adjust accordingly)
        # import datetime and calculate the date for the last 7 days
        import datetime
        import firebase_admin
        last_week = datetime.datetime.now() - datetime.timedelta(days=7)
        query = query.where("date", ">=", last_week)
    elif time_filter == "last_month":
        last_month = datetime.datetime.now() - datetime.timedelta(days=30)
        query = query.where("date", ">=", last_month)

    docs = query.stream()
    return [{"order_id": doc.id, **doc.to_dict()} for doc in docs]

# Save an order
def save_order(order_data):
    """
    Save a new order to Firebase.
    
    :param order_data: Dictionary containing order details.
    :return: None
    """
    orders_ref = db.collection("orders")
    order_id = orders_ref.document().id
    orders_ref.document(order_id).set(order_data)

# Process a product return
def process_return(order_id, product_id, return_quantity, store_location):
    """
    Handle product returns and adjust inventory.
    
    :param order_id: ID of the order.
    :param product_id: ID of the product being returned.
    :param return_quantity: Quantity of product to return.
    :param store_location: The store location ('Store 1' or 'Store 2').
    :return: None
    """
    try:
        # Verify the order exists
        order_ref = db.collection("orders").document(order_id)
        order = order_ref.get()
        if not order.exists:
            raise ValueError(f"Order with ID '{order_id}' does not exist.")

        # Update stock for the returned product
        update_stock(product_id, return_quantity, store_location)

        # Log the return (Optional: Adjust order record or create a returns log)
        return_ref = db.collection("returns")
        return_id = return_ref.document().id
        return_data = {
            "order_id": order_id,
            "product_id": product_id,
            "return_quantity": return_quantity,
            "store_location": store_location,
            "date": db.ServerValue.TIMESTAMP,
        }
        return_ref.document(return_id).set(return_data)
        ###
        '''
        product_ref = db.collection("products").document(product_id)
        product = product_ref.get()
        if not product.exists:
            raise ValueError(f"Product with ID '{product_id}' does not exist.")

        product_data = product.to_dict()

        # Update the stock
        current_quantity = product_data[store_location]
        new_quantity = current_quantity + quantity_change
        if new_quantity < 0:
            raise ValueError(f"Insufficient stock in {store_location}. Current stock: {current_quantity}.")

        product_ref.update({store_key: new_quantity})
        '''
        ###
    except Exception as e:
        raise e