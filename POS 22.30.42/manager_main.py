import tkinter as tk
from tkinter import ttk, messagebox
import threading
from firebase_config import db
from datetime import datetime, timedelta
from controllers.stocks_controller import StocksController
from controllers.product_controller import (
    add_product_with_custom_id,
    get_all_products,
    delete_product,
    update_product,
    add_stock_in_order,
    deduct_stock
)
from controllers.order_controller import fetch_orders, save_order, clear_new_order_fields

# Initialize main window
root = tk.Tk()
root.title("Mahinda Motors - Manager System")
root.geometry("1000x700")

# Tabbed Interface
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Product Management Tab
frame_products = tk.Frame(notebook)
notebook.add(frame_products, text="Product Management")

# Stock-In Management Tab
frame_stock_in = tk.Frame(notebook)
notebook.add(frame_stock_in, text="Stock-In Management")

# recent stocks in tab
frame_recent_stocks = tk.Frame(notebook)
notebook.add(frame_recent_stocks, text="Recent Stocks")

# new order tab
new_order_frame = tk.Frame(notebook)
notebook.add(new_order_frame, text="New order")

# recent orders tab
#frame_recent_orders = tk.Frame(notebook)
#notebook.add(frame_recent_orders, text="Recent orders")

# ------------------------------
# Product Management Functions
# ------------------------------
all_products = []

def filter_products():
    """Filter products based on Product ID/Name and Category input fields."""
    query_name = entry_filter_name.get().strip().lower()
    query_category = entry_filter_category.get().strip().lower()
    
    for row in product_table.get_children():
        product_table.delete(row)
    
    for product_id, product_data in all_products.items():
        name_matches = query_name in product_id.lower() or query_name in product_data["name"].lower()
        category_matches = query_category in product_data["category"].lower()
        
        if (not query_name or name_matches) and (not query_category or category_matches):
            product_table.insert(
                "",
                "end",
                iid=product_id,
                values=(
                    product_id,
                    product_data["name"],
                    product_data["category"],
                    product_data["price"],
                    product_data["quantity_store_1"],
                    product_data["quantity_store_2"],
                    product_data["supplier"],
                ),
            )

def refresh_product_list():
    """Fetch and display all products in the table."""
    global all_products
    all_products = get_all_products()  # Fetch all products
    filter_products()

def add_product():
    product_id = entry_id.get()
    product_data = {
        "name": entry_name.get(),
        "category": entry_category.get(),
        "price": float(entry_price.get()),
        "quantity_store_1": int(entry_store1.get()),
        "quantity_store_2": int(entry_store2.get()),
        "supplier": entry_supplier.get(),
    }
    try:
        add_product_with_custom_id(product_id, product_data)
        refresh_product_list()
        messagebox.showinfo("Success", "Product added successfully!")
        clear_input_fields()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add product: {e}")

def delete_selected_product():
    selected = product_table.focus()
    if not selected:
        messagebox.showerror("Error", "Please select a product to delete.")
        return
    product_id = product_table.item(selected)["values"][0]
    confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete {product_id}?")
    if confirm:
        delete_product(product_id)
        refresh_product_list()

def load_selected_product():
    selected = product_table.focus()
    if not selected:
        messagebox.showerror("Error", "Please select a product to edit.")
        return
    product_id = product_table.item(selected)["values"][0]
    product_data = product_table.item(selected)["values"]
    entry_id.delete(0, tk.END)
    entry_id.insert(0, product_id)
    entry_name.delete(0, tk.END)
    entry_name.insert(0, product_data[1])
    entry_category.delete(0, tk.END)
    entry_category.insert(0, product_data[2])
    entry_price.delete(0, tk.END)
    entry_price.insert(0, product_data[3])
    entry_store1.delete(0, tk.END)
    entry_store1.insert(0, product_data[4])
    entry_store2.delete(0, tk.END)
    entry_store2.insert(0, product_data[5])
    entry_supplier.delete(0, tk.END)
    entry_supplier.insert(0, product_data[6])

def clear_input_fields():
    entry_id.delete(0, tk.END)
    entry_name.delete(0, tk.END)
    entry_category.delete(0, tk.END)
    entry_price.delete(0, tk.END)
    entry_store1.delete(0, tk.END)
    entry_store2.delete(0, tk.END)
    entry_supplier.delete(0, tk.END)

def update_product_details():
    product_id = entry_id.get()
    product_data = {
        "name": entry_name.get(),
        "category": entry_category.get(),
        "price": float(entry_price.get()),
        "quantity_store_1": int(entry_store1.get()),
        "quantity_store_2": int(entry_store2.get()),
        "supplier": entry_supplier.get(),
    }
    try:
        update_product(product_id, product_data)
        refresh_product_list()
        messagebox.showinfo("Success", f"Product '{product_id}' updated successfully!")
        clear_input_fields()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update product: {e}")

