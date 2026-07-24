import pytest
from flask import Flask, request, jsonify
from api.middleware.request_validation import validate_schema, require_schema
from domain.exceptions import ValidationError

# --- Tests de la Fonction Pure ---

def test_payload_valide():
    # A) Payload valide
    schema = {"username": str, "password": str}
    payload = {"username": "student", "password": "123456"}
    
    result = validate_schema(payload, schema)
    assert result == payload

def test_champ_manquant():
    # B) Champ manquant
    schema = {"username": str, "password": str}
    payload = {"username": "student"}
    
    with pytest.raises(ValidationError) as exc:
        validate_schema(payload, schema)
    assert "Missing required field: 'password'" in str(exc.value)

def test_mauvais_type():
    # C) Mauvais type
    schema = {"username": str, "age": int}
    payload = {"username": "student", "age": "20"} # str au lieu de int
    
    with pytest.raises(ValidationError) as exc:
        validate_schema(payload, schema)
    assert "Invalid type for field 'age'. Expected int" in str(exc.value)

def test_champ_supplementaire_strict():
    # D) Champ supplémentaire (Mode Strict)
    schema = {"username": str, "password": str}
    payload = {"username": "student", "password": "123", "role": "admin"}
    
    with pytest.raises(ValidationError) as exc:
        validate_schema(payload, schema, strict=True)
    assert "Unexpected field: 'role'" in str(exc.value)

def test_champ_supplementaire_permissif():
    # E) Mode permissif
    schema = {"username": str, "password": str}
    payload = {"username": "student", "password": "123", "role": "admin"}
    
    # Ne lève pas d'exception
    result = validate_schema(payload, schema, strict=False)
    
    # Le dictionnaire retourné doit quand même être nettoyé (F)
    assert "role" not in result
    assert result == {"username": "student", "password": "123"}

def test_securite_retour_nettoye():
    # F) Test de sécurité : le dict retourné ne contient JAMAIS de clé hors schéma
    schema = {"id": int}
    payload = {"id": 1, "is_admin": True, "xp": 9000}
    
    result = validate_schema(payload, schema, strict=False)
    assert list(result.keys()) == ["id"]


# --- Tests d'Intégration Flask ---

@pytest.fixture
def app():
    flask_app = Flask(__name__)
    
    # Indispensable pour que Flask ne transforme pas l'exception en HTTP 500
    # Cela permet à pytest.raises de la capturer.
    flask_app.testing = True
    
    @flask_app.route("/register", methods=["POST"])
    @require_schema({"username": str, "password": str}, strict=True)
    def register():
        # Utilisation des données sécurisées validées
        data = request.validated_data
        return jsonify({"saved_user": data["username"]})
        
    return flask_app

def test_flask_decorator_integration(app):
    client = app.test_client()
    
    # Valide
    res = client.post("/register", json={"username": "bob", "password": "pwd"})
    assert res.status_code == 200
    
    # Injection refusée (ValidationError interceptée par pytest)
    with pytest.raises(ValidationError) as exc:
        client.post("/register", json={"username": "bob", "password": "pwd", "role": "admin"})
    assert "Unexpected field: 'role'" in str(exc.value)