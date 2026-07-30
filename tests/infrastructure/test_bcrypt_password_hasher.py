from infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher

def test_bcrypt_hash_and_verify():
    hasher = BcryptPasswordHasher()
    password = "SuperSecretPassword123!"
    
    pw_hash = hasher.hash(password)
    assert pw_hash.value.startswith("$2b$") # Signature Bcrypt
    
    assert hasher.verify(password, pw_hash) is True
    assert hasher.verify("WrongPassword", pw_hash) is False