# Product Management Form
frame_add_1 = tk.Frame(frame_products)
frame_add_1.pack(fill="x", padx=10, pady=10)

tk.Label(frame_add_1, text="Product ID/Name:").grid(row=2, column=0, padx=5, pady=5)
entry_filter_name = tk.Entry(frame_add_1, width= 30)  # Create Entry widget
entry_filter_name.grid(row=2, column=1, padx=5, pady=5)  # Use .grid() separately
entry_filter_name.bind("<KeyRelease>", lambda e: filter_products())

tk.Label(frame_add_1, text="Category:").grid(row=2, column=2, padx=5, pady=5)
entry_filter_category = tk.Entry(frame_add_1, width= 30)  # Create Entry widget
entry_filter_category.grid(row=2, column=3, padx=5, pady=5)  # Use .grid() separately
entry_filter_category.bind("<KeyRelease>", lambda e: filter_products())

columns = ("ID", "Name", "Category", "Price", "Store 1", "Store 2", "Supplier")
product_table = ttk.Treeview(frame_products, columns=columns, show="headings")
for col in columns:
    product_table.heading(col, text=col)
product_table.pack(fill="both", expand=True, pady=10)

frame_add = tk.Frame(frame_products)
frame_add.pack(fill="x", padx=10, pady=10)

tk.Label(frame_add, text="Product ID:").grid(row=0, column=0, padx=5, pady=5)
entry_id = tk.Entry(frame_add)
entry_id.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_add, text="Name:").grid(row=0, column=2, padx=5, pady=5)
entry_name = tk.Entry(frame_add)
entry_name.grid(row=0, column=3, padx=5, pady=5)

tk.Label(frame_add, text="Category:").grid(row=0, column=4, padx=5, pady=5)
entry_category = tk.Entry(frame_add)
entry_category.grid(row=0, column=5, padx=5, pady=5)

tk.Label(frame_add, text="Price:").grid(row=1, column=0, padx=5, pady=5)
entry_price = tk.Entry(frame_add)
entry_price.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_add, text="Store 1 Quantity:").grid(row=1, column=2, padx=5, pady=5)
entry_store1 = tk.Entry(frame_add)
entry_store1.grid(row=1, column=3, padx=5, pady=5)

tk.Label(frame_add, text="Store 2 Quantity:").grid(row=1, column=4, padx=5, pady=5)
entry_store2 = tk.Entry(frame_add)
entry_store2.grid(row=1, column=5, padx=5, pady=5)

tk.Label(frame_add, text="Supplier:").grid(row=2, column=0, padx=5, pady=5)
entry_supplier = tk.Entry(frame_add)
entry_supplier.grid(row=2, column=1, padx=5, pady=5)

tk.Button(frame_add, text="Add Product", command=add_product).grid(row=2, column=5, padx=10, pady=5)

# Product Management Buttons
frame_buttons = tk.Frame(frame_products)
frame_buttons.pack(pady=10)

tk.Button(frame_buttons, text="Refresh", command=refresh_product_list).pack(side="left", padx=5)
tk.Button(frame_buttons, text="Delete Selected", command=delete_selected_product).pack(side="left", padx=5)
tk.Button(frame_buttons, text="Edit Selected", command=load_selected_product).pack(side="left", padx=5)
tk.Button(frame_buttons, text="Update Product", command=update_product_details).pack(side="left", padx=5)

refresh_product_list()

# ------------------------------
# Stock-In Management Functions
# ------------------------------
def populate_autocomplete(event=None):
    """Dynamically filter products based on user inputs (name/ID and category)."""
    # Get the current inputs
    name_or_id_text = name_id_combobox.get().lower()  # Input for name or ID
    category_text = category_combobox.get().lower()  # Input for category

    # Filter products based on name/ID
    filtered_by_name_id = [
        f"{product_id} - {data['name']}-{data['category']}" 
        for product_id, data in all_products.items()
        if name_or_id_text in data['name'].lower() or name_or_id_text in product_id.lower()
    ]

    # Filter products based on category
    filtered_by_category = [
        f"{product_id} - {data['name']}-{data['category']}" 
        for product_id, data in all_products.items()
        if category_text in data['category'].lower()
    ]

    # Get the common set of filtered results
    common_filtered = set(filtered_by_name_id) & set(filtered_by_category)

    # Update the autocomplete options
    autocomplete_combobox['values'] = list(common_filtered)

