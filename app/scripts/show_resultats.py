import sqlite3
from pathlib import Path


def get_db_path():
    #chemin de la base sqlite
    db_dir = Path("/app/db")
    db_path = db_dir / "ventes.db"
    return db_path


def main():
    #affichage des resultats d'analyses
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute(
            "select type_resultat, cle, valeur "
            "from resultats_analyses "
            "order by type_resultat, valeur desc"
        )
        for type_res, cle, val in cur:
            print(f"{type_res:15s} | {cle:20s} | {val:.2f}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
