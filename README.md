# Tag Heuer Data Analysis

## Introduction
Ce projet vise à extraire et analyser les données du catalogue en ligne des montres Tag Heuer, en utilisant des techniques de scraping et d'analyse des données. L'objectif est de fournir un aperçu complet des caractéristiques des montres, incluant les références, prix, dimensions, mouvement et autres attributs.

## Méthodologie
- **Collecte des données** : Un script Python avec Selenium a été utilisé pour scraper les informations sur les montres depuis le site de Tag Heuer.
- **Nettoyage des données** : Les données ont été nettoyées, incluant la gestion des valeurs manquantes, la conversion des prix en valeurs numériques et la séparation des attributs en colonnes distinctes (mouvement, diamètre, matériau).
- **Extraction des attributs** : Les attributs (mouvement, diamètre, matériau) ont été extraits pour une analyse approfondie.

## Résultats
- **Nombre total de montres** : 360 montres ont été extraites du site web.
- **Distribution des mouvements** :
    - Automatique : 215 montres
    - Quartz : 87 montres
    - Connectée : 19 montres
    - Solaire : 14 montres
    - Non applicable : 37 montres
- **Prix moyen des montres** : CHF 7,200.

## Analyses effectuées
### 1. Statistiques sur les prix
Une analyse de la distribution des prix a été effectuée, avec une concentration des prix entre CHF 3,000 et CHF 12,000.
![image alt]https://github.com/PhilippePerels/Tag-Heuer-Data-Analysis/blob/main/Distribution%20du%20prix%20des%20montres.png?raw=true

### 2. Répartition des mouvements
Les montres automatiques représentent la majorité des produits Tag Heuer, suivies par les montres à mouvement quartz et les montres connectées.

### 3. Relation entre diamètre et prix
Un nuage de points a révélé une corrélation positive entre le diamètre et le prix, avec une tendance à des prix plus élevés pour les montres de plus grand diamètre.

## Conclusion
Ce projet a permis de collecter et d'analyser des données pertinentes sur les montres Tag Heuer, fournissant un aperçu des principales caractéristiques et de la distribution des prix. 

## Instructions pour exécuter le script
1. Cloner ce dépôt :
git clone https://github.com/PhilippePerels/Tag-Heuer-Data-Analysis.git

2. Installer les dépendances :
pip install -r requirements.txt

3. Exécuter le script :
python code/scrape_tag_heuer.py


## Fichiers inclus
- `tag_heuer_watch_data_cleaned.csv` : Fichier contenant les données nettoyées et analysées.
- `code/scrape_tag_heuer.py` : Script Python utilisé pour scraper et nettoyer les données.