def add_to_cart():
    product = autocomplete_combobox.get()
    try:
        # Check if the product format is valid (i.e., contains ' - ')
        if " - " not in product:
            raise ValueError("Invalid format. Please select a valid product.")
        
        product_id, product_name = product.split(" - ")

        unit_price = float(entry_unit_price.get())
        total_quantity = int(entry_total_quantity.get())
        store_1_qty = int(entry_store1_qty.get())
        store_2_qty = int(entry_store2_qty.get())

        if store_1_qty + store_2_qty == total_quantity:
            pass
        else:
            raise ValueError("quantities in stores does not equal to total")

        cart_table.insert(
            "",
            "end",
            values=(product_id, product_name, unit_price, total_quantity, store_1_qty, store_2_qty),
        )
        autocomplete_combobox.delete(0,tk.END)
        entry_total_quantity.delete(0,tk.END)
        entry_store1_qty.delete(0,tk.END)
        entry_store2_qty.delete(0,tk.END)
        entry_unit_price.delete(0,tk.END)
    except ValueError as e:
        messagebox.showerror("Error", str(e))  # Show the error message to the user

def finalize_stock_in_order():
    order_items = []
    for row in cart_table.get_children():
        values = cart_table.item(row, "values")
        order_items.append({
            "product_id": values[0],
            "name": values[1],
            "unit_price": values[2],
            "total_quantity": values[3],
            "quantity_store_1": values[4],
            "quantity_store_2": values[5],
        })

    from datetime import datetime
    order_id = datetime.now().strftime("%Y%m%d%H%M%S") + "-" + entry_invoice_no.get()
    
    if len(order_items) ==0:
        messagebox.showinfo("Error", "Cart is empty")
    elif (entry_total_price.get())=="":
        messagebox.showinfo("Error", "total price is empty")
    elif (entry_invoice_no.get()) == "":
        messagebox.showinfo("Error", "please enter PO number")
    else:
        stocks_in_data = {
        "order_id": order_id,
        "total_price_after_discount": float(entry_total_price.get()),
        "items": order_items,}
        add_stock_in_order(stocks_in_data)
        messagebox.showinfo("Success", "Stock-In Order Saved!")
        controller.refresh_table()
        name_id_combobox.delete(0,tk.END)
        category_combobox.delete(0,tk.END)
        autocomplete_combobox.delete(0,tk.END)
        entry_invoice_no.delete(0,tk.END)
        entry_total_price.delete(0,tk.END)
        entry_total_quantity.delete(0,tk.END)
        entry_store1_qty.delete(0,tk.END)
        entry_store2_qty.delete(0,tk.END)
        entry_unit_price.delete(0,tk.END)
        cart_table.delete(*cart_table.get_children())

def clear_cart_stock_in_order():
    name_id_combobox.delete(0,tk.END)
    category_combobox.delete(0,tk.END)
    autocomplete_combobox.delete(0,tk.END)
    entry_invoice_no.delete(0,tk.END)
    entry_total_price.delete(0,tk.END)
    entry_total_quantity.delete(0,tk.END)
    entry_store1_qty.delete(0,tk.END)
    entry_store2_qty.delete(0,tk.END)
    entry_unit_price.delete(0,tk.END)
    cart_table.delete(*cart_table.get_children())

# Stock-In Form
frame_stock_in_form = tk.Frame(frame_stock_in)
frame_stock_in_form.pack(fill="x", padx=10, pady=10)

tk.Label(frame_stock_in_form, text="name | Category:").grid(row=0, column=0)
name_id_combobox = ttk.Entry(frame_stock_in_form, width=30)#new
name_id_combobox.grid(row=0, column=1, padx=5, pady=5)#new
category_combobox = ttk.Entry(frame_stock_in_form, width=30) #new
category_combobox.grid(row=0, column=2, padx=5, pady=5) #new
tk.Label(frame_stock_in_form, text="Select Product:").grid(row=1, column=0)
autocomplete_combobox = ttk.Combobox(frame_stock_in_form, width=28)
autocomplete_combobox.grid(row=1, column=1, padx=0, pady=5)
name_id_combobox.bind("<KeyRelease>", populate_autocomplete)#new
category_combobox.bind("<KeyRelease>", populate_autocomplete)#new
#autocomplete_combobox.bind("<KeyRelease>", populate_autocomplete) 


populate_autocomplete()

tk.Label(frame_stock_in_form, text="Unit Price:").grid(row=2, column=0, padx=5, pady=5)
entry_unit_price = tk.Entry(frame_stock_in_form, width=30)
entry_unit_price.grid(row=2, column=1, padx=5)

