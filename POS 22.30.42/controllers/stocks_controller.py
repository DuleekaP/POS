from tkinter import messagebox, ttk
import tkinter as tk
from firebase_admin import firestore
from firebase_config import db

class StocksController:
    def __init__(self, table):
        """Initialize the controller with a reference to the Treeview table."""
        self.table = table

    def fetch_recent_stock_data(self):
        """Fetch the most recent stock data from the database and populate the table."""
        # Fetch the recent stock data from Firestore
        recent_stock_ref = db.collection('stock_in_orders').order_by('order_id', direction=firestore.Query.DESCENDING).limit(100)
        recent_stocks = recent_stock_ref.stream()

        # Clear the existing data in the table
        for row in self.table.get_children():
            self.table.delete(row)

        # Insert the new data into the table
        for stock in recent_stocks:
            data = stock.to_dict()
            order_items = data.get('items', [])
            total_price_after_discount = data.get('total_price_after_discount', 0)

            # Generate product details string
            product_details = ", ".join(
                [f"{item['name']} (x{item['total_quantity']})" for item in order_items]
            )

            # Insert the aggregated data into the table
            self.table.insert(
                "",
                "end",
                values=(
                    data['order_id'],
                    product_details,
                    total_price_after_discount,
                ),
            )

    def refresh_table(self):
        """Refresh the recent stock data."""
        self.fetch_recent_stock_data()

    def view_selected_order_details(self, table):
        """Show the details of the selected order in a popup window with a table for items."""
        selected_item = table.selection()
        if not selected_item:
            messagebox.showerror("Error", "No order selected!")
            return

        # Get the order ID from the selected row
        selected_order_id = table.item(selected_item[0], "values")[0]

        # Fetch the selected order data from Firestore
        order_ref = db.collection('stock_in_orders').document(selected_order_id)
        order = order_ref.get()

        if order.exists:
            data = order.to_dict()
            order_items = data.get('items', [])
            total_price_after_discount = data.get('total_price_after_discount', 0)

            # Extract date and time from the order_id
            order_id_parts = selected_order_id.split("-")
            date_time = order_id_parts[0].replace("_", " ")  # Replace '_' with a space
            bill_no = order_id_parts[1] if len(order_id_parts) > 1 else "Unknown"

            # Create a popup window
            details_window = tk.Toplevel()
            details_window.title(f"Order Details: {selected_order_id}")
            details_window.geometry("700x600")

            # Display basic order details
            ttk.Label(details_window, text="Order Details", font=("Helvetica", 14, "bold")).pack(pady=10)
            order_frame = ttk.Frame(details_window)
            order_frame.pack(pady=10, fill="x", padx=10)

            # Show basic information
            for idx, (label, value) in enumerate([
                ("Order ID", selected_order_id),
                ("Date & Time", date_time),
                ("Bill Number", bill_no),
                ("Total Price After Discount", f"${total_price_after_discount:.2f}")
            ]):
                ttk.Label(order_frame, text=f"{label}:").grid(row=idx, column=0, sticky="w", padx=5, pady=3)
                ttk.Label(order_frame, text=value).grid(row=idx, column=1, sticky="w", padx=5, pady=3)

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
            item_columns = ("Product ID", "Name", "Unit Price", "Total Quantity", "Store 1 Quantity", "Store 2 Quantity")
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
            for item in order_items:
                items_table.insert(
                    "", "end",
                    values=(
                        item["product_id"],
                        item["name"],
                        item["unit_price"],
                        item["total_quantity"],
                        item["quantity_store_1"],
                        item["quantity_store_2"],
                    )
                )

            # Separator
            ttk.Separator(details_window, orient="horizontal").pack(fill="x", pady=10)

            # Close button
            ttk.Button(details_window, text="Close", command=details_window.destroy).pack(pady=10)

        else:
            messagebox.showerror("Error", "Order not found.")