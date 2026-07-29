# CyberLab Education Platform

# Architecture Technique de Référence

Version : v0.3-phase-c2
Phase actuelle : Phase C.2 (Composition Root & Intégration Flask)
Nombre de tests validés : 244

==================================================

1. Vision et objectifs du système
==================================================

* **Plateforme CyberLab offline :** CyberLab Education Platform est conçue comme un système éducatif robuste orienté *offline/edge*, permettant un déploiement autonome au sein d'institutions et de structures éducatives sans dépendance critique à une connexion Internet permanente.
* **Objectif pédagogique :** Fournir un environnement d'apprentissage pratique pour l'enseignement de la cybersécurité, de l'administration réseau et de l'informatique technique à destination d'un public jeune et d'étudiants.
* **Public cible :** Élèves, clubs scientifiques, et instructeurs techniques encadrant des sessions d'apprentissage pratique.
* **Contraintes opérationnelles et techniques :**
* Fonctionnement entièrement hors ligne (local-first).
* Adapté aux laboratoires informatiques scolaires aux ressources matérielles hétérogènes ou limitées.
* Architecture modulaire permettant l'évolution des programmes pédagogiques et des modules de TP sans impacter le cœur du système.



==================================================
2. Architecture globale

La plateforme repose sur une application stricte des principes de la **Clean Architecture** et du **Domain-Driven Design (DDD)**, garantissant une séparation claire et inviolable des responsabilités à travers des couches concentriques.

**Schéma global du flux de dépendances :**

```text
Utilisateur
 |
Flask API
 |
Composition Root / Container
 |
Application
 |
Domain
 |
Infrastructure
 |
Database

```

==================================================
3. Structure réelle du projet

L'arborescence officielle et effective du projet reflète l'organisation modulaire suivante :

```text
CyberLab/
├── api/
│   ├── error_handlers.py
│   └── v1/
│       ├── auth_api.py
│       └── labs_api.py
├── bootstrap/
│   └── container.py
├── core/
│   ├── app_factory.py
│   ├── blueprint_loader.py
│   └── extensions.py
├── config/
│   └── settings.py
├── database/
│   ├── base.py
│   ├── session.py
│   └── models/
│       ├── lab.py
│       ├── progress.py
│       └── user.py
├── domain/
│   └── labs/
│       ├── entities/
│       │   └── lab_instance.py
│       └── value_objects/
│           ├── lab_id.py
│           ├── lab_status.py
│           └── student_id.py
├── infrastructure/
│   └── repositories/
│       ├── sqlalchemy_lab_instance_repository.py
│       ├── sqlalchemy_lab_repository.py
│       └── sqlalchemy_student_repository.py
├── docs/
│   └── ARCHITECTURE.md
└── tests/
    ├── core/
    │   └── test_app_factory_container.py
    └── infrastructure/
        └── repositories/
            └── test_sqlalchemy_lab_instance_repository.py

```

==================================================
4. Règles architecturales

* **Dependency Rule :** La règle de dépendance est unidirectionnelle et pointe toujours vers l'intérieur. Les couches externes peuvent dépendre des couches internes, mais les couches internes (Domaine, Application) ignorent totalement l'existence des couches externes (Infrastructure, Framework web).
* **Absence de dépendance Flask dans le Domain :** Le code situé dans `domain/` ne contient aucun import ni référence au framework Flask ou à un quelconque protocole HTTP.
* **Absence de SQLAlchemy dans Application / Domain :** Les use cases et les entités métier n'importent jamais l'ORM SQLAlchemy ni de concepts liés directement aux pilotes de bases de données relationnelles.
* **Rôle des Ports :** Les ports définissent les contrats (interfaces) métier abstraits que l'infrastructure doit implémenter pour permettre aux use cases de persister ou de récupérer des données sans couplage fort.
* **Rôle des Adapters :** Les adapters (situés dans `infrastructure/`) implémentent concrètement les ports en effectuant la traduction entre les objets du domaine et les modèles de persistance ou services externes.

==================================================
5. Composition Root et Dependency Injection

