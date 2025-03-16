from json import dumps

import pytest
from fastapi.testclient import TestClient
from fastapi.exceptions import RequestValidationError, HTTPException
from sqlalchemy.orm import Session

from app.main import app
from app.database import get_db
from app.models import MessageRead


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db():
    return get_db


def Create_Convo(client: TestClient, db: Session):
    response = client.post("/conversations/", json={})
    return int(response.json()["id"])


def Delete_Convo(client: TestClient, db: Session, convo_id: int):
    client.delete(f"/conversations/{convo_id}")


def Create_Message(client: TestClient, db: Session, convo_id: int):
    response = client.post(
        "/messages/",
        json={"conversation_id": convo_id, "role": "user", "text": "Test Message"},
    )
    return int(response.json()["id"])


def Delete_Message(client: TestClient, db: Session, message_id: int):
    client.delete(f"/messages/{message_id}")


class TestCreate:
    def test_valid_with_no_text(self, client: TestClient, db: Session) -> None:
        convo_id: int = Create_Convo(client, db)

        response = client.post(
            "/messages/", json={"conversation_id": convo_id, "role": "user"}
        )
        assert response.status_code == 200
        assert isinstance(
            MessageRead.model_validate_json(dumps(response.json())),
            MessageRead,
        )

        Delete_Convo(client, db, convo_id)

    def test_valid_with_text(self, client: TestClient, db: Session) -> None:
        convo_id: int = Create_Convo(client, db)

        response = client.post(
            "/messages/",
            json={"conversation_id": convo_id, "role": "user", "text": "Test Message"},
        )
        assert response.status_code == 200
        assert response.json()["text"] == "Test Message"
        assert isinstance(
            MessageRead.model_validate_json(dumps(response.json())),
            MessageRead,
        )

        Delete_Convo(client, db, convo_id)

    def test_invalid_with_no_role(self, client: TestClient, db: Session) -> None:
        convo_id: int = Create_Convo(client, db)

        response = client.post("/messages/", json={"conversation_id": convo_id})
        assert response.status_code == 422

        Delete_Convo(client, db, convo_id)

    def test_valid_with_role(self, client: TestClient, db: Session) -> None:
        convo_id: int = Create_Convo(client, db)

        response = client.post(
            "/messages/",
            json={
                "conversation_id": convo_id,
                "text": "Test Message",
                "role": "system",
            },
        )
        assert response.status_code == 200
        assert response.json()["role"] == "system"
        assert isinstance(
            MessageRead.model_validate_json(dumps(response.json())),
            MessageRead,
        )

        response = client.post(
            "/messages/",
            json={
                "conversation_id": convo_id,
                "text": "Test Message",
                "role": "assistant",
            },
        )
        assert response.status_code == 200
        assert response.json()["role"] == "assistant"
        assert isinstance(
            MessageRead.model_validate_json(dumps(response.json())),
            MessageRead,
        )

        response = client.post(
            "/messages/",
            json={
                "conversation_id": convo_id,
                "text": "Test Message",
                "role": "user",
            },
        )
        assert response.status_code == 200
        assert response.json()["role"] == "user"
        assert isinstance(
            MessageRead.model_validate_json(dumps(response.json())),
            MessageRead,
        )

        Delete_Convo(client, db, convo_id)

    def test_invalid_with_wrong_role(self, client: TestClient, db: Session) -> None:
        convo_id: int = Create_Convo(client, db)

        response = client.post(
            "/messages/",
            json={
                "conversation_id": convo_id,
                "text": "Test Message",
                "role": "invalid",
            },
        )
        assert response.status_code == 422

        Delete_Convo(client, db, convo_id)

    def test_invalid_with_wrong_convo_id(self, client: TestClient, db: Session) -> None:
        response = client.post(
            "/messages/",
            json={"conversation_id": -1, "text": "Test Message", "role": "system"},
        )
        assert response.status_code == 404

    def test_invalid_with_wrong_type(self, client: TestClient, db: Session) -> None:
        convo_id: int = Create_Convo(client, db)

        response = client.post(
            "/messages/",
            json={"conversation_id": convo_id, "text": "Test Message", "role": 1},
        )
        assert response.status_code == 422

        response = client.post(
            "/messages/",
            json={"conversation_id": convo_id, "text": 1, "role": "user"},
        )
        assert response.status_code == 422

        Delete_Convo(client, db, convo_id)


