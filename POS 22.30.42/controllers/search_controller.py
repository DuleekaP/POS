from firebase_config import db

def search_products(search_term):
    """
    Search products by name or ID.
    :param search_term: String to search in product name or ID.
    :return: List of matching products.
    """
    docs = db.collection("products").stream()
    results = []
    for doc in docs:
        product_id = doc.id
        product_data = doc.to_dict()
        if search_term.lower() in product_id.lower() or search_term.lower() in product_data["name"].lower():
            results.append({product_id: product_data})
    return results