tk.Label(frame_stock_in_form, text="Total Quantity:").grid(row=3, column=0, padx=5, pady=5)
entry_total_quantity = tk.Entry(frame_stock_in_form, width=30)
entry_total_quantity.grid(row=3, column=1, padx=5)

tk.Label(frame_stock_in_form, text="Store 1 Quantity:").grid(row=4, column=0, padx=5, pady=5)
entry_store1_qty = tk.Entry(frame_stock_in_form, width=30)
entry_store1_qty.grid(row=4, column=1, padx=5)

tk.Label(frame_stock_in_form, text="Store 2 Quantity:").grid(row=5, column=0, padx=5, pady=5)
entry_store2_qty = tk.Entry(frame_stock_in_form, width=30)
entry_store2_qty.grid(row=5, column=1, padx=5)
tk.Button(frame_stock_in_form, text="Add to Cart", command=add_to_cart).grid(row=5, column=2, padx=50)
tk.Button(frame_stock_in_form, text="Clear Cart", command=clear_cart_stock_in_order).grid(row=5, column=3, padx=5, pady=5)


cart_columns = ("Product ID", "Name", "Unit Price", "Quantity", "Store 1", "Store 2")
cart_table = ttk.Treeview(frame_stock_in, columns=cart_columns, show="headings")
for col in cart_columns:
    cart_table.heading(col, text=col)
cart_table.pack(fill="both", expand=True, padx=10, pady=10)

tk.Label(frame_stock_in, text="Invoice No:").pack(pady=5)
entry_invoice_no = tk.Entry(frame_stock_in)
entry_invoice_no.pack(pady=5)

tk.Label(frame_stock_in, text="Total Price After Discount:").pack(pady=5)
entry_total_price = tk.Entry(frame_stock_in)
entry_total_price.pack(pady=5)

tk.Button(frame_stock_in, text="Finalize Stock-In", command=finalize_stock_in_order).pack(pady=10)

# ------------------------------
# Recent Stocks Tab
# ------------------------------

# Create the Treeview table for recent stocks
recent_columns = ("Order ID", "Product Details", "Total Price After Discount")
recent_stock_table = ttk.Treeview(frame_recent_stocks, columns=recent_columns, show="headings")
for col in recent_columns:
    recent_stock_table.heading(col, text=col)
recent_stock_table.pack(fill="both", expand=True, pady=10)

# Create the controller instance
controller = StocksController(recent_stock_table)

# Button to manually refresh the recent stock list
refresh_button = tk.Button(frame_recent_stocks, text="Refresh Recent Stocks", command=controller.refresh_table)
refresh_button.pack(pady=5)

# Button to view details of the selected order
details_button = tk.Button(frame_recent_stocks, text="View Details", command=lambda: controller.view_selected_order_details(recent_stock_table))
details_button.pack(pady=5)

# ------------------------------
# new order tab
# ------------------------------
cart_items = []  # Global cart to store added items

def update_product_search_suggestions(product_entry_widget, category_entry_widget, combobox_widget):
    '''updates a list based on entry widget inputs'''
    name_or_id_text = product_entry_widget.get().lower()
    category_text = category_entry_widget.get().lower()

    filter_by_name_id = [
        f"{product_id} - {data['name']} - {data['category']}"
        for product_id, data in all_products.items()
        if name_or_id_text in data['name'].lower()  or  name_or_id_text in product_id.lower()
    ]

    filter_by_category = [
        f"{product_id} - {data['name']} - {data['category']}"
        for product_id, data in all_products.items()
        if category_text in data["category"].lower()
    ]

    common_filtered = set(filter_by_name_id) & set(filter_by_category)

    combobox_widget['values']=list(common_filtered)

