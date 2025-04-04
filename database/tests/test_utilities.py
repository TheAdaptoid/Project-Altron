from db_module.utilities import create_id


def test_create_id():
    id1 = create_id()
    id2 = create_id()
    assert id1 != id2