class TestReads:
    def test_valid_no_params(self, client: TestClient, db: Session) -> None:
        convo_id: int = Create_Convo(client, db)
        [Create_Message(client, db, convo_id) for _ in range(2)]

        response = client.get(f"/messages/?conversation_id={convo_id}")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == 2

        Delete_Convo(client, db, convo_id)

    def test_valid_with_params(self, client: TestClient, db: Session) -> None:
        convo_id: int = Create_Convo(client, db)
        [Create_Message(client, db, convo_id) for _ in range(2)]

        response = client.get(f"/messages/?conversation_id={convo_id}&limit=1")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == 1

        Delete_Convo(client, db, convo_id)

    def test_invalid_with_wrong_convo_id(self, client: TestClient, db: Session) -> None:
        response = client.get("/messages/?conversation_id=-1")
        assert response.status_code == 404

    def test_invalid_with_wrong_params(self, client: TestClient, db: Session) -> None:
        response = client.get("/messages/?conversation_id=-1&limit=2&skip=-1")
        assert response.status_code == 400


class TestRead:
    def test_valid(self, client: TestClient, db: Session) -> None:
        convo_id: int = Create_Convo(client, db)
        message_id: int = Create_Message(client, db, convo_id)

        response = client.get(f"/messages/{message_id}")
        assert response.status_code == 200
        assert isinstance(
            MessageRead.model_validate_json(dumps(response.json())),
            MessageRead,
        )
        assert response.json()["id"] == message_id

        Delete_Convo(client, db, convo_id)

    def test_invalid(self, client: TestClient, db: Session) -> None:
        response = client.get(f"/messages/{-1}")
        assert response.status_code == 404


class TestUpdate:
    def test_valid(self, client: TestClient, db: Session) -> None:
        convo_id: int = Create_Convo(client, db)
        message_id: int = Create_Message(client, db, convo_id)

        response = client.patch(
            f"/messages/{message_id}", json={"text": "Updated Message"}
        )
        assert response.status_code == 200
        assert response.json()["text"] == "Updated Message"
        assert isinstance(
            MessageRead.model_validate_json(dumps(response.json())),
            MessageRead,
        )

        Delete_Convo(client, db, convo_id)

    def test_invalid_with_wrong_id(self, client: TestClient, db: Session) -> None:
        response = client.patch(f"/messages/{-1}", json={"text": "Updated Message"})
        assert response.status_code == 404

    def test_invalid_with_wrong_params(self, client: TestClient, db: Session) -> None:
        convo_id: int = Create_Convo(client, db)
        message_id: int = Create_Message(client, db, convo_id)

        response = client.patch(
            f"/messages/{message_id}", json={"invalid": "Updated Message"}
        )
        assert response.status_code == 400

        Delete_Convo(client, db, convo_id)

    def test_invalid_with_no_params(self, client: TestClient, db: Session) -> None:
        convo_id: int = Create_Convo(client, db)
        message_id: int = Create_Message(client, db, convo_id)

        response = client.patch(f"/messages/{message_id}", json={})
        assert response.status_code == 400

        Delete_Convo(client, db, convo_id)


class TestDelete:
    def test_valid_del_convo(self, client: TestClient, db: Session) -> None:
        convo_id: int = Create_Convo(client, db)
        message_id: int = Create_Message(client, db, convo_id)

        Delete_Convo(client, db, convo_id)

        response = client.get(f"/messages/{message_id}")
        assert response.status_code == 404

    def test_valid_del_message(self, client: TestClient, db: Session) -> None:
        convo_id: int = Create_Convo(client, db)
        message_id: int = Create_Message(client, db, convo_id)

        response = client.delete(f"/messages/{message_id}")
        assert response.status_code == 200

        Delete_Convo(client, db, convo_id)

    def test_valid_del_multiple_messages(self, client: TestClient, db: Session) -> None:
        convo_id: int = Create_Convo(client, db)
        message_ids: list[int] = [
            Create_Message(client, db, convo_id) for _ in range(2)
        ]

        Delete_Convo(client, db, convo_id)

        for message_id in message_ids:
            response = client.get(f"/messages/{message_id}")
            assert response.status_code == 404

    def test_valid_del_single_message(self, client: TestClient, db: Session) -> None:
        convo_id: int = Create_Convo(client, db)
        message_ids: list[int] = [
            Create_Message(client, db, convo_id) for _ in range(2)
        ]

        response = client.delete(f"/messages/{message_ids[0]}")
        assert response.status_code == 200

        response = client.get(f"/messages/{message_ids[1]}")
        assert response.status_code == 200

        Delete_Convo(client, db, convo_id)

    def test_invalid(self, client: TestClient, db: Session) -> None:
        response = client.delete(f"/messages/{-1}")
        assert response.status_code == 404
