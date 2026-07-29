Document Officiel de Conception : PHASE E.1.1 — ARCHITECTURE HARDENING
En tant que Lead Software Architect, je présente le document de spécification architecturale pour la sous-phase de durcissement (Hardening). L'objectif est de sécuriser le socle technique de CyberLab avant l'introduction des flux métiers réels, en ciblant spécifiquement les limites physiques d'une base SQLite exploitée simultanément par 20 à 40 étudiants en mode offline.

Conformément aux directives strictes de la plateforme, aucun code source n'est inclus dans ce document.

PARTIE 1 — Objectifs Phase E.1.1
La Phase E.1.1 a pour but exclusif de transformer une architecture théoriquement saine en un système physiquement résilient. Les objectifs sont :

Prévenir les blocages concurrentiels (database is locked) inhérents à SQLite.

Garantir la cohérence des données en cas de contention réseau ou disque.

Protéger le domaine de la Gamification contre la duplication des récompenses.

Contrôler la propagation événementielle pour éviter la surcharge du thread HTTP.

Établir les normes de traçabilité (Correlation ID) pour faciliter le débogage hors ligne.

PARTIE 2 — Analyse des risques actuels
L'audit précédent a mis en lumière plusieurs failles physiques dans notre modèle actuel :

Risque de verrouillage SQLite (Haute probabilité) : L'UoW principal commit, déclenchant l'EventBus synchrone, qui déclenche un Handler ouvrant un nouvel UoW. Avec 30 requêtes simultanées, SQLite va inévitablement lever une erreur sqlite3.OperationalError: database is locked.

Risque d'incohérence par manque de Retry (Haute probabilité) : En l'absence de mécanisme de nouvelle tentative, un verrouillage temporaire se traduit par un échec définitif de l'opération (ex: perte des points d'un étudiant).

Risque de non-idempotence (Moyenne probabilité) : Si un client renvoie une requête ou si un événement est rejoué, le système risque d'attribuer plusieurs fois les points pour le même laboratoire.

Risque de boucle infinie (Faible probabilité, Impact critique) : Un événement A déclenche un événement B qui redéclenche A, provoquant un crash par dépassement de pile (Stack Overflow) ou un timeout HTTP.

PARTIE 3 — Décisions architecturales proposées
1. Stratégie de Résilience SQLite
Configuration :

journal_mode=WAL (Write-Ahead Logging) : Permet la lecture et l'écriture simultanées.

busy_timeout=5000 (5 secondes) : Demande à SQLite de patienter au lieu de rejeter immédiatement une transaction bloquée.

foreign_keys=ON : Garantie de l'intégrité référentielle.

Isolation et durée : Niveau d'isolation par défaut (Serializable pour SQLite). Les transactions doivent être extrêmement courtes (lecture, vérification métier, enregistrement événement, écriture).

Emplacement architectural : Couche Infrastructure, lors de l'initialisation de l'Engine SQLAlchemy (via les événements connect de SQLAlchemy).

2. Politique de Retry (Retry Policy)
Déclencheur : Exclusivement ciblé sur les exceptions d'accès concurrentiel (sqlite3.OperationalError contenant "database is locked").

Stratégie : Retry purement Python (sans librairie externe lourde type Celery). Utilisation d'un backoff exponentiel avec "jitter" (délai aléatoire) pour éviter le problème du "troupeau de tonnerre" (thundering herd).

Paramètres : 3 à 5 tentatives maximales, attente de 100ms à 1000ms.

