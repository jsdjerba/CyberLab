# Guide de Test : Couche de Persistance CyberLab (Phase 2.3.3)

Ce guide décrit la procédure de test étape par étape pour valider la couche de persistance (Repositories, Unit of Work, Modèles).

## Prérequis
- Python 3.11+
- `pytest` et `sqlalchemy` installés.
- Environnement virtuel activé.

---

## Étape 1 : Audit de l'Architecture
Vérifie que les règles de Clean Architecture sont respectées (pas de `commit` dans les repos, pas de dépendances interdites).
```bash
pytest tests/test_architecture.py -v