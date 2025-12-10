PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS produits (
    id_produit TEXT PRIMARY KEY,
    nom_produit TEXT NOT NULL,
    prix REAL NOT NULL,
    stock INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS magasins (
    id_magasin INTEGER PRIMARY KEY,
    ville TEXT NOT NULL,
    nombre_salaries INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS ventes (
    id_vente INTEGER PRIMARY KEY AUTOINCREMENT,
    date_vente TEXT NOT NULL,
    id_produit TEXT NOT NULL,
    id_magasin INTEGER NOT NULL,
    quantite INTEGER NOT NULL,
    FOREIGN KEY (id_produit) REFERENCES produits(id_produit),
    FOREIGN KEY (id_magasin) REFERENCES magasins(id_magasin),
    UNIQUE (date_vente, id_produit, id_magasin)
);

CREATE TABLE IF NOT EXISTS resultats_analyses (
    id_resultat INTEGER PRIMARY KEY AUTOINCREMENT,
    type_resultat TEXT NOT NULL,
    cle TEXT NOT NULL,
    valeur REAL NOT NULL,
    date_calcul TEXT NOT NULL
);