def add_to_cart(product_entry, product_search_entry, quantity_entry, store_combobox, table):
    """Add selected product to the cart."""
    product_info = product_entry.get()
    quantity = int(quantity_entry.get())

    if not product_info or not quantity or not store_combobox.get():
        tk.messagebox.showerror("Error", "Please fill in all fields before adding to the cart.")
        return

    # Parse product information
    product_id, product_name = product_info.split(" - ", 1) if " - " in product_info else (product_info, "")
    product = all_products.get(product_id)

    # Check if product exists in all_products
    if product_id not in all_products:
        tk.messagebox.showerror("Error", f"Product with ID {product_id} not found in the database.")
        return

    try:
        store_location = store_combobox.get().lower()  # Get the selected store location
        store_key = f"quantity_{store_location.replace(' ', '_')}"
        
        # Check stock availability
        if store_key not in product or int(product[store_key]) < int(quantity):
            tk.messagebox.showerror("Error", "Insufficient stock.")
            return

        item_total = product["price"] * quantity
        # Add to cart with store location
        cart_items.append({
            "id": product_id,
            "name": product["name"],
            "quantity": quantity,
            "price": product["price"],
            "store_location": store_location,  # Store location added to the cart item
            "item_total": item_total
        })

        clear_new_order_fields(store_combobox, product_entry, product_search_entry, quantity_entry)

    except ValueError:
        tk.messagebox.showerror("Error", "Quantity must be a valid number.")

    # Update the table
    table.delete(*table.get_children())  # Clear existing rows in the table
    grand_total = 0

    for item in cart_items:
        table.insert("", "end", values=(item["id"], item["name"], item["store_location"], item["quantity"], item["item_total"]))
        grand_total += item["item_total"]

    # Add or update the "Grand Total" row
    table.insert("", "end", values=("", "", "", "Grand Total", grand_total))

def clear_cart(table):
    """Clear the cart."""
    import tkinter.messagebox as messagebox
    if not cart_items:
        messagebox.showinfo("Info", "The cart is already empty.")
        return

    # Confirmation dialog
    if messagebox.askyesno("Confirm", "Are you sure you want to clear the cart?"):
        table.delete(*table.get_children())
        cart_items.clear()
        messagebox.showinfo("Info", "The cart has been cleared.")

def handle_save_order(
    bill_number_entry, 
    cart_items, 
    total_price_entry, 
    table, 
    store_selection, 
    product_entry, 
    product_search_entry, 
    quantity_entry
):
    """Handle the save order process."""
    bill_number = bill_number_entry.get()
    total_price = total_price_entry.get()

    # Validate cart and total price
    if not cart_items:
        tk.messagebox.showerror("Error", "The cart is empty. Add items before saving the order.")
        return

    if not total_price or total_price == "0":
        tk.messagebox.showerror("Error", "The total price cannot be empty or zero.")
        return

    if not bill_number or bill_number == "0":
        tk.messagebox.showerror("Error", "The bill number cannot be empty or zero.")
        return
    
    # Save the order
    save_order(bill_number, cart_items, total_price)

    # Clear the cart
    table.delete(*table.get_children())
    cart_items.clear()

    # Clear input fields
    clear_new_order_fields(store_selection, product_entry, product_search_entry, quantity_entry)
    bill_number_entry.delete(0,tk.END)
    total_price_entry.delete(0,tk.END)
    fetch_orders()

