import sqlite3
from pathlib import Path
from datetime import datetime


def get_db_path():
    #chemin de la base sqlite
    db_dir = Path("/app/db")
    if not db_dir.exists():
        raise FileNotFoundError(f"dossier base introuvable: {db_dir}")
    db_path = db_dir / "ventes.db"
    if not db_path.exists():
        raise FileNotFoundError(f"fichier sqlite introuvable: {db_path}")
    return db_path


def get_conn():
    #ouverture de la connexion sqlite
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    return conn


def get_now_iso():
    #date courante au format iso
    return datetime.utcnow().isoformat(timespec="seconds")


def reset_resultats(conn):
    #nettoyage de la table des resultats
    conn.execute("delete from resultats_analyses")
    conn.commit()


def analyse_ca_total(conn):
    #calcul du chiffre d'affaires total
    sql = """
    select sum(v.quantite * p.prix) as ca_total
    from ventes v
    join produits p on v.id_produit = p.id_produit
    """
    cur = conn.execute(sql)
    row = cur.fetchone()
    ca = row[0] if row and row[0] is not None else 0.0
    now_iso = get_now_iso()
    conn.execute(
        "insert into resultats_analyses(type_resultat, cle, valeur, date_calcul) "
        "values (?, ?, ?, ?)",
        ("ca_total", "global", ca, now_iso),
    )
    conn.commit()
    print(f"ca total calcule: {ca:.2f}")


def analyse_ca_par_produit(conn):
    #calcul du chiffre d'affaires par produit (avec nom du produit)
    sql = """
    select p.nom_produit, sum(v.quantite * p.prix) as ca
    from ventes v
    join produits p on v.id_produit = p.id_produit
    group by p.nom_produit
    order by ca desc
    """
    cur = conn.execute(sql)
    rows = cur.fetchall()
    now_iso = get_now_iso()
    for nom_produit, ca in rows:
        if ca is None:
            continue
        conn.execute(
            "insert into resultats_analyses(type_resultat, cle, valeur, date_calcul) "
            "values (?, ?, ?, ?)",
            ("ca_par_produit", str(nom_produit), float(ca), now_iso),
        )
    conn.commit()
    print(f"{len(rows)} lignes de ca par produit enregistrees")


def analyse_ca_par_ville(conn):
    #calcul du chiffre d'affaires par ville
    sql = """
    select m.ville, sum(v.quantite * p.prix) as ca
    from ventes v
    join produits p on v.id_produit = p.id_produit
    join magasins m on v.id_magasin = m.id_magasin
    group by m.ville
    order by ca desc
    """
    cur = conn.execute(sql)
    rows = cur.fetchall()
    now_iso = get_now_iso()
    for ville, ca in rows:
        if ca is None:
            continue
        conn.execute(
            "insert into resultats_analyses(type_resultat, cle, valeur, date_calcul) "
            "values (?, ?, ?, ?)",
            ("ca_par_ville", str(ville), float(ca), now_iso),
        )
    conn.commit()
    print(f"{len(rows)} lignes de ca par ville enregistrees")


def main():
    #script principal d'analyse
    conn = get_conn()
    try:
        print("debut des analyses")
        reset_resultats(conn)
        analyse_ca_total(conn)
        analyse_ca_par_produit(conn)
        analyse_ca_par_ville(conn)
        print("analyses terminees et enregistrees dans resultats_analyses")
    finally:
        #fermeture propre de la connexion
        conn.close()


if __name__ == "__main__":
    main()
