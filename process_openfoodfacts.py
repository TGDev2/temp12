import json
import random

def extract_products(file_path, limit=100):
    products = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if len(products) >= limit:
                break
            product = json.loads(line)
            code_barre = product.get('code')
            nom = product.get('product_name', '').replace("'", "''")
            categories = product.get('categories', '').replace("'", "''")
            if code_barre and nom:
                products.append({
                    'code_barre': code_barre,
                    'nom': nom,
                    'categories': categories
                })
    return products

products = extract_products('openfoodfacts-products.jsonl')

# Générer des prix aléatoires et préparer les requêtes SQL
with open('insert_data.sql', 'w', encoding='utf-8') as f:
    for product in products:
        code_barre = product['code_barre']
        nom = product['nom']
        categories = product['categories']
        prix = round(random.uniform(1.0, 100.0), 2)
        query = f"INSERT INTO articles (code_barre, nom, prix, categorie) VALUES ('{code_barre}', '{nom}', {prix}, '{categories}');\n"
        f.write(query)
