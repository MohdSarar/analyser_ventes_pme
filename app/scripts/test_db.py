import sqlite3
from pathlib import Path


def init_db_path():
    #chemin du dossier de la base
    db_dir = Path("/app/db")
    if not db_dir.exists():
        #creation du dossier si besoin
        db_dir.mkdir(parents=True, exist_ok=True)
    #nom du fichier sqlite
    db_path = db_dir / "ventes.db"
    return db_path


def main():
    #script de test pour la base sqlite
    db_path = init_db_path()
    #ouverture de la connexion sqlite
    conn = sqlite3.connect(db_path)
    try:
        #creation d'une petite table de ping
        conn.execute(
            "create table if not exists ping (id integer primary key, message text)"
        )
        conn.execute("insert into ping(message) values (?)", ("docker ok",))
        conn.commit()
        #lecture du dernier message inséré
        row = conn.execute(
            "select id, message from ping order by id desc limit 1"
        ).fetchone()
        print(f"base sqlite ok, dernier message: {row}")
    finally:
        #fermeture propre de la connexion
        conn.close()


if __name__ == "__main__":
    main()
