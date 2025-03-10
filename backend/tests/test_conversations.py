import pytest
from fastapi.testclient import TestClient
from fastapi.exceptions import RequestValidationError, HTTPException
from sqlalchemy.orm import Session

from app.routers.conversations import router
from app.database import get_db


@pytest.fixture
def client():
    with TestClient(router) as test_client:
        yield test_client


@pytest.fixture
def db():
    return get_db


class TestConversations:
    convo_ids: list[int] = []

    def test_create_with_wrong_type(self, client: TestClient, db: Session) -> None:
        with pytest.raises(RequestValidationError) as e:
            response = client.post("/conversations/", json={"title": 1})

    def test_create_without_title(self, client: TestClient, db: Session) -> None:
        response = client.post("/conversations/", json={})
        assert response.status_code == 200
        assert response.json()["title"] == "New Conversation"
        TestConversations.convo_ids.append(int(response.json()["id"]))

    def test_create(self, client: TestClient, db: Session) -> None:
        response = client.post("/conversations/", json={"title": "Test Conversation"})
        assert response.status_code == 200
        assert response.json()["title"] == "Test Conversation"
        TestConversations.convo_ids.append(int(response.json()["id"]))

    def test_reads(self, client: TestClient, db: Session) -> None:
        response = client.get("/conversations/")
        assert response.status_code == 200
        assert (
            len(response.json()) >= 2
        )  # There is at least one conversation object stuck in the database

    def test_read_existing(self, client: TestClient, db: Session) -> None:
        for convo_id in TestConversations.convo_ids:
            response = client.get(f"/conversations/{convo_id}")
            assert response.status_code == 200

    def test_read_non_existing(self, client: TestClient, db: Session) -> None:
        with pytest.raises(HTTPException) as e:
            response = client.get(f"/conversations/{-1}")

        assert e.value.status_code == 404

    def test_update_non_existing(self, client: TestClient, db: Session) -> None:
        with pytest.raises(HTTPException) as e:
            response = client.patch(
                f"/conversations/{-1}", json={"title": "Updated Title"}
            )

        assert e.value.status_code == 404

    def test_update_with_wrong_type(self, client: TestClient, db: Session) -> None:
        with pytest.raises(RequestValidationError) as e:
            response = client.patch(
                f"/conversations/{TestConversations.convo_ids}", json={"title": 1}
            )

    def test_update_existing(self, client: TestClient, db: Session) -> None:
        for convo_id in TestConversations.convo_ids:
            response = client.patch(
                f"/conversations/{convo_id}", json={"title": "Updated Title"}
            )
            assert response.status_code == 200
            assert response.json()["title"] == "Updated Title"

    def test_delete_non_existing(self, client: TestClient, db: Session) -> None:
        with pytest.raises(HTTPException) as e:
            response = client.delete(f"/conversations/{-1}")

        assert e.value.status_code == 404

    def test_delete_existing(self, client: TestClient, db: Session) -> None:
        for convo_id in TestConversations.convo_ids:
            response = client.delete(f"/conversations/{convo_id}")
            assert response.status_code == 200
