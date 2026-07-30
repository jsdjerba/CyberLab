from domain.entities.user import User
from domain.value_objects.user_id import UserId
from domain.value_objects.email import Email
from domain.value_objects.password_hash import PasswordHash
from domain.value_objects.role import Role
from infrastructure.persistence.models.user_model import UserModel
from infrastructure.persistence.mappers.user_mapper import UserMapper

def test_user_mapper_bidirectional():
    # 1. Domain to Model
    domain_user = User(
        UserId("u-map"), Email("map@test.com"), PasswordHash("hash123"), Role.TEACHER, True
    )
    model = UserMapper.to_model(domain_user)
    
    assert model.id == "u-map"
    assert model.email == "map@test.com"
    
    # 2. Model to Domain
    mapped_back = UserMapper.to_domain(model)
    assert mapped_back.user_id.value == "u-map"
    assert mapped_back.role == Role.TEACHER