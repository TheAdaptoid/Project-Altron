from datetime import datetime

import pytest

from db_module.models import Role, Message

TEST_ATTACHMENT_PATH: str = "database/attachments/Test_Attachment.txt"


class TestRole:
    def test_valid(self):
        assert Role.USER == "user"
        assert Role.ASSISTANT == "assistant"
        assert Role.SYSTEM == "system"


class TestMessage:
    def test_valid_role_and_content(self):
        message = Message(role=Role.USER, content="Hello")

        assert message.role == Role.USER
        assert message.__content == "Hello"
        assert message.created_at <= datetime.now()
        assert message.updated_at <= datetime.now()
        assert message.created_at <= message.updated_at

        assert isinstance(message.role, str)
        assert isinstance(message.__content, str)
        assert isinstance(message.created_at, datetime)
        assert isinstance(message.updated_at, datetime)
        assert isinstance(message.id, int)

    def test_invalid_role(self):
        with pytest.raises(ValueError):
            Message(role="invalid", content="Hello")

        with pytest.raises(TypeError):
            Message(role=1, content="Hello")

        with pytest.raises(TypeError):
            Message(role=None, content="Hello")

    def test_invalid_content(self):
        with pytest.raises(TypeError):
            Message(role=Role.USER, content=1)

        with pytest.raises(TypeError):
            Message(role=Role.USER, content=None)

        with pytest.raises(ValueError):
            Message(role=Role.USER, content="")

        with pytest.raises(ValueError):
            Message(role=Role.USER, content=" " * 1001)

    def test_invalid_id(self):
        with pytest.raises(TypeError):
            Message(role=Role.USER, content="Hello", id=None)

        with pytest.raises(TypeError):
            Message(role=Role.USER, content="Hello", id=1.0)

        with pytest.raises(TypeError):
            Message(role=Role.USER, content="Hello", id="1")

    def test_invalid_created_at(self):
        with pytest.raises(TypeError):
            Message(role=Role.USER, content="Hello", created_at=None)

        with pytest.raises(TypeError):
            Message(role=Role.USER, content="Hello", created_at=1.0)

        with pytest.raises(TypeError):
            Message(role=Role.USER, content="Hello", created_at="1")

    def test_invalid_updated_at(self):
        with pytest.raises(TypeError):
            Message(role=Role.USER, content="Hello", updated_at=None)

        with pytest.raises(TypeError):
            Message(role=Role.USER, content="Hello", updated_at=1.0)

        with pytest.raises(TypeError):
            Message(role=Role.USER, content="Hello", updated_at="1")

    def test_to_dict(self):
        message = Message(role=Role.USER, content="Hello")
        assert message.to_dict() == {
            "id": message.id,
            "created_at": message.created_at,
            "updated_at": message.updated_at,
            "role": message.role,
            "content": message.__content,
        }

        message = Message(
            role=Role.ASSISTANT,
            content="Hello",
            id=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert message.to_dict() == {
            "id": message.id,
            "created_at": message.created_at,
            "updated_at": message.updated_at,
            "role": message.role,
            "content": message.__content,
        }

    def test_from_dict(self):
        data = {
            "id": 1,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "role": Role.USER,
            "content": "Hello",
        }
        message = Message.from_dict(data)
        assert message.id == data["id"]
        assert message.created_at == data["created_at"]
        assert message.updated_at == data["updated_at"]
        assert message.role == data["role"]
        assert message.__content == data["content"]