def init_new_order_tab(root):
    """Initialize the new order tab."""
    # Title
    ttk.Label(new_order_frame, text="New Order", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=3, pady=10)

    # Order Details Section
    order_details_frame = ttk.LabelFrame(new_order_frame, text="Order Details", padding=10)
    order_details_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

    ttk.Label(order_details_frame, text="Bill Number:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    bill_number_entry = ttk.Entry(order_details_frame, width=20)
    bill_number_entry.grid(row=0, column=1, padx=5, pady=5)

    # Product Search Section
    product_search_frame = ttk.LabelFrame(new_order_frame, text="Search Products", padding=10)
    product_search_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

    ttk.Label(product_search_frame, text="Product ID/Name:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    product_search_entry = ttk.Entry(product_search_frame, width=20)
    product_search_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(product_search_frame, text="Category:").grid(row=0, column=2, sticky="e", padx=5, pady=5)
    category_search_entry = ttk.Entry(product_search_frame, width=20)
    category_search_entry.grid(row=0, column=3, padx=5, pady=5)

    # Search Results
    product_suggestions_combobox = ttk.Combobox(product_search_frame, width=35)
    product_suggestions_combobox.grid(row=1, column=1, columnspan=2, padx=5, pady=5)

    # Quantity and Add to Cart
    ttk.Label(product_search_frame, text="Quantity:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    quantity_entry = ttk.Entry(product_search_frame, width=10)
    quantity_entry.grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(product_search_frame, text="Store:").grid(row=2, column=2, sticky="e", padx=5, pady=5)
    store_selection = ttk.Combobox(product_search_frame, values=["Store 1", "Store 2"], state="readonly", width=14)
    store_selection.grid(row=2, column=3, padx=5, pady=5)

    ttk.Button(product_search_frame, text="Add to Cart", command=lambda: add_to_cart(
        product_suggestions_combobox, product_search_entry, quantity_entry, store_selection, cart_table
    )).grid(row=2, column=4, padx=5, pady=5)

    # Cart Section
    cart_frame = ttk.LabelFrame(new_order_frame, text="Cart", padding=10)
    cart_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

    cart_table = ttk.Treeview(cart_frame, columns=("Product ID", "Name", "Store", "Quantity", "Price"), show="headings")
    cart_table.heading("Product ID", text="Product ID")
    cart_table.heading("Name", text="Name")
    cart_table.heading("Store", text="Store")
    cart_table.heading("Quantity", text="Quantity")
    cart_table.heading("Price", text="Price")
    cart_table.grid(row=0, column=0, columnspan=3, pady=5)

    # Total Price and Actions
    summary_frame = ttk.Frame(new_order_frame)
    summary_frame.grid(row=4, column=0, columnspan=3, pady=10, padx=10, sticky="ew")

    ttk.Label(summary_frame, text="Total Price:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    total_price_entry = ttk.Entry(summary_frame, width=20, state="normal")
    total_price_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Button(summary_frame, text="Clear Cart", command=lambda: clear_cart(cart_table)).grid(row=0, column=2, padx=5, pady=5)

    ttk.Button(summary_frame, text="Save Order", command=lambda: handle_save_order(
        bill_number_entry, cart_items, total_price_entry, cart_table, store_selection,
        product_suggestions_combobox, product_search_entry, quantity_entry
    )).grid(row=0, column=3, padx=5, pady=5)

    # Bind search entry
    category_search_entry.bind(
        "<KeyRelease>",
        lambda event: update_product_search_suggestions(product_search_entry, category_search_entry, product_suggestions_combobox)
    )

    product_search_entry.bind(
        "<KeyRelease>",
        lambda event: update_product_search_suggestions(product_search_entry, category_search_entry, product_suggestions_combobox)
    )

# ------------------------------
# recents sales orders tab
# ------------------------------
def create_recent_orders_tab(notebook):
    """Create the Recent Sales Orders tab with a return functionality."""

    def show_order_details(order_id):
        """Display details of the selected order in a popup window."""
        order = next((o for o in orders if o["order_id"] == order_id), None)
        if order:
            details_window = tk.Toplevel()
            details_window.title(f"Order Details: {order_id}")
            details_window.geometry("700x600")

            # Basic order details
            ttk.Label(details_window, text="Order Details", font=("Helvetica", 14, "bold")).pack(pady=10)
            order_frame = ttk.Frame(details_window)
            order_frame.pack(pady=10, fill="x", padx=10)

            # Friendly key mapping for display
            for idx, (key, display_name) in enumerate([("order_id", "Order ID"), ("date", "Date"), ("total_amount", "Total Amount")]):
                ttk.Label(order_frame, text=f"{display_name}:").grid(row=idx, column=0, sticky="w", padx=5, pady=3)
                ttk.Label(order_frame, text=f"{order.get(key, 'N/A')}").grid(row=idx, column=1, sticky="w", padx=5, pady=3)

            # Separator
            ttk.Separator(details_window, orient="horizontal").pack(fill="x", pady=10)

            # Display items in a table
            ttk.Label(details_window, text="Order Items", font=("Helvetica", 12, "bold")).pack(pady=5)
            items_frame = ttk.Frame(details_window)
            items_frame.pack(fill="both", expand=True, padx=10)

            # Scrollbar for items
            scrollbar = ttk.Scrollbar(items_frame, orient="vertical")
            scrollbar.pack(side="right", fill="y")

            # Table for items
            item_columns = ("Product ID", "Name", "Quantity", "Price", "Store Location")
            items_table = ttk.Treeview(
                items_frame, columns=item_columns, show="headings", yscrollcommand=scrollbar.set, height=10
            )
            items_table.pack(fill="both", expand=True)
            scrollbar.config(command=items_table.yview)

            # Set headings and column widths
            for col in item_columns:
                items_table.heading(col, text=col)
                items_table.column(col, anchor="center", width=100)

            # Populate the table with item details
            for item in order["items"]:
                items_table.insert(
                    "", "end",
                    values=(item["product_id"], item["name"], item["quantity"], f"${item['price']:.2f}", item["store_location"])
                )

            # Separator
            ttk.Separator(details_window, orient="horizontal").pack(fill="x", pady=10)

            # Display total amount
            total_amount = order.get("total_amount", 0.0)
            ttk.Label(details_window, text=f"Total Amount: ${total_amount:.2f}", font=("Helvetica", 12, "bold")).pack(pady=10)

            # Close button
            ttk.Button(details_window, text="Close", command=details_window.destroy).pack(pady=10)

    def initiate_return_order():
        """Initiate the return process for the selected order."""
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No order selected!")
            return

        order_id = tree.item(selected_item, "values")[0]
        order = next((o for o in orders if o["order_id"] == order_id), None)

        if order:
            # Open a return order window
            return_window = tk.Toplevel()
            return_window.title(f"Return Order: {order_id}")
            return_window.geometry("700x600")

            ttk.Label(return_window, text="Return Order Details", font=("Helvetica", 14, "bold")).pack(pady=10)

            # Display order items for return
            ttk.Label(return_window, text="Select items to return:", font=("Helvetica", 12)).pack(pady=5)
            items_frame = ttk.Frame(return_window)
            items_frame.pack(fill="both", expand=True, padx=10)

            # Scrollbar for items
            scrollbar = ttk.Scrollbar(items_frame, orient="vertical")
            scrollbar.pack(side="right", fill="y")

            # Table for items
            item_columns = ("Product ID", "Name", "Quantity", "Return Quantity", "Store Location")
            items_table = ttk.Treeview(
                items_frame, columns=item_columns, show="headings", yscrollcommand=scrollbar.set, height=10
            )
            items_table.pack(fill="both", expand=True)
            scrollbar.config(command=items_table.yview)

            # Set headings and column widths
            for col in item_columns:
                items_table.heading(col, text=col)
                items_table.column(col, anchor="center", width=100)

            # Populate the table with item details
            for item in order["items"]:
                print(item)
                items_table.insert(
                    "", "end",
                    values=(item["product_id"], item["name"], item["quantity"], 0, item["store_location"])  # Default return quantity to 0
                )

            # Make the "Return Quantity" column editable
            def edit_cell(event):
                selected_row = items_table.selection()
                if not selected_row:
                    return

                # Get selected row and column
                item_id = selected_row[0]
                column_id = items_table.identify_column(event.x)
                col_index = int(column_id.replace("#", "")) - 1

                # Only allow editing the "Return Quantity" column
                if col_index == 3:
                    # Get current cell value
                    current_value = items_table.item(item_id, "values")[col_index]

                    # Create an entry widget
                    entry = tk.Entry(items_table)
                    entry.insert(0, current_value)
                    entry.place(x=event.x, y=event.y, anchor="nw", width=100)

                    def save_value():
                        new_value = entry.get()
                        try:
                            new_value = int(new_value)  # Ensure value is an integer
                            values = list(items_table.item(item_id, "values"))
                            values[col_index] = new_value
                            items_table.item(item_id, values=values)
                        except ValueError:
                            messagebox.showerror("Error", "Invalid quantity. Please enter a number.")
                        finally:
                            entry.destroy()

                    entry.bind("<Return>", lambda _: save_value())
                    entry.bind("<FocusOut>", lambda _: save_value())
                    entry.focus()

            items_table.bind("<Double-1>", edit_cell)

            # Add a label and entry for Return Amount
            return_amount_label = tk.Label(return_window, text="Return Amount ($):", font=("Helvetica", 12))
            return_amount_label.pack(pady=5)
            
            return_amount_entry = tk.Entry(return_window, font=("Helvetica", 12))
            return_amount_entry.pack(pady=5)

            # Add a confirm return button
            def confirm_return():
                return_amount = return_amount_entry.get()
                if not return_amount.isdigit() or float(return_amount) <= 0:
                    messagebox.showerror("Error", "Invalid return amount. Please enter a positive number.")
                    return
                
                # Process return order
                process_return_order(order_id, items_table, return_amount)

                # Show success message
                messagebox.showinfo("Success", "Return processed successfully!")

                # Close the return window
                return_window.destroy()

            ttk.Button(return_window, text="Confirm Return", command=confirm_return).pack(pady=10)
    
    def fetch_and_display_orders():
        """Fetch and display orders for the last 100 days."""
        # Clear the Treeview
        for row in tree.get_children():
            tree.delete(row)

        # Fetch orders
        global orders
        orders = fetch_orders()

        # Ensure `date_time` is a datetime object
        for order in orders:
            if isinstance(order["date_time"], str):
                order["date_time"] = datetime.strptime(order["date_time"], "%Y-%m-%d %H:%M:%S")

        # Calculate the date 100 days ago
        today = datetime.today()
        hundred_days_ago = today - timedelta(days=100)

        # Filter orders for the last 100 days
        recent_orders = [
            order for order in orders
            if hundred_days_ago <= order["date_time"] <= today
        ]

        # Sort orders by date_time in descending order
        recent_orders.sort(key=lambda x: x["date_time"], reverse=True)

        # Populate the Treeview
        for order in recent_orders:
            tree.insert("", "end", values=(order["order_id"], order["date_time"], order["total_amount"]))

    def process_return_order(order_id, items_table, return_amount_input):
        """
        Process the return order, update the database, and log the return.
        :param order_id: ID of the order being returned.
        :param items_table: Table containing items to return.
        :param return_amount_input: Input field value for return amount.
        """
        return_items = []
        return_amount = float(return_amount_input)  # Use the provided return amount

        # Extract return items from the table
        for row in items_table.get_children():
            values = items_table.item(row, "values")
            print(values)
            product_id, name, quantity, return_quantity, store_location = values
            return_quantity = int(return_quantity)

            if return_quantity > 0:
                return_items.append({
                    "product_id": product_id,
                    "name": name,
                    "quantity": return_quantity,
                    "store_location": store_location
                })

        # Check if there are items to return
        if not return_items:
            messagebox.showerror("Error", "No items selected for return.")
            return

        if return_amount <= 0:
            messagebox.showerror("Error", "Return amount must be greater than zero.")
            return

        try:
            # Begin Firestore transaction
            with db.transaction() as transaction:
                # Update products collection
                for item in return_items:
                    product_id = item["product_id"]
                    store_location = item["store_location"]
                    return_quantity = item["quantity"]
                    print(product_id, store_location, return_quantity)

                    # Get the product document reference
                    product_ref = db.collection("products").document(product_id)
                    product = product_ref.get().to_dict()

                    if product:
                        # Prepare the update dictionary
                        update_data = {}
                        if store_location == "store 1":
                            update_data["quantity_store_1"] = product["quantity_store_1"] + return_quantity
                        elif store_location == "store 2":
                            update_data["quantity_store_2"] = product["quantity_store_2"] + return_quantity

                        # Update the Firestore document directly
                        if update_data:
                            product_ref.update(update_data)

                # Update orders collection
                order_ref = db.collection("orders").document(order_id)
                order = order_ref.get().to_dict()
                if order:
                    for item in return_items:
                        product_id = item["product_id"]
                        return_quantity = item["quantity"]

                        # Update items in the order
                        for order_item in order["items"]:
                            if order_item["product_id"] == product_id:
                                order_item["quantity"] -= return_quantity

                    # Update the order in the database
                    transaction.update(order_ref, {"items": order["items"]})

                # Add entry to returns collection
                return_data = {
                    "order_id": order_id,
                    "return_date": datetime.now(),
                    "return_amount": return_amount,
                    "return_items": return_items
                }
                db.collection("returns").add(return_data)

            messagebox.showinfo("Success", f"Order {order_id} returned successfully!\nReturn Amount: ${return_amount:.2f}")
            fetch_and_display_orders()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to process return: {str(e)}")

    # Frame for the tab
    recent_orders_frame = ttk.Frame(notebook)
    notebook.add(recent_orders_frame, text="Recent Sales / Returns")

    # Filters (Today, Last Week, Last Month)
    filters_frame = ttk.Frame(recent_orders_frame)
    filters_frame.pack(pady=10)
    ttk.Label(filters_frame, text="Filter Orders:").pack(side="left", padx=5)
    ttk.Button(filters_frame, text="Today", command=lambda: fetch_and_display_orders()).pack(side="left", padx=5)
    ttk.Button(filters_frame, text="Last Week", command=lambda: fetch_and_display_orders("last_week")).pack(side="left", padx=5)
    ttk.Button(filters_frame, text="Last Month", command=lambda: fetch_and_display_orders("last_month")).pack(side="left", padx=5)
    ttk.Button(filters_frame, text="Refresh", command=lambda: fetch_and_display_orders()).pack(side="left", padx=5)
    # Table for displaying orders
    columns = ("Order ID", "Date", "Total Amount")
    tree = ttk.Treeview(recent_orders_frame, columns=columns, show="headings", height=15)
    tree.pack(pady=10, fill="both", expand=True)

    # Set column headings
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150)

    # Add double-click event to show order details
    def on_item_double_click(event):
        selected_item = tree.selection()
        if selected_item:
            order_id = tree.item(selected_item, "values")[0]
            show_order_details(order_id)

    # Add double-click event to show order details
    tree.bind("<Double-1>", lambda event: on_item_double_click(event))

    # Add a "Return Order" button
    ttk.Button(recent_orders_frame, text="Return Order", command=initiate_return_order).pack(pady=10)
    refresh_button = ttk.Button(recent_orders_frame, text="Refresh", command=fetch_and_display_orders)
    refresh_button.pack(pady=5)
    # Fetch and display today's orders by default
    fetch_and_display_orders()

create_recent_orders_tab(notebook)
# Call the controller to fetch and display the data initially
controller.fetch_recent_stock_data()
init_new_order_tab(root)
root.mainloop()