import json

# Chemin vers le fichier
file_path = "C:\\Users\\TGA\\Documents\\Projects\\P240003 - Data Openfoodfacts\\openfoodfacts-products.jsonl"

# Lire et afficher quelques lignes
with open(file_path, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        # Charger chaque ligne comme un objet JSON
        data = json.loads(line)
        print(data)  # Afficher les données de la ligne
        if i >= 0:  # Limiter à 5 lignes
            break
