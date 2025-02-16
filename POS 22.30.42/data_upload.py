from firebase_config import db
import pandas as pd

def data_upload(file_path, sheet_name):
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    for _, row in df.iterrows():  # Correct iteration
        product_id = str(row[0])  # Ensure product_id is a string
        
        product_data = {
            "category": row[2],
            "name": row[1],
            "price": row[3],
            "quantity_store_1": row[4],
            "quantity_store_2": row[5],
            "supplier": row[6]
        }

        db.collection("products").document(product_id).set(product_data)

data_upload("ring_set_updated.xlsx", "Sheet1")
