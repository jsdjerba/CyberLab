# CyberLab : Guide de Validation de la Couche de Persistance (Phase 2.3.3)

Ce document centralise toutes les étapes nécessaires pour valider la robustesse de l'architecture transactionnelle et des repositories avant le passage à la Phase 3 (Services).

## 1. Audit de Conformité
Avant d'exécuter les tests, vérifiez manuellement les points critiques :
- **Intégrité Transactionnelle** : Aucun `commit()` ou `rollback()` ne doit figurer dans les fichiers de `repositories/sqlalchemy/`.
- **Isolation** : Les fichiers dans `repositories/interfaces/` n'importent ni `sqlalchemy` ni `database.models`.
- **Unité de travail** : Toutes les opérations multi-domaines sont encapsulées dans un `with UnitOfWork(session):`.
- **Types UTC** : Tous les modèles utilisent `UTCDateTime()` pour les champs `DateTime`.

## 2. Procédure de Validation Automatisée

Exécutez la suite complète de tests via votre terminal à la racine du projet :

```bash
# Lancement de tous les tests de persistance
pytest tests/ -v


# CyberLab : Guide complet de validation et de lancement (Phase 2.3.3)

Ce document centralise toutes les étapes nécessaires pour configurer, auditer et valider la couche de persistance de CyberLab avant de démarrer la Phase 3 (Services).

## 1. Mise en place de l'environnement
Configurez votre environnement de travail local pour garantir la cohérence :

1. **Création de l'environnement virtuel** :
   ```bash
   python -m venv venv
   # Sous Windows :
   venv\Scripts\activate
   # Sous Linux/macOS :
   source venv/bin/activate

Vérification des dépendances :Installez les bibliothèques requises :Bashpip install -r requirements.txt
pip list  # Vérifiez la présence de sqlalchemy et pytest
Localisation des fichiers :Assurez-vous d'être à la racine du projet CyberLab/. Les répertoires clés sont :database/models/ : Entités SQLAlchemy.repositories/sqlalchemy/ : Implémentations concrètes.tests/ : Scripts de validation.2. Audit de ConformitéAvant de tester, vérifiez manuellement ces points critiques :Intégrité : Aucun commit() ou rollback() ne doit figurer dans repositories/sqlalchemy/.Isolation : Les interfaces (repositories/interfaces/) n'importent ni sqlalchemy ni database.models.3. Lancement des Tests de ValidationExécutez la suite complète pour valider la couche de persistance :Bash# Lancement de tous les tests
pytest tests/ -v
Détail des tests :TestObjectiftest_architecture.pyAudit statique : interdiction des commits/rollbacks et isolation des imports.test_transactions.pyValidation de l'atomicité (rollback automatique) et des savepoints.test_datetime.pyVérification de la normalisation UTC stricte.4. Structure Architecturale (Frozen)PlaintextCyberLab/
├── database/           # UoW, Types UTC, Modèles
├── repositories/       # Interfaces (Protocol) & Impl. SQLAlchemy
└── tests/              # Audit et validation transactionnelle
5. Vérification de l'Intégrité des IndexAssurez-vous que les index composés suivants sont bien présents dans votre base de données pour supporter les futurs dashboards :Enrollment : Index('idx_classroom_user', 'classroom_id', 'user_id')LabProgress : Index('idx_user_lab_progress', 'user_id', 'lab_id')