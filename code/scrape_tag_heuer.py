from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import json

# Configurer les options de Chrome
options = Options()
options.add_argument("--headless")  # Exécuter en mode headless si nécessaires
options.add_argument("user-agent=Mozilla/5.0")
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_experimental_option('useAutomationExtension', False)

# Initialiser le driver
driver = webdriver.Chrome(options=options)

def scroll_to_bottom():
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

    # Trouver tous les éléments de montres
    products = driver.find_elements(By.CSS_SELECTOR, 'th-product-tile')

    for product in products:
        try:
            # Accéder au Shadow DOM
            shadow_root = driver.execute_script('return arguments[0].shadowRoot', product)

            # Extraire les attributs
            try:
                attributes = shadow_root.find_element(By.CSS_SELECTOR, 'span.product-tile__attributes').text.strip()
            except:
                attributes = "N/A"

            # Extraire les autres détails
            try:
                name = shadow_root.find_element(By.CSS_SELECTOR, 'h2.product-tile__collection').text.strip()
            except:
                name = "N/A"

            try:
                price = shadow_root.find_element(By.CSS_SELECTOR, 'span.product-tile__sales-value').text.strip()
            except:
                price = "N/A"

            # Extraire l'attribut data-gtmdata depuis l'élément hôte
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

            # Ajouter les données à la liste
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
    'https://www.tagheuer.com/ch/fr/montres/decouvrir/editions-speciales/': 'Montres editions speciales',
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

    # Nettoyer les données et séparer les attributs en colonnes distinctes
    # Fonction pour extraire le mouvement, le diamètre et le matériau
    def parse_attributes(attr):
        mouvement = "N/A"
        diametre = "N/A"
        materiau = "N/A"

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

    # Appliquer la fonction au DataFrame
    df[['Mouvement', 'Diamètre', 'Matériau']] = df['attributes'].apply(parse_attributes)

    # Réorganiser les colonnes
    df = df[['id', 'name', 'price', 'brand', 'category', 'Mouvement', 'Diamètre', 'Matériau', 'category_type']]

    # Sauvegarder dans un fichier CSV
    df.to_csv('tag_heuer_watch_data_cleaned.csv', index=False)

    # Afficher les premières lignes pour vérifier
    print(f"Nombre total de montres trouvées : {len(df)}")
    print(df.head())

    driver.quit()
