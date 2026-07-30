from infrastructure.identity.uuid_id_generator import UuidIdGenerator

def test_uuid_generator_format_and_uniqueness():
    generator = UuidIdGenerator()
    id1 = generator.generate()
    id2 = generator.generate()
    
    assert id1.startswith("u-")
    assert len(id1) == 14 # "u-" (2) + hex[:12] (12)
    assert id1 != id2