Emplacement : Implémenté comme un décorateur ou un middleware dans la couche Application (ou injecté via l'UoW), encapsulant l'exécution des Use Cases et des Handlers.

3. Idempotence de la Gamification
Modèle Métier : L'Aggregate Root StudentProfile doit devenir gardien de sa propre idempotence.

Value Object : Introduction d'un Value Object CompletedLabId.

Mécanisme : StudentProfile maintient une collection interne des CompletedLabId déjà évalués.

Méthode métier : L'appel à add_score_for_lab(lab_id, score) vérifie la présence du lab_id. S'il est présent, l'opération est ignorée (retour silencieux ou exception de domaine gérée).

4. Contrôle de la Cascade Événementielle
Règle de profondeur : La profondeur de cascade synchrone est strictement limitée à 1 rebond majeur (ex: Action Utilisateur -> Événement A -> Handler -> Événement B -> Handler -> FIN).

Responsabilité : L'EventBus intègre un compteur de profondeur dans le contexte d'exécution. Si la profondeur maximale est dépassée, une exception préventive est levée.

Événements interdits : Il est interdit pour un Handler du Gamification Context de publier un événement qui impacterait en retour le Learning Context.

5. Durcissement de l'EventBus
Métadonnées obligatoires : Tous les événements du domaine doivent désormais inclure un correlation_id (UUID unique par requête HTTP) et un timestamp immuable.

Isolation et Logging : Maintien du bloc try/except global dans l'EventBus, enrichi par la journalisation systématique du correlation_id et du type d'événement pour assurer la traçabilité offline.

6. Analyse de l'Outbox Pattern
Option A (Actuelle) : EventBus en mémoire post-commit.

Option B (Outbox) : Sauvegarde des événements dans une table SQLite, traités par un thread séparé.

Décision : Plus tard. L'Option A, combinée au mode WAL, au busy_timeout et au Retry, est suffisante pour 30 à 40 utilisateurs locaux et maintient une complexité technique faible (critique pour une distribution offline pédagogique). L'Option B introduit une complexité de gestion des processus (workers asynchrones) disproportionnée pour le moment.

PARTIE 4 — ADR nécessaires
La documentation sera enrichie des décisions suivantes :

ADR-015 SQLite Resilience Configuration : Choix du mode WAL et du busy_timeout pour gérer la concurrence d'une salle de classe.

ADR-016 Database Retry Policy : Implémentation d'un mécanisme de backoff exponentiel purement Python pour les erreurs database is locked.

ADR-017 Gamification Idempotency : Délégation à StudentProfile du filtrage des récompenses dupliquées (unicité par Lab).

ADR-018 Event Cascade Limitation : Fixation des règles de profondeur maximale pour l'EventBus synchrone afin d'éviter les boucles.

ADR-019 Outbox Future Enhancement : Documentation de l'abandon temporaire du pattern Outbox en faveur de la simplicité offline, conservé comme évolution future si la synchronisation cloud devient requise.

PARTIE 5 — Stratégie de tests
Pour garantir que ces mesures sont efficaces sans provoquer de régression, de nouveaux tests automatisés sont prescrits (passant le total attendu de 254 à environ 270+).

Tests Domaine :

Vérification que l'Aggregate Root StudentProfile refuse ou ignore l'ajout d'un score pour un LabId déjà validé.

Tests Infrastructure :

Validation au niveau du connecteur SQLAlchemy que les PRAGMA (WAL, busy_timeout) sont bien injectés à l'ouverture de la connexion.

Test unitaire du mécanisme de Retry simulant une exception sqlite3.OperationalError (mocking).

Tests EventBus :

Vérification qu'une chaîne d'événements dépassant la limite de cascade lève l'exception de protection.

Vérification de la transmission correcte du correlation_id entre les événements.

Tests Concurrence (Stress Test critique) :

Création d'un test utilisant concurrent.futures.ThreadPoolExecutor.

Simulation de 30 workers invoquant le Use Case de soumission simultanément sur une vraie base SQLite en mémoire/fichier.

Assertion attendue : Aucun plantage (ou retries transparents réussis), intégrité des 30 enregistrements.

PARTIE 6 — Impact sur architecture existante
Modifications de la configuration base de données : Impact circonscrit au module de création de l'Engine (Infrastructure). Aucun impact sur les Repositories.

Modifications de l'Application Layer : Les Use Cases actuels ne changent pas. L'ajout du décorateur/mécanisme de Retry sera transparent.

Modifications de l'EventBus : Ajout de la gestion du correlation_id et du compteur de profondeur de pile.

Modifications du Domaine : Enrichissement strict des événements de base (métadonnées) et de StudentProfile. Les entités du Learning Context restent globalement inchangées.

Documentation à mettre à jour :

docs/ARCHITECTURAL_DECISIONS.md

docs/EVENT_LIFECYCLE.md (pour inclure la traçabilité)

docs/EVENT_CATALOG.md (pour documenter les nouveaux champs)

docs/ROADMAP.md (pour ajouter l'Outbox Pattern en phase future)

PARTIE 7 — Plan d'implémentation futur
Phase E.1.2 : Implémentation TDD de l'idempotence dans le Domaine et de l'EventBus durci.

Phase E.1.3 : Implémentation TDD de l'Infrastructure SQLite (WAL, PRAGMA) et de la politique de Retry.

Phase E.1.4 : Écriture et validation du test de stress concurrentiel (30 utilisateurs).

Phase E.1.5 : Rédaction définitive des fichiers ADR et mise à jour de la documentation projet.

PARTIE 8 — Verdict Architecture
VERDICT ARCHITECTURAL : GO

Justification :
L'ensemble des vulnérabilités physiques identifiées lors de l'audit précédent trouve ici une réponse pragmatique, adaptée aux contraintes d'un environnement edge/offline et respectant l'absence de framework lourd.
La décision de reporter le pattern Outbox au profit d'une configuration SQLite optimisée (WAL + Retry) est un choix Enterprise parfaitement mesuré : on privilégie l'efficacité pédagogique immédiate et la simplicité de déploiement (clé USB/serveur local minimaliste) tout en érigeant des barrières logicielles robustes (idempotence domaine, limite de cascade) contre les effets de bord de l'architecture événementielle.

L'équipe d'ingénierie est formellement autorisée à ouvrir l'implémentation TDD de ce durcissement.