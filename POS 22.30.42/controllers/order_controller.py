from firebase_config import db
import tkinter as tk

# Fetch all orders
def fetch_orders(time_filter=None):
    orders_ref = db.collection("orders").stream()
    orders = []
    for order in orders_ref:
        order_data = order.to_dict()
        order_data["order_id"] = order.id  # Add order_id manually
        order_data["date"] = order_data.get("date_time", "N/A")  # Use date_time instead of date
        order_data["total_price"] = order_data.get("total_amount", 0)  # total_amount is now total_price
        orders.append(order_data)
    return orders

def clear_new_order_fields(store_selection,product_entry, product_search_entry,quantity_entry):
    """Clear all input fields and the cart in the New Order tab."""
    # Clear the bill number entry
        
    store_selection.set("")
    product_entry.delete(0,tk.END)
    product_search_entry.delete(0, tk.END)
    quantity_entry.delete(0, tk.END)

    print("New Order fields cleared!")


# Save an order
def save_order(bill_number, order_details, total):
    """Save the current order to the database and update product quantities."""
    from datetime import datetime
    import tkinter.messagebox as messagebox

    # Check if total is 0
    try:
        total = float(total)  # Convert total to a float
        if total <= 0:
            messagebox.showerror("Error", "The total amount cannot be empty.")
            return
    except ValueError:
        messagebox.showerror("Error", "Invalid total amount. Please ensure the total is a valid number.")
        return

    # Proceed with saving the order
    current_datetime = datetime.now()
    date_time_str = current_datetime.strftime("%Y%m%d%H%M%S")  # Format: YYYYMMDDHHMMSS
    order_id = f"{date_time_str}-{bill_number}"
    order_data = {
        "bill number": bill_number,
        "date_time": current_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        "total_amount": float(total),  # Ensure it's stored as a number
        "items": [
            {
                "product_id": item["id"],
                "name": item["name"],
                "quantity": item["quantity"],
                "price": item["item_total"],
                "store_location": item["store_location"]  # Include store location in order details
            }
            for item in order_details
        ]
    }

    try:
        # Update product quantities in the database
        for item in order_details:
            product_id = item["id"]
            quantity_sold = item["quantity"]
            store_key = f"quantity_{item['store_location'].replace(' ', '_')}"  # e.g., "quantity_store_1" or "quantity_store_2"

            # Retrieve the product document
            product_ref = db.collection("products").document(product_id)
            product = product_ref.get()

            if product.exists:
                product_data = product.to_dict()
                current_quantity = product_data.get(store_key, 0)

                # Check if sufficient stock is available
                if current_quantity >= quantity_sold:
                    new_quantity = current_quantity - quantity_sold
                    product_ref.update({store_key: new_quantity})
                else:
                    messagebox.showerror("Error", f"Not enough stock for product ID {product_id} in {item['store_location']}.")
                    return
            else:
                messagebox.showerror("Error", f"Product ID {product_id} not found in the database.")
                return
        
        # Save the order to the database
        db.collection("orders").document(order_id).set(order_data)
        messagebox.showinfo("Success", "Order saved successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to save order or update stock: {e}")


# Fetch order details
def fetch_order_details(order_id):
    order_ref = db.collection("orders").document(order_id)
    order = order_ref.get()
    if order.exists:
        return order.to_dict()
    else:
        raise ValueError(f"Order with ID '{order_id}' does not exist.")