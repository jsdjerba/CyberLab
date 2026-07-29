# Roadmap Officielle de Développement — CyberLab

Cette feuille de route définit les jalons séquentiels pour l'évolution de la plateforme CyberLab à compter de la clôture de la Phase C.3.

---

## Phase D — Fondations Métier Transverses
* **Objectifs :** Mettre en place l'infrastructure transactionnelle et événementielle du système.
* **Livrables :** Implémentation de l'Unit of Work, du système de Domain Events, de l'EventBus synchrone et du gestionnaire de mapping d'erreurs HTTP.
* **Critères de validation :** Tests unitaires UoW et EventBus au vert, passage réussi de la suite de tests globale.
* **Risques :** Gestion des exceptions durant la publication des événements.
* **Pré-requis :** Fin de la Phase C.3 (Validé — 244 tests).
* **Tests attendus :** Tests d'intégrité transactionnelle UoW.
* **Estimation :** 1 SEMAINE.

---

## Phase E — Flux Métier Verticaux (Core Use Cases)
* **Objectifs :** Implémenter et brancher de bout en bout les cas d'usage fondamentaux.
* **Livrables :** `StartLabUseCase`, `SubmitFlagUseCase`, `ResumeLabUseCase`, `CompleteLabUseCase` pleinement fonctionnels et exposés via les Blueprints Flask.
* **Critères de validation :** Couverture complète par des tests unitaires, d'intégration et E2E Flask.
* **Risques :** Effets de bord sur les sessions SQLite concurrentes.
* **Pré-requis :** Phase D validée.
* **Tests attendus :** Tests E2E HTTP sur les routes de lab.
* **Estimation :** 2 SEMAINES.

---

## Phase F — Gamification et Historique
* **Objectifs :** Introduire la logique de récompense et de suivi analytique.
* **Livrables :** `Score Engine`, `Achievement Engine`, `StudentHistory` et calcul du `Leaderboard`.
* **Critères de validation :** Écoute correcte des Domain Events par les moteurs de gamification.
* **Risques :** Couplage excessif si les events ne sont pas bien isolés.
* **Pré-requis :** Phase E validée.
* **Tests attendus :** Tests de validation des scores et des achievements.
* **Estimation :** 1.5 SEMAINE.

---

## Phase G — API REST et Dashboards
* **Objectifs :** Finaliser les interfaces d'administration et d'apprentissage.
* **Livrables :** DTOs stabilisés, Dashboard Étudiant, Dashboard Enseignant.
* **Critères de validation :** Conformité des réponses JSON aux contrats d'API.
* **Risques :** Volumétrie de données sur les graphiques de supervision.
* **Pré-requis :** Phase F validée.
* **Tests attendus :** Tests de non-régression des contrats d'API.
* **Estimation :** 2 SEMAINES.

---

## Phase H — Contenu Pédagogique (Cyber Labs)
* **Objectifs :** Déployer les premiers modules pratiques standardisés.
* **Livrables :** Spécification `manifest.json` pleinement opérationnelle et création des premiers labs (HTTP, Linux, Nmap, etc.).
* **Critères de validation :** Chargement et exécution réussie des labs par le moteur offline.
* **Risques :** Bogues dans les scripts de validation des flags.
* **Pré-requis :** Phase G validée.
* **Tests attendus :** Tests de validation de contenu (Labs d'acceptation).
* **Estimation :** 2 SEMAINES.