* **Emplacement du Container :** Le conteneur d'injection de dépendances est centralisé dans le fichier `bootstrap/container.py`.
* **Rôle du Container :** Il agit en tant que point unique d'assemblage (Composition Root) pour instancier les repositories d'infrastructure en leur injectant la session de base de données active, puis assemble les use cases et services métier associés.
* **Cycle d'initialisation :**
1. Démarrage de Flask via la factory (`core/app_factory.py`).
2. Enregistrement des extensions et initialisation de la session SQLAlchemy (`app.db_session`).
3. Instanciation du conteneur injecté avec la session active : `container = Container(app.db_session)`.
4. Stockage du conteneur dans le contexte de l'application : `app.extensions["container"] = container`.
5. Chargement des Blueprints et liaison via le chargeur dédié (`core/blueprint_loader.py`).





















## 1. Vue globale

La plateforme **CyberLab Education Platform** repose sur une architecture logicielle stricte combinant les principes de la **Clean Architecture** et du **Domain-Driven Design (DDD)**, conçue pour un fonctionnement orienté offline/edge adapté aux environnements éducatifs institutionnels.

L'objectif de la **Phase C.2** a été de mettre en place une **Composition Root** robuste via un conteneur d'injection de dépendances (`Container`) et de l'intégrer proprement au cycle de vie du framework web Flask, tout en garantissant l'hermétisme absolu du domaine métier.

   [ Client / Navigateur HTTP ]
                │
                ▼
      [ Flask Framework ]
   (app_factory & Blueprints)
                │
                ▼  (Récupère container via app.extensions)
  [ Composition Root / Container ]
(Résolution des Use Cases & Repositories)│▼[ Couche Application ](Use Cases / DTOs)│▼[ Couche Domaine ] ── (Pur, sans dépendance externe)(Entités / Value Objects)│▲  (Implémente les Ports)[ Couche Infrastructure ](SQLAlchemy natif / app.db_session)
---

## 2. Arborescence réelle du projet CyberLab

