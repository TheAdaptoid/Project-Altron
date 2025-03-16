from json import dumps

import pytest
from fastapi.testclient import TestClient
from fastapi.exceptions import RequestValidationError, HTTPException
from sqlalchemy.orm import Session

from app.routers.conversations import router
from app.database import get_db
from app.models import ConversationRead


@pytest.fixture
def client():
    with TestClient(router) as test_client:
        yield test_client


@pytest.fixture
def db():
    return get_db


followed_convo_ids: list[int] = []


class TestCreate:
    def test_valid_with_title(self, client: TestClient, db: Session) -> None:
        response = client.post("/conversations/", json={"title": "Test Conversation"})
        assert response.status_code == 200
        assert isinstance(
            ConversationRead.model_validate_json(dumps(response.json())),
            ConversationRead,
        )
        followed_convo_ids.append(int(response.json()["id"]))

    def test_valid_without_title(self, client: TestClient, db: Session) -> None:
        response = client.post("/conversations/", json={})
        assert response.status_code == 200
        assert response.json()["title"] == "New Conversation"
        assert isinstance(
            ConversationRead.model_validate_json(dumps(response.json())),
            ConversationRead,
        )
        followed_convo_ids.append(int(response.json()["id"]))

    def test_invalid_with_wrong_type(self, client: TestClient, db: Session) -> None:
        with pytest.raises(RequestValidationError) as e:
            response = client.post("/conversations/", json={"title": 1})


class TestReads:
    def test_valid_no_params(self, client: TestClient, db: Session) -> None:
        response = client.get("/conversations/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        # Check sorting of conversations

    def test_valid_with_params(self, client: TestClient, db: Session) -> None:
        response = client.get("/conversations/?limit=2&skip=0")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == 2

    def test_invalid_with_wrong_params(self, client: TestClient, db: Session) -> None:
        with pytest.raises(HTTPException) as e:
            response = client.get("/conversations/?limit=2&skip=-1")
        assert e.value.status_code == 400


class TestRead:
    def test_valid(self, client: TestClient, db: Session) -> None:
        response = client.get(f"/conversations/{followed_convo_ids[0]}")
        assert response.status_code == 200
        assert isinstance(
            ConversationRead.model_validate_json(dumps(response.json())),
            ConversationRead,
        )
        assert response.json()["id"] == followed_convo_ids[0]

    def test_invalid(self, client: TestClient, db: Session) -> None:
        with pytest.raises(HTTPException) as e:
            response = client.get(f"/conversations/{-1}")
        assert e.value.status_code == 404


class TestUpdate:
    def test_valid(self, client: TestClient, db: Session) -> None:
        response = client.patch(
            f"/conversations/{followed_convo_ids[0]}", json={"title": "Updated Title"}
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"
        assert isinstance(
            ConversationRead.model_validate_json(dumps(response.json())),
            ConversationRead,
        )

    def test_invalid_with_wrong_type(self, client: TestClient, db: Session) -> None:
        with pytest.raises(RequestValidationError) as e:
            response = client.patch(
                f"/conversations/{followed_convo_ids[0]}", json={"title": 1}
            )

    def test_invalid_with_non_existing(self, client: TestClient, db: Session) -> None:
        with pytest.raises(HTTPException) as e:
            response = client.patch(
                f"/conversations/{-1}", json={"title": "Updated Title"}
            )
        assert e.value.status_code == 404


class TestDelete:
    def test_valid(self, client: TestClient, db: Session) -> None:
        response = client.delete(f"/conversations/{followed_convo_ids[0]}")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    def test_invalid_with_non_existing(self, client: TestClient, db: Session) -> None:
        with pytest.raises(HTTPException) as e:
            response = client.delete(f"/conversations/{-1}")
        assert e.value.status_code == 404
