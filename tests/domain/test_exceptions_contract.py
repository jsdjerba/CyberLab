import pytest
import sys
import inspect

# 2. Vérification que l'import façade fonctionne (Backward compatibility)
from domain.exceptions import (
    BaseDomainException,
    UserAlreadyExists,
    ValidationError,
    LabLockedOutException
)
import domain.exceptions

def test_all_exceptions_inherit_from_base():
    """1. Test architectural : Toutes les exceptions doivent hériter de BaseDomainException."""
    # Récupère dynamiquement toutes les classes exposées par le package
    classes = [
        obj for name, obj in inspect.getmembers(domain.exceptions)
        if inspect.isclass(obj) and issubclass(obj, Exception)
    ]
    
    for exc_class in classes:
        assert issubclass(exc_class, BaseDomainException), \
            f"L'exception {exc_class.__name__} n'hérite pas de BaseDomainException."

def test_exceptions_accept_custom_messages():
    """3. Vérifie que les exceptions acceptent des messages personnalisés."""
    msg = "Le flag est incorrect."
    exc = ValidationError(msg)
    assert str(exc) == msg

def test_domain_exceptions_has_no_infrastructure_dependencies():
    """4. Anti-Corruption : Vérifie qu'aucune dépendance d'infra n'a fuité dans le module."""
    # On force le chargement du package
    import domain.exceptions
    
    # On inspecte les modules chargés par le package domain.exceptions.*
    forbidden_keywords = ['flask', 'sqlalchemy', 'requests', 'werkzeug', 'http']
    
    for module_name in sys.modules.keys():
        if module_name.startswith('domain.exceptions'):
            module = sys.modules[module_name]
            if module and hasattr(module, '__file__') and module.__file__:
                with open(module.__file__, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    for keyword in forbidden_keywords:
                        assert f"import {keyword}" not in content, \
                            f"Violation Clean Architecture: {keyword} importé dans {module_name}"
                        assert f"from {keyword}" not in content, \
                            f"Violation Clean Architecture: {keyword} importé dans {module_name}"