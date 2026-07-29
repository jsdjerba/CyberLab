# Catalogue des Événements Domaine (Domain Events) — CyberLab

Ce document répertorie l'ensemble des événements du domaine émis par les agrégats de la plateforme CyberLab.

## 1. Liste des Domain Events

### 1. `LabStarted`
* **Description :** Émis lorsqu'un étudiant initialise avec succès un nouveau laboratoire.
* **Émetteur :** Agrégat `LabInstance`
* **Données transportées :** `student_id`, `lab_id`, `timestamp`
* **Moment d'émission :** Juste avant la validation de la transaction de création de l'instance.
* **Consommateurs :** Dashboard enseignant (compteur d'activité), service de télémétrie locale.
* **Invariants :** Le lab doit être dans un état valide et non déjà actif.

### 2. `FlagSubmitted`
* **Description :** Émis lorsqu'un étudiant soumet une tentative de drapeau.
* **Émetteur :** Use Case / Service de validation
* **Données transportées :** `student_id`, `lab_id`, `is_correct`, `timestamp`
* **Moment d'émission :** Immédiatement après l'évaluation de la soumission.
* **Consommateurs :** Système d'audit, moteur de score (en cas de succès).
* **Invariants :** La soumission doit correspondre à une instance de lab active.

### 3. `FlagValidated`
* **Description :** Émis spécifiquement lorsqu'un flag correct est validé pour la première fois.
* **Émetteur :** Agrégat `LabInstance`
* **Données transportées :** `student_id`, `lab_id`, `timestamp`
* **Moment d'émission :** Lors du passage du statut à validé.
* **Consommateurs :** Score Engine, Achievement Engine.
* **Invariants :** Ne peut être émis qu'une seule fois par instance de laboratoire réussie.

### 4. `LabCompleted`
* **Description :** Émis lorsque toutes les étapes d'un laboratoire sont achevées.
* **Émetteur :** Agrégat `LabInstance`
* **Données transportées :** `student_id`, `lab_id`, `completion_time`, `timestamp`
* **Moment d'émission :** Lors de la clôture de l'instance.
* **Consommateurs :** Gamification Context, Historique Étudiant.
* **Invariants :** Toutes les conditions de validation du lab doivent être remplies.

### 5. `ScoreUpdated`
* **Description :** Émis lorsque le score global d'un étudiant est incrémenté.
* **Émetteur :** Score Engine
* **Données transportées :** `student_id`, `added_points`, `new_total_score`, `timestamp`
* **Moment d'émission :** Suite à un événement de réussite (ex: `LabCompleted`).
* **Consommateurs :** Leaderboard, Profil étudiant.
* **Invariants :** Le score ne peut pas être négatif.

### 6. `AchievementUnlocked`
* **Description :** Émis lorsqu'un badge ou un trophée est débloqué par l'apprenant.
* **Émetteur :** Achievement Engine
* **Données transportées :** `student_id`, `achievement_id`, `timestamp`
* **Moment d'émission :** Après vérification des critères de l'achievement.
* **Consommateurs :** Notification UI, Historique étudiant.

---

## 2. Classification des Événements

* **Événements Synchrones (Transactionnels) :** Tous les événements ci-dessus sont gérés via un bus synchrone en mémoire exécuté dans la même limite transactionnelle (Unit of Work) pour garantir la cohérence des données dans l'environnement offline.
* **Événements Futurs (Roadmap externe) :** Événements inter-domaines distribués via broker externe (ex: MQTT/RabbitMQ pour des salles connectées en réseau étendu — *Hors périmètre actuel YAGNI*).
* **Événements Techniques à Éviter :** Les événements de bas niveau liés à la base de données (ex: `SQLAlchemy INSERT executed`, `HTTP Request Received`) ne doivent jamais être traités comme des Domain Events. Le domaine s'intéresse exclusivement aux faits métiers.