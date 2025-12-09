# architecture docker du projet

ce document décrit l'architecture technique du projet **analyser les ventes d'une pme** en utilisant docker et une base de données sqlite.

## objectifs

- séparer clairement le stockage de la la base de données et l'exécution des scripts python
- utiliser une base sqlite pour stocker les données de ventes, produits et magasins
- permettre de rejouer facilement l'ingestion et les analyses via des conteneurs docker
- garder une structure simple et lisible pour un petit projet de test technique

## vue d'ensemble

l'architecture repose sur deux services principaux :

- `db` : service responsable du stockage de la base sqlite
- `app` : service responsable de l'exécution des scripts python (création de la base, ingestion, analyses)

les fichiers csv et le schéma sql restent versionnés dans le dépôt git, et sont montés dans le conteneur `app` en lecture seule.

## structure des dossiers

l'arborescence cible du projet est la suivante :

```text
analyser_ventes_pme/
  README.md
  .gitignore
  docs/
    brief_projet.pdf
    architecture.md
  data/
    produits.csv
    magasins.csv
    ventes.csv
  sql/
    schema.sql
  app/
    scripts/
    __init__.py
```

- `docs/` : contient le pdf du brief et la documentation de l'architecture
- `data/` : contient les fichiers csv fournis dans le test
- `sql/` : contient le fichier `schema.sql` qui définit les tables sqlite
- `app/` : contiendra le code python et le dockerfile pour le service d'application

## description des services

### service `db`

le service `db` a un rôle simple mais important :

- il possède le volume docker qui contient le fichier sqlite (`ventes.db`)
- il peut être utilisé, si besoin, pour lancer des commandes `sqlite3` de diagnostic
- il ne publie aucun port vers l'extérieur (sqlite fonctionne sur un fichier, pas sur un serveur réseau)

caractéristiques :

- nom du service : `db`
- image : une image légère (`python:3.12-slim` par exemple) pour pouvoir utiliser facilement `sqlite3` si besoin
- volume principal :
  - `db_data:/data/db`
  - le fichier `ventes.db` sera stocké dans ce volume, typiquement à l'emplacement `/data/db/ventes.db`
- réseau : réseau par défaut de docker compose, partagé avec le service `app`

### service `app`

le service `app` est le coeur logique du projet :

- il exécute les scripts python
- il crée la base sqlite à partir de `schema.sql`
- il charge les données à partir des fichiers csv
- il lance les analyses (chiffre d'affaires global, par produit, par ville, etc.)
- il écrit les résultats dans la table `resultats_analyses`

caractéristiques :

- nom du service : `app`
- image : construite à partir d'un `Dockerfile` dans `./app` 
- volumes montés :
  - `./data:/app/data:ro` → accès aux csv en lecture seule
  - `./sql:/app/sql:ro` → accès au schéma sql en lecture seule
  - `db_data:/app/db` → accès en lecture/écriture au fichier sqlite
- dépendance :
  - `depends_on: [db]` pour s'assurer que le volume `db_data` est bien attaché avant l'exécution des scripts

## schéma d'architecture (vue texte)

la vue générale des flux est la suivante :

```text
+----------------------+       volume        +----------------------+
|        db            |<------------------->|         app          |
|                      |   db_data          |   scripts python     |
|  /data/db/ventes.db  |                    |  /app/db/ventes.db   |
+----------------------+                    +----------------------+

          ^                                           ^
          |                                           |
          |                                           |
          |                         +-----------------+-------------------+
          |                         |                                 |
          |               ./data -> /app/data               ./sql -> /app/sql
          |               (csv)                            (schema.sql)
```

- le service `db` est responsable du volume `db_data` qui contient le fichier `ventes.db`
- le service `app` monte ce même volume dans `/app/db` pour pouvoir lire et écrire dans la base
- le dossier local `data/` est monté dans `/app/data` pour lire les fichiers csv
- le dossier local `sql/` est monté dans `/app/sql` pour utiliser le fichier `schema.sql`

## exemple potentiel du fichier docker-compose


```yaml
version: "3.9"

services:
  db:
    image: python:3.12-slim
    volumes:
      - db_data:/data/db

  app:
    build: ./app
    depends_on:
      - db
    volumes:
      - ./data:/app/data:ro
      - ./sql:/app/sql:ro
      - db_data:/app/db

volumes:
  db_data:
```

ce fichier sera ajouté à la racine du projet, et le `Dockerfile` du service `app` sera créé dans le dossier `app/`. on ajoutera aussi un premier script python de test pour vérifier que les conteneurs démarrent correctement.

## traçabilité git

toutes les étapes  doivent être versionnées séparément pour que l'historique soit lisible.

exemple de commandes git à lancer après la création de ce fichier et du dossier `app/` :

```bash
git add docs/architecture.md app/
git commit -m "ajout conception architecture docker deux services"
git push
```

cela permet de voir clairement dans l'historique :

- un premier commit pour l'initialisation du projet et le modèle de données (étape 1)
- un deuxième commit pour la conception de l'architecture docker (étape 2)