```text
CyberLab/
├── api/
│   ├── error_handlers.py
│   └── v1/
│       ├── auth_api.py
│       └── labs_api.py
├── bootstrap/
│   └── container.py
├── core/
│   ├── app_factory.py
│   ├── blueprint_loader.py
│   └── extensions.py
├── config/
│   └── settings.py
├── database/
│   ├── base.py
│   ├── session.py
│   └── models/
│       ├── lab.py
│       ├── progress.py
│       └── user.py
├── domain/
│   └── labs/
│       ├── entities/
│       │   └── lab_instance.py
│       └── value_objects/
│           ├── lab_id.py
│           ├── lab_status.py
│           └── student_id.py
├── infrastructure/
│   └── repositories/
│       ├── sqlalchemy_lab_instance_repository.py
│       ├── sqlalchemy_lab_repository.py
│       └── sqlalchemy_student_repository.py
├── docs/
│   └── ARCHITECTURE_PHASE_C2.md
└── tests/
    ├── core/
    │   └── test_app_factory_container.py
    └── infrastructure/
        └── repositories/
            └── test_sqlalchemy_lab_instance_repository.py
3. Dependency Graph complet du ContainerLe conteneur d'injection (bootstrap/container.py) gère la composition hiérarchique des objets de la manière suivante :Services Domaine / Logique Métier :Validation des flags et règles d'exécution des laboratoires.Use Cases (Couche Application) :StartLabUseCase (dépend du Repository d'instances de lab).SubmitFlagUseCase (dépend des services de validation et des repositories).Repositories (Ports d'Infrastructure) :SqlAlchemyLabRepositorySqlAlchemyStudentRepositorySqlAlchemyLabInstanceRepositoryAdapters / Infrastructure :ChallengeValidationAdapterEventBusAdapter


4. Tableau de Répartition des CouchesCoucheComposantResponsabilitéDomaineLabInstance, LabId, StudentId, LabStatusModélisation des règles métier pures et des objets de valeur (Value Objects), totalement agnostiques de toute technologie.ApplicationStartLabUseCase, SubmitFlagUseCaseOrchestration des cas d'usage métiers et manipulation des frontières d'entrée/sortie sous forme de DTOs.InfrastructureSqlAlchemyLabInstanceRepository, Modèles ORM (UserModel, LabModel, ProgressModel)Implémentation technique des ports du domaine via SQLAlchemy natif et gestion de la persistance SQLite.Framework / Interfaceapp_factory.py, blueprint_loader.py, Blueprints Flask (auth_api.py, labs_api.py)Exposition des points de terminaison HTTP, gestion du cycle de vie de l'application et routage des requêtes vers les services.Composition RootContainer (bootstrap/container.py)Point unique d'assemblage et d'injection des dépendances liant l'infrastructure au domaine.

## 5. Tableau Ports ↔ Implémentations InfrastructurePort Métier 

/ ContratImplémentation InfrastructureSupport de StockageRepository de LaboratoiresSqlAlchemyLabRepositoryTable ORM LabModelRepository d'ÉtudiantsSqlAlchemyStudentRepositoryTable ORM UserModelRepository d'Instances de LabsSqlAlchemyLabInstanceRepositoryTable ORM ProgressModelAdaptateur de ValidationChallengeValidationAdapterMoteur de validation externe / interne

6. Mapping Domaine ↔ ORMObjet Domaine / Value ObjectModèle ORM (Infrastructure)Stratégie de CorrespondanceLabIdLabModel.lab_idConversion de l'identifiant métier textuel/technique vers la colonne technique de la table.StudentIdProgressModel.user_id / UserModel.idCorrespondance directe avec l'identifiant numérique de l'utilisateur.LabInstanceProgressModelReconstruction de l'entité agrégée à partir des colonnes relationnelles (domain_id, status, started_at, completed_at).ProgressProgressModelSuivi de l'état d'avancement persisté en base de données.Flags / ValidationChallengeValidationAdapterTraitement orienté service consommateur des flags soumis par l'étudiant.7. Architecture Decision Records (ADR)ADR-01 : Choix d'un SQLAlchemy natif sans Flask-SQLAlchemy global magiqueStatut : Validé (Phase C.2)Contexte : Le projet nécessite un contrôle strict du cycle de vie des sessions pour des environnements offline et une isolation totale des repositories.Décision : Utilisation d'un moteur et d'une session SQLAlchemy instanciés explicitement via des fonctions d'extension (core/extensions.py) et attachés au contexte de l'application Flask (app.db_session).Conséquence : Pas de dépendance cachée au framework dans les couches basses ; le Container reçoit directement la session active.ADR-02 : Container d'injection de dépendances manuel (Pure DI)Statut : Validé (Phase C.2)Contexte : Éviter l'utilisation de frameworks DI lourds ou magiques pour conserver une transparence totale du code et faciliter les tests unitaires.Décision : Implémentation d'une classe Container pure Python centralisant l'instanciation des dépendances.Conséquence : Maîtrise absolue du graphe d'objets, injection simplifiée dans les tests et absence de couplage au framework.ADR-03 : Séparation stricte Flask / DomaineStatut : Validé (Phase C.2)Contexte : Garantir la règle fondamentale de la Clean Architecture où le domaine ignore tout de l'infrastructure web.Décision : Les Blueprints utilisent des fonctions factories et un chargeur dédié (core/blueprint_loader.py) pour extraire les cas d'usage du conteneur sans polluer les entités métier.Conséquence : Le code métier reste testable unitairement en dehors de tout serveur HTTP.8. État d'avancement global du projetPhase A : Structuration du Domaine et des Value Objects — 
✅ TerminéPhase B : Implémentation des Use Cases et des Ports — 
✅ TerminéPhase C.1 : Développement des Adaptateurs d'Infrastructure et Tests de Repositories — 
✅ TerminéPhase C.2 : Composition Root et Intégration Flask (v0.3-phase-c2) — 
✅ Terminé (244 tests au vert)Phase D : Implémentation du premier flux métier End-to-End (StartLabUseCase) — 
⏳ Planifié9. Règles de contribution pour les futures phasesRègle de l'Isolation : Aucun code placé dans domain/ ou application/ ne doit importer des modules provenant de flask, sqlalchemy ou de l'infrastructure.Règle des Tests (TDD) : Toute modification ou ajout de fonctionnalité doit être précédée ou accompagnée de tests unitaires ou d'intégration dont la non-régression est validée par pytest.Règle du Container : Les dépendances des nouveaux cas d'usage doivent obligatoirement être enregistrées et résolues via le Container (bootstrap/container.py) et transmises aux couches d'interface via les mécanismes validés de l'application.Interdiction d'import circulaire : Veiller à ce que les adaptateurs d'infrastructure ne dépendent pas des points d'entrée de l'API web.