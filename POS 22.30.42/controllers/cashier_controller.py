import tkinter as tk
from tkinter import ttk, messagebox
from controllers.product_controller import get_all_products
from controllers.order_controller import create_order, get_orders
from controllers.return_controller import handle_return
from services.memory_store import memory_store

def refresh_product_list():
    """Refresh the product list in the table."""
    product_table.delete(*product_table.get_children())
    products = get_all_products()
    for product_id, product_data in products.items():
        product_table.insert(
            "",
            "end",
            iid=product_id,
            values=(
                product_id,
                product_data["name"],
                product_data["quantity_store_1"],
                product_data["quantity_store_2"],
            ),
        )

def search_products():
    """Search products based on the search bar input."""
    query = search_entry.get().lower()
    product_table.delete(*product_table.get_children())
    products = get_all_products()
    for product_id, product_data in products.items():
        if query in product_data["name"].lower() or query in product_id.lower():
            product_table.insert(
                "",
                "end",
                iid=product_id,
                values=(
                    product_id,
                    product_data["name"],
                    product_data["quantity_store_1"],
                    product_data["quantity_store_2"],
                ),
            )

def make_order():
    """Open a window for making an order."""
    order_window = tk.Toplevel(root)
    order_window.title("Make Order")
    order_window.geometry("400x400")
    
    tk.Label(order_window, text="Product ID:").grid(row=0, column=0, padx=10, pady=5)
    product_id_entry = tk.Entry(order_window)
    product_id_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(order_window, text="Quantity:").grid(row=1, column=0, padx=10, pady=5)
    quantity_entry = tk.Entry(order_window)
    quantity_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(order_window, text="Bill Number:").grid(row=2, column=0, padx=10, pady=5)
    bill_entry = tk.Entry(order_window)
    bill_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(order_window, text="Store Location:").grid(row=3, column=0, padx=10, pady=5)
    store_var = tk.StringVar(order_window, "Store 1")
    tk.OptionMenu(order_window, store_var, "Store 1", "Store 2").grid(row=3, column=1, padx=10, pady=5)

    def add_to_cart():
        product_id = product_id_entry.get()
        quantity = int(quantity_entry.get())
        bill_number = bill_entry.get()
        store_location = store_var.get()
        success = create_order(product_id, quantity, bill_number, store_location)
        if success:
            messagebox.showinfo("Success", "Product added to order!")
            order_window.destroy()
            refresh_order_list()
        else:
            messagebox.showerror("Error", "Failed to create order.")

    tk.Button(order_window, text="Add to Cart", command=add_to_cart).grid(row=4, column=1, pady=10)

def refresh_order_list():
    """Refresh the order list."""
    order_table.delete(*order_table.get_children())
    orders = get_orders()
    for order in orders:
        order_table.insert(
            "",
            "end",
            values=(
                order["order_id"],
                order["date"],
                order["total_items"],
                order["total_price"],
            ),
        )

def handle_returns():
    """Handle returns in a new window."""
    return_window = tk.Toplevel(root)
    return_window.title("Handle Returns")
    return_window.geometry("400x300")
    # Add return handling code here...

# Initialize main window
root = tk.Tk()
root.title("Cashier Activities")
root.geometry("800x600")

# Search Bar
search_frame = tk.Frame(root)
search_frame.pack(fill="x", pady=5)
search_entry = tk.Entry(search_frame)
search_entry.pack(side="left", fill="x", expand=True, padx=5)
tk.Button(search_frame, text="Search", command=search_products).pack(side="right", padx=5)

# Product Table
columns = ("ID", "Name", "Store 1", "Store 2")
product_table = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    product_table.heading(col, text=col)
product_table.pack(fill="both", expand=True, pady=5)

# Orders Section
tk.Label(root, text="Orders:").pack(pady=5)
columns_orders = ("Order ID", "Date", "Items", "Total Price")
order_table = ttk.Treeview(root, columns=columns_orders, show="headings")
for col in columns_orders:
    order_table.heading(col, text=col)
order_table.pack(fill="both", expand=True, pady=5)

# Buttons
button_frame = tk.Frame(root)
button_frame.pack(fill="x", pady=10)
tk.Button(button_frame, text="Make Order", command=make_order).pack(side="left", padx=5)
tk.Button(button_frame, text="Refresh Products", command=refresh_product_list).pack(side="left", padx=5)
tk.Button(button_frame, text="Handle Returns", command=handle_returns).pack(side="left", padx=5)

# Initial Data Load
refresh_product_list()
refresh_order_list()

root.mainloop()