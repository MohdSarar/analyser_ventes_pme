# analyser les ventes d'une pme

Ce dépôt sert de support pour un exercice de data engineer. l'idée est de créer une petite architecture avec une base sqlite et des scripts pour analyser les ventes d'une pme à partir de fichiers csv.

## les données

les données proviennent de trois fichiers csv :

- `produits.csv` : liste des produits, leur prix et le stock
- `magasins.csv` : liste des magasins avec la ville et le nombre de salariés
- `ventes.csv` : historique des ventes (date, produit, quantité, magasin)

## modèle de base de données

le modèle relationnel est le suivant :

- `produits(id_produit, nom_produit, prix, stock)`
- `magasins(id_magasin, ville, nombre_salaries)`
- `ventes(id_vente, date_vente, id_produit, id_magasin, quantite)`
- `resultats_analyses(id_resultat, type_resultat, cle, valeur, date_calcul)`

la table `ventes` est liée à `produits` et `magasins` par des clés étrangères, avec une contrainte d'unicité sur `(date_vente, id_produit, id_magasin)` pour éviter les doublons.

dans la suite du projet, la table `resultats_analyses` servira à stocker le résultat des requêtes (chiffre d'affaires global, par produit, par ville, etc.).
