import sqlite3
import csv
from pathlib import Path
from datetime import datetime


def get_db_path():
    #chemin de la base sqlite
    db_dir = Path("/app/db")
    if not db_dir.exists():
        #creation du dossier si besoin
        db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / "ventes.db"
    return db_path


def get_schema_path():
    #chemin du fichier schema sql
    return Path("/app/sql/schema.sql")


def get_data_dir():
    #chemin du dossier des csv
    return Path("/app/data")


def init_schema(conn):
    #initialisation du schema sqlite a partir du fichier sql
    schema_path = get_schema_path()
    if not schema_path.exists():
        raise FileNotFoundError(f"schema sql introuvable: {schema_path}")
    with schema_path.open("r", encoding="utf-8") as f:
        sql_script = f.read()
    conn.executescript(sql_script)
    conn.commit()


def nettoyer_prix(val):
    #conversion d'un prix texte en float
    if val is None:
        return 0.0
    txt = str(val).strip()
    if not txt:
        return 0.0
    txt = txt.replace("€", "")
    txt = txt.replace(" ", "")
    txt = txt.replace("\u00a0", "")
    txt = txt.replace(",", ".")
    #gestion des separateurs de milliers eventuels
    if txt.count(".") > 1:
        parts = txt.split(".")
        txt = "".join(parts[:-1]) + "." + parts[-1]
    try:
        return float(txt)
    except ValueError:
        return 0.0



def nettoyer_int(val):
    #conversion d'une valeur texte en entier
    if val is None:
        return 0
    txt = str(val).strip()
    if not txt:
        return 0
    txt = txt.replace(" ", "")
    try:
        return int(txt)
    except ValueError:
        return 0


def normaliser_date(val):
    #normalisation simple de la date en yyyy-mm-dd si possible
    if val is None:
        return ""
    txt = str(val).strip()
    if not txt:
        return ""
    #format jour/mois/annee classique
    try:
        if "/" in txt:
            d = datetime.strptime(txt, "%d/%m/%Y")
            return d.strftime("%Y-%m-%d")
    except ValueError:
        pass
    #si deja en yyyy-mm-dd on laisse comme ca
    return txt


def load_produits(conn):
    #chargement de la table produits
    data_dir = get_data_dir()
    path = data_dir / "produits.csv"
    if not path.exists():
        raise FileNotFoundError(f"csv produits introuvable: {path}")

    conn.execute("delete from produits")
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=",")
        rows = []
        for row in reader:
            ref = row.get("ID Référence produit", "").strip()
            nom = row.get("Nom", "").strip()
            prix = nettoyer_prix(row.get("Prix"))
            stock = nettoyer_int(row.get("Stock"))
            if not ref:
                continue
            rows.append((ref, nom, prix, stock))
        conn.executemany(
            "insert into produits(id_produit, nom_produit, prix, stock) values (?, ?, ?, ?)",
            rows,
        )
    conn.commit()
    print(f"{len(rows)} produits charges")


def load_magasins(conn):
    #chargement de la table magasins
    data_dir = get_data_dir()
    path = data_dir / "magasins.csv"
    if not path.exists():
        raise FileNotFoundError(f"csv magasins introuvable: {path}")

    conn.execute("delete from magasins")
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=",")
        rows = []
        for row in reader:
            id_mag = nettoyer_int(row.get("ID Magasin"))
            ville = row.get("Ville", "").strip()
            nb_sal = nettoyer_int(row.get("Nombre de salariés"))
            if not id_mag:
                continue
            rows.append((id_mag, ville, nb_sal))
        conn.executemany(
            "insert into magasins(id_magasin, ville, nombre_salaries) values (?, ?, ?)",
            rows,
        )
    conn.commit()
    print(f"{len(rows)} magasins charges")


def load_ventes(conn):
    #chargement de la table ventes sans doublons
    data_dir = get_data_dir()
    path = data_dir / "ventes.csv"
    if not path.exists():
        raise FileNotFoundError(f"csv ventes introuvable: {path}")

    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=",")
        rows = []
        for row in reader:
            date_brut = row.get("Date", "")
            date_sql = normaliser_date(date_brut)
            ref = row.get("ID Référence produit", "").strip()
            id_mag = nettoyer_int(row.get("ID Magasin"))
            qte = nettoyer_int(row.get("Quantité"))
            if not date_sql or not ref or not id_mag or not qte:
                continue
            rows.append((date_sql, ref, id_mag, qte))
        conn.executemany(
            "insert or ignore into ventes(date_vente, id_produit, id_magasin, quantite) "
            "values (?, ?, ?, ?)",
            rows,
        )
    conn.commit()
    print(f"{len(rows)} lignes de ventes traitees (doublons eventuels ignores)")


def main():
    #pipeline principal de creation de base et ingestion
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        print(f"utilisation de la base sqlite: {db_path}")
        init_schema(conn)
        print("schema sqlite initialise")
        load_produits(conn)
        load_magasins(conn)
        load_ventes(conn)
        print("pipeline ingestion termine")
    finally:
        #fermeture propre de la connexion
        conn.close()


if __name__ == "__main__":
    main()
