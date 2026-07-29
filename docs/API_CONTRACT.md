# Contrats d'API REST (DTOs, Codes HTTP et Erreurs) — CyberLab

Ce document définit les contrats d'interface entre les clients frontends et les API Flask de la plateforme CyberLab.

## 1. Principes Généraux
* **Format d'échange :** JSON strict pour toutes les requêtes et réponses.
* **Versioning :** Intégré dans le préfixe de l'URL (`/api/v1/...`).
* **Authentification :** En-tête `Authorization: Bearer <token>` requis pour les routes protégées.

---

## 2. Contrats par Cas d'Usage

### A. Start Lab (`POST /api/v1/labs/<lab_id>/start`)
* **Request DTO :** Vide (les informations de l'étudiant sont extraites du contexte du token d'authentification).
* **Response DTO (201 Created) :**
  ```json
  {
    "lab_id": "string",
    "status": "IN_PROGRESS",
    "started_at": "ISO-8601 string"
  }