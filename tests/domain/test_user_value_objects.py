import pytest
from domain.value_objects.user_id import UserId
from domain.value_objects.email import Email
from domain.value_objects.password_hash import PasswordHash
from domain.value_objects.role import Role

def test_user_id_valid():
    uid = UserId("user-123")
    assert uid.value == "user-123"

def test_user_id_invalid_empty():
    with pytest.raises(ValueError, match="UserId ne peut pas être vide"):
        UserId("   ")

def test_email_valid_and_normalized():
    email = Email("  John.Doe@CyberLab.EDU  ")
    assert email.value == "john.doe@cyberlab.edu"

def test_email_invalid_format():
    with pytest.raises(ValueError, match="Format d'email invalide"):
        Email("john.doe.cyberlab.edu")

def test_password_hash_valid():
    ph = PasswordHash("$2b$12$eImiTXuWVxfM37uY4JANj.K")
    assert ph.value == "$2b$12$eImiTXuWVxfM37uY4JANj.K"

def test_password_hash_invalid_empty():
    with pytest.raises(ValueError, match="Le hash du mot de passe ne peut pas être vide"):
        PasswordHash("   ")

def test_role_enum():
    assert Role.ADMIN.value == "ADMIN"
    assert Role.STUDENT.value == "STUDENT"