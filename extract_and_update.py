import sys
import re
import easyocr
import mysql.connector
import cv2
import numpy as np

def extract_price_from_image(image_path):
    try:
        # Charger l'image
        image = cv2.imread(image_path)

        # Optionnel : Prétraitement de l'image pour améliorer la reconnaissance
        # Convertir en niveaux de gris
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Binarisation (noir et blanc)
        _, binary = cv2.threshold(gray, 140, 255, cv2.THRESH_BINARY)

        # Sauvegarder l'image prétraitée (utile pour débogage)
        processed_image_path = 'processed_image.jpg'
        cv2.imwrite(processed_image_path, binary)

        # Utiliser EasyOCR pour extraire le texte
        reader = easyocr.Reader(['fr', 'en'])  # Ajouter d'autres langues si nécessaire
        results = reader.readtext(processed_image_path)

        # Rechercher un prix dans le texte extrait
        for _, text, _ in results:
            # Utiliser une expression régulière pour trouver les prix (ex: 12.34 ou 12,34)
            match = re.search(r'(\d+[\.,]\d{2})[ €]?', text)
            if match:
                price_str = match.group(1).replace(',', '.')
                price = float(price_str)
                return price
        return None  # Aucun prix trouvé
    except Exception as e:
        print(f'Erreur lors de l\'extraction du prix : {e}')
        return None

def update_price_in_db(article_id, new_price):
    try:
        # Informations de connexion à la base de données
        db_config = {
            'host': 'db5016742771.hosting-data.io',
            'user': 'dbu77894',
            'password': 'Janvier4622.',
            'database': 'dbs13545829'
        }

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        update_query = """
        UPDATE articles
        SET prix = %s
        WHERE id_article_abarak = %s
        """
        cursor.execute(update_query, (new_price, article_id))
        conn.commit()

        cursor.close()
        conn.close()
        print(f'Prix de l\'article {article_id} mis à jour à {new_price} €')
    except Exception as e:
        print(f'Erreur lors de la mise à jour de la base de données : {e}')

def main():
    if len(sys.argv) < 3:
        print('Usage: python extract_and_update.py <image_path> <article_id>')
        return

    image_path = sys.argv[1]
    article_id = sys.argv[2]

    price = extract_price_from_image(image_path)
    if price is not None:
        update_price_in_db(article_id, price)
        print(price)  # Imprime le prix pour que le script PHP puisse le récupérer
    else:
        print('0')  # Indique qu'aucun prix n'a été trouvé

if __name__ == '__main__':
    main()
