# Spécification de l'Unit of Work (UoW) — CyberLab

Ce document définit le pattern Unit of Work chargé de garantir l'atomicité et la cohérence transactionnelle des opérations métier de la plateforme CyberLab.

## 1. Responsabilités
* **Gestion des transactions :** Coordonner l'ouverture, la validation (`commit`) ou l'annulation (`rollback`) des transactions sur la base de données SQLite via la session SQLAlchemy (`app.db_session`).
* **Registre (Identity Map) :** Assurer qu'une même entité chargée en mémoire n'est instanciée qu'une seule fois au cours d'une même transaction.
* **Collecte et Dispatch des Domain Events :** Extraire les événements métiers accumulés par les agrégats modifiés au cours de la transaction et les publier via l'EventBus juste avant ou juste après le commit.

## 2. Cycle de Vie
1. **Ouverture :** Déclenchée au début d'un Use Case (généralement via un middleware ou une injection explicite dans le conteneur).
2. **Exécution :** Les repositories enregistrent les modifications d'état des entités dans le contexte de l'UoW.
3. **Clôture (Succès) :** Appel de `commit()`. L'UoW valide la transaction SQLite et déclenche la publication des Domain Events collectés.
4. **Clôture (Échec) :** En cas d'exception métier ou technique non gérée dans le Use Case, appel automatique de `rollback()` et purge des événements en attente.

## 3. Relation avec les Composants
* **SQLAlchemy :** L'UoW encapsule directement la session SQLAlchemy native fournie par l'infrastructure Flask (`app.db_session`). Elle ne expose aucun objet ORM brut vers le domaine.
* **Repositories :** Les repositories reçoivent l'instance de l'UoW ou de la session active pour attacher les entités au mécanisme de suivi des modifications.
* **EventBus :** L'UoW fait office de coordinateur de publication. Les événements ne sont pas envoyés au fil de l'eau pendant l'exécution des méthodes du domaine, mais collectés par l'UoW pour être publiés de manière atomique au moment du commit.

## 4. Choix Architecturaux
* **Pourquoi un UoW manuel ?** Pour éviter la complexité des frameworks ORM lourds tout en maintenant un contrôle absolu sur les frontières transactionnelles dans un environnement SQLite soumis à des contraintes de verrouillage local.