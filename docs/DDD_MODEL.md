# Modèle Domain-Driven Design (DDD) — CyberLab

Ce document formalise le modèle tactique et stratégique du domaine pour la plateforme CyberLab, dans le respect de la Clean Architecture et des principes DDD.

## 1. Bounded Contexts (Contextes Délimités)

Le système est découpé en trois Bounded Contexts principaux afin d'isoler les responsabilités métier :

1. **Learning Context (Contexte d'Apprentissage et d'Exécution) :**
   - *Responsabilité :* Gestion des laboratoires, de leur cycle de vie, de l'état d'avancement des étudiants et de la validation cryptographique ou logique des drapeaux (flags).
2. **Gamification Context (Contexte de Récompenses et de Scores) :**
   - *Responsabilité :* Suivi des points, calculs de scores, attribution des trophées et gestion des classements (Leaderboards).
3. **Supervision Context (Contexte de Suivi Pédagogique) :**
   - *Responsabilité :* Restitution de l'historique des étudiants, génération de rapports et tableaux de bord pour les enseignants.

---

## 2. Agrégats (Aggregates)

### Agrégat : LabInstance (Racine d'Agrégat)
* **Contexte :** Learning Context
* **Responsabilité :** Encapsuler l'état d'un laboratoire assigné ou en cours d'exécution pour un étudiant donné. Garantit les invariants liés au passage des états (ex: impossible de soumettre un flag sur un lab non démarré ou déjà terminé).
* **Entités internes et Value Objects :** 
  - `LabInstance` (Entité Racine)
  - `LabId` (Value Object)
  - `StudentId` (Value Object)
  - `LabStatus` (Value Object : `NOT_STARTED`, `IN_PROGRESS`, `COMPLETED`, `FAILED`)

### Agrégat : StudentProfile (Racine d'Agrégat)
* **Contexte :** Gamification Context
* **Responsabilité :** Centraliser les données de progression globale de l'apprenant (score cumulé, liste des achievements débloqués).

---

## 3. Entités (Entities)
* **`LabInstance` :** Possède une identité unique liée à la combinaison d'un étudiant et d'un laboratoire. Son cycle de vie est mutable au sein de ses règles métiers.
* **`Student` :** Représentant l'utilisateur de type apprenant au sein de l'établissement.

---

## 4. Value Objects (Objets de Valeur)
* **`LabId` :** Identifiant fort et immuable d'un laboratoire (ex: format slug ou UUID).
* **`StudentId` :** Identifiant fort et immuable d'un étudiant.
* **`LabStatus` :** Énumération stricte encapsulant les transitions d'état valides d'un lab.
* **`Flag` :** Représentation de la chaîne soumise par l'étudiant, encapsulant les règles de formatage et de masquage (sécurité des logs).

---

## 5. Domain Services (Services Domaine)
* **`FlagValidationService` :** Service métier pur chargé de comparer le flag soumis par l'étudiant au hachage cryptographique de référence du laboratoire, sans dépendre d'aucune base de données ni d'infrastructure web.
* **`ScoringService` :** Service de calcul des points attribués en fonction de la complexité du lab et du temps d'exécution.

---

## 6. Repositories (Ports du Domaine)
Les repositories définissent les contrats d'accès aux données dont le domaine a besoin pour reconstituer les agrégats :
* **`LabRepository`**
* **`StudentRepository`**
* **`LabInstanceRepository`**

---

## 7. Ports (Interfaces Entrant / Sortant)
* **Ports Entrants (Primary/Driving Ports) :** Représentés par les interfaces des *Use Cases* (`StartLabUseCase`, `SubmitFlagUseCase`, etc.).
* **Ports Sortants (Secondary/Driven Ports) :** Représentés par les interfaces de persistance (*Repositories*) et de communication asynchrone (*EventBus*).

---

## 8. Use Cases (Cas d'Application)
* **`StartLabUseCase` :** Initialise ou reprend une instance de laboratoire pour un étudiant.
* **`SubmitFlagUseCase` :** Soumet et valide un flag, met à jour le statut du lab et déclenche les événements associés.
* **`ResumeLabUseCase` :** Restaure l'état d'un laboratoire en cours.
* **`CompleteLabUseCase` :** Finalise formellement un laboratoire.
* **`GetStudentHistoryUseCase` :** Agrège l'historique des activités d'un apprenant.