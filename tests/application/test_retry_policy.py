import pytest
import sqlite3
from unittest.mock import patch
from application.common.retry_policy import retry_on_db_locked

def test_retry_policy_success_immediate():
    """Vérifie que le décorateur n'altère pas une fonction qui réussit immédiatement."""
    @retry_on_db_locked(max_attempts=3)
    def successful_operation():
        return "Success"
        
    assert successful_operation() == "Success"

@patch("time.sleep")  # Mock du sleep pour garder la suite de tests ultra-rapide
def test_retry_policy_succeeds_after_retries(mock_sleep):
    """Vérifie le succès après plusieurs échecs 'database is locked'."""
    attempts = 0
    
    @retry_on_db_locked(max_attempts=3)
    def flaky_operation():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise sqlite3.OperationalError("database is locked")
        return "Final Success"
        
    result = flaky_operation()
    
    assert result == "Final Success"
    assert attempts == 3
    assert mock_sleep.call_count == 2  # Le système a patienté 2 fois

@patch("time.sleep")
def test_retry_policy_fails_after_max_attempts(mock_sleep):
    """Vérifie que l'exception remonte si le nombre maximum de tentatives est atteint."""
    attempts = 0
    
    @retry_on_db_locked(max_attempts=3)
    def always_failing_operation():
        nonlocal attempts
        attempts += 1
        raise sqlite3.OperationalError("database is locked")
        
    with pytest.raises(sqlite3.OperationalError, match="database is locked"):
        always_failing_operation()
        
    assert attempts == 3
    assert mock_sleep.call_count == 2

def test_retry_policy_does_not_retry_on_other_exceptions():
    """Vérifie que les autres exceptions (ex: ValueError métier) ne sont pas interceptées."""
    @retry_on_db_locked(max_attempts=3)
    def value_error_operation():
        raise ValueError("Invalid Domain State")
        
    with pytest.raises(ValueError, match="Invalid Domain State"):
        value_error_operation()

def test_retry_policy_does_not_retry_on_other_operational_errors():
    """Vérifie que les autres erreurs SQLite (ex: syntaxe, table manquante) ne sont pas interceptées."""
    @retry_on_db_locked(max_attempts=3)
    def other_db_error_operation():
        raise sqlite3.OperationalError("no such table: students")
        
    with pytest.raises(sqlite3.OperationalError, match="no such table"):
        other_db_error_operation()

def test_retry_policy_preserves_function_metadata():
    """Vérifie que functools.wraps conserve le nom et la docstring."""
    @retry_on_db_locked()
    def my_custom_func():
        """This is my custom function."""
        pass

    assert my_custom_func.__name__ == "my_custom_func"
    assert my_custom_func.__doc__ == "This is my custom function."

@patch("time.sleep")
def test_retry_policy_respects_custom_attempts(mock_sleep):
    """Vérifie que le paramètre max_attempts est bien respecté."""
    attempts = 0

    @retry_on_db_locked(max_attempts=5)
    def failing_func():
        nonlocal attempts
        attempts += 1
        raise sqlite3.OperationalError("database is locked")

    with pytest.raises(sqlite3.OperationalError):
        failing_func()

    assert attempts == 5
    assert mock_sleep.call_count == 4