import duckdb
import pandas as pd
import matplotlib.pyplot as plt

def main():
    # Chemin vers le fichier de données
    data_file = 'openfoodfacts-products.jsonl'

    # Créer une connexion DuckDB en mémoire
    con = duckdb.connect(database=':memory:')

    # Charger les données depuis le fichier JSONL
    # Si le fichier est compressé en .gz, utilisez 'openfoodfacts-products.jsonl.gz'
    con.execute(f"""
    CREATE VIEW products AS
    SELECT *
    FROM '{data_file}';
    """)

    # Exemple 1 : Compter le nombre total de produits
    total_products = con.execute("SELECT COUNT(*) FROM products;").fetchone()[0]
    print(f"Nombre total de produits : {total_products}")

    # Exemple 2 : Obtenir les 10 premiers produits avec leur nom et marque
    print("\nLes 10 premiers produits :")
    results = con.execute("""
    SELECT product_name, brands
    FROM products
    LIMIT 10;
    """).fetchall()
    for row in results:
        product_name = row[0] if row[0] else 'N/A'
        brands = row[1] if row[1] else 'N/A'
        print(f"- Produit : {product_name} | Marque : {brands}")

    # Exemple 3 : Filtrer les produits disponibles en France
    print("\nProduits disponibles en France :")
    query_france = """
    SELECT product_name, brands, countries_tags
    FROM products
    WHERE 'en:france' = ANY(countries_tags)
    LIMIT 10;
    """
    results_france = con.execute(query_france).fetchall()
    for row in results_france:
        product_name = row[0] if row[0] else 'N/A'
        brands = row[1] if row[1] else 'N/A'
        countries = ', '.join(row[2]) if row[2] else 'N/A'
        print(f"- Produit : {product_name} | Marque : {brands} | Pays : {countries}")

    # Exemple 4 : Analyse du Nutri-Score
    print("\nAnalyse du Nutri-Score :")
    query_nutriscore = """
    SELECT nutriscore_grade, COUNT(*) AS count
    FROM products
    WHERE nutriscore_grade IS NOT NULL
    GROUP BY nutriscore_grade
    ORDER BY count DESC;
    """
    df_nutriscore = con.execute(query_nutriscore).df()
    print(df_nutriscore)

    # Visualisation du Nutri-Score
    df_nutriscore.plot(kind='bar', x='nutriscore_grade', y='count', legend=False)
    plt.xlabel('Nutri-Score')
    plt.ylabel('Nombre de produits')
    plt.title('Répartition des produits par Nutri-Score')
    plt.tight_layout()
    plt.show()

    # Exemple 5 : Produits avec un Nutri-Score 'a' disponibles en France
    print("\nProduits avec un Nutri-Score 'a' disponibles en France :")
    query_nutriscore_a_france = """
    SELECT product_name, brands
    FROM products
    WHERE 'en:france' = ANY(countries_tags)
      AND nutriscore_grade = 'a'
    LIMIT 10;
    """
    results_nutriscore_a_france = con.execute(query_nutriscore_a_france).fetchall()
    for row in results_nutriscore_a_france:
        product_name = row[0] if row[0] else 'N/A'
        brands = row[1] if row[1] else 'N/A'
        print(f"- Produit : {product_name} | Marque : {brands}")

    # Exemple 6 : Analyse des catégories de produits
    query_categories = """
    SELECT category, COUNT(*) AS count
    FROM (
        SELECT UNNEST(categories_tags) AS category
        FROM products
        WHERE categories_tags IS NOT NULL
    ) subquery
    GROUP BY category
    ORDER BY count DESC
    LIMIT 10;
    """
    df_categories = con.execute(query_categories).fetchdf()

    # Affichage des résultats
    print(df_categories)

    # Visualisation
    df_categories.plot(kind='barh', x='category', y='count', legend=False)
    plt.xlabel('Nombre de produits')
    plt.ylabel('Catégorie')
    plt.title('Top 10 des catégories de produits')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()

    # Exemple 7 : Sauvegarder les résultats dans un fichier CSV
    output_file = 'produits_france_nutriscore_a.csv'
    con.execute(f"""
    COPY (
        SELECT product_name, brands, nutriscore_grade
        FROM products
        WHERE 'en:france' = ANY(countries_tags)
          AND nutriscore_grade = 'a'
    ) TO '{output_file}' (HEADER, DELIMITER ',');
    """)
    print(f"\nLes résultats ont été sauvegardés dans le fichier {output_file}")

if __name__ == "__main__":
    main()
