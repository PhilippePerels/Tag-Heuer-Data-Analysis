from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configurer les options de Chrome
options = Options()
options.add_argument("--headless")  # Exécuter en mode headless si nécessaire
options.add_argument("user-agent=Mozilla/5.0")
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_experimental_option('useAutomationExtension', False)

# Initialiser le driver
driver = webdriver.Chrome(options=options)

def scroll_to_bottom():
    """Scrolle jusqu'en bas de la page pour charger tous les produits."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    print("Toutes les montres sont chargées.")

def get_data(url, category):
    """Scrape les données d'une page spécifique."""
    driver.get(url)
    try:
        accept_cookies = driver.find_element(By.ID, 'onetrust-accept-btn-handler')
        accept_cookies.click()
        print("Pop-up des cookies fermée.")
    except Exception as e:
        print("Pas de pop-up cookies trouvée.")
    
    scroll_to_bottom()
    time.sleep(2)  # Attendre pour s'assurer que tous les produits sont chargés
    
    watches = []
    products = driver.find_elements(By.CSS_SELECTOR, 'th-product-tile')

    for product in products:
        try:
            shadow_root = driver.execute_script('return arguments[0].shadowRoot', product)
            attributes = shadow_root.find_element(By.CSS_SELECTOR, 'span.product-tile__attributes').text.strip()
            name = shadow_root.find_element(By.CSS_SELECTOR, 'h2.product-tile__collection').text.strip()
            price = shadow_root.find_element(By.CSS_SELECTOR, 'span.product-tile__sales-value').text.strip()

            gtmdata = product.get_attribute('data-gtmdata')
            if gtmdata:
                watch_info = json.loads(gtmdata)
                watch_id = watch_info.get('id')
                brand = watch_info.get('brand')
                category_gtm = watch_info.get('category')
            else:
                watch_id = "N/A"
                brand = "N/A"
                category_gtm = "N/A"

            watches.append({
                'id': watch_id,
                'name': name,
                'price': price,
                'brand': brand,
                'category': category_gtm,
                'attributes': attributes,
                'category_type': category
            })
        except Exception as e:
            print(f"Erreur lors de l'extraction d'un produit: {e}")
            continue
    return watches

if __name__ == "__main__":
    urls = {
        'https://www.tagheuer.com/ch/fr/montres/decouvrir/homme/': 'Montres homme',
        'https://www.tagheuer.com/ch/fr/montres/decouvrir/femme/': 'Montres femme',
        'https://www.tagheuer.com/ch/fr/montres/decouvrir/editions-speciales/': 'Montres éditions spéciales',
        'https://www.tagheuer.com/ch/fr/montres/decouvrir/montres-chronographe/': 'Montres chronographe',
        'https://www.tagheuer.com/ch/fr/montres-connectees/collections/tag-heuer-connected/tag-heuer-connected-calibre-e4-45-mm/': 'Montres connectées 45mm',
        'https://www.tagheuer.com/ch/fr/montres-connectees/collections/tag-heuer-connected/tag-heuer-connected-calibre-e4-42-mm/': 'Montres connectées 42mm',
        'https://www.tagheuer.com/ch/fr/nos-solaires/': 'Eyewear'
    }

    all_watches_data = []

    for url, category in urls.items():
        watches = get_data(url, category)
        all_watches_data.extend(watches)
        print(f"{len(watches)} montres trouvées sur {url}")

    # Créer le DataFrame
    df = pd.DataFrame(all_watches_data)

    # Nettoyer les données et extraire les attributs
    def parse_attributes(attr):
        mouvement, diametre, materiau = "N/A", "N/A", "N/A"
        if attr and attr != "N/A":
            parts = [part.strip() for part in attr.split(',')]
            for part in parts:
                if "mm" in part:
                    diametre = part
                elif part.lower() in ["automatique", "manuelle", "quartz"]:
                    mouvement = part
                else:
                    materiau = part
        return pd.Series([mouvement, diametre, materiau])

    df[['Mouvement', 'Diamètre', 'Matériau']] = df['attributes'].apply(parse_attributes)

    # Réorganiser les colonnes
    df = df[['id', 'name', 'price', 'brand', 'category', 'Mouvement', 'Diamètre', 'Matériau', 'category_type']]

    # Sauvegarder dans un fichier CSV
    df.to_csv('tag_heuer_watch_data_cleaned.csv', index=False)

    # Afficher les premières lignes pour vérifier
    print(f"Nombre total de montres trouvées : {len(df)}")
    print(df.head())

    driver.quit()

# Nettoyage et conversion des prix
df['price_clean'] = df['price'].str.replace("CHF", "", regex=False)\
                                .str.replace("'", "", regex=False)\
                                .str.replace(",", "", regex=False)\
                                .str.strip()

df['price_clean'] = df['price_clean'].replace('Prix sur demande', np.nan)
df['price_numeric'] = pd.to_numeric(df['price_clean'], errors='coerce')

# Analyse des prix
plt.figure(figsize=(10,6))
df['price_numeric'].hist(bins=20)
plt.title('Distribution des prix des montres')
plt.xlabel('Prix (CHF)')
plt.ylabel('Nombre de montres')
plt.show()

# Répartition par mouvement
movement_counts = df['Mouvement'].value_counts()
print(movement_counts)

# Moyenne des prix par mouvement
moyenne_prix_par_mouvement = df.groupby('Mouvement')['price_numeric'].mean()
print(moyenne_prix_par_mouvement)

# Correction des mouvements pour les montres connectées et solaires
df['type_produit'] = df['category_type'].apply(lambda x: 'Montre connectée' if 'connectée' in x.lower() else ('Lunettes' if 'eyewear' in x.lower() else 'Montre classique'))
df.loc[df['type_produit'] == 'Montre connectée', 'Mouvement'] = 'Connectée'
df.loc[df['name'].str.contains('SOLARGRAPH', case=False, na=False), 'Mouvement'] = 'Solaire'

# Relation diamètre/prix
df_filtered = df[df['Diamètre'].str.contains('mm')].copy()
df_filtered['Diamètre_numeric'] = df_filtered['Diamètre'].str.replace(' mm', '').astype(float)

plt.figure(figsize=(10, 6))
plt.scatter(df_filtered['Diamètre_numeric'], df_filtered['price_numeric'], alpha=0.5, c='blue')
plt.title('Relation entre le diamètre et le prix des montres')
plt.xlabel('Diamètre (mm)')
plt.ylabel('Prix (CHF)')
plt.grid(True)
plt.show()

# Boxplot des prix par type de mouvement
plt.figure(figsize=(10, 6))
sns.boxplot(x='Mouvement', y='price_numeric', data=df)
plt.title('Répartition des prix par type de mouvement')
plt.xlabel('Type de mouvement')
plt.ylabel('Prix (CHF)')
plt.xticks(rotation=45)
plt.show()

# Boxplot des prix par catégorie
plt.figure(figsize=(12, 6))
category_order = df.groupby('category_type')['price_numeric'].median().sort_values().index
sns.boxplot(x='category_type', y='price_numeric', data=df, order=category_order)
plt.title('Distribution des prix selon la catégorie des montres')
plt.xlabel('Catégorie de montres')
plt.ylabel('Prix (CHF)')
plt.xticks(rotation=45)
plt.grid(True)
plt.show()
