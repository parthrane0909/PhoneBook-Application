import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def test_contact_crud_and_duplicate_phone(client):
    payload = {
        "name": "Ada Lovelace",
        "phone_number": "+1 555 0100",
        "email": "ada@example.com",
        "tags": ["Work"],
    }

    created = client.post("/contacts/", json=payload)
    assert created.status_code == 200
    contact_id = created.json()["id"]
    assert created.json()["tags"][0]["name"] == "Work"

    duplicate = client.post("/contacts/", json={**payload, "email": "other@example.com"})
    assert duplicate.status_code == 400

    listed = client.get("/contacts/", params={"search": "Ada", "tag": "Work"})
    assert listed.status_code == 200
    assert listed.json()["total"] == 1

    tag_search = client.get("/contacts/", params={"search": "work"})
    assert tag_search.status_code == 200
    assert tag_search.json()["total"] == 1

    combined_search = client.get("/contacts/", params={"search": "Ada", "tag": "Friends"})
    assert combined_search.status_code == 200
    assert combined_search.json()["total"] == 0

    metrics = client.get("/contacts/metrics")
    assert metrics.status_code == 200
    assert metrics.json()["total"] == 1
    assert metrics.json()["unlabeled"] == 0

    viewed_list = client.get("/contacts/", params={"recent": True, "sort": "recently_viewed"})
    assert viewed_list.status_code == 200
    assert viewed_list.json()["total"] == 0

    updated = client.put(f"/contacts/{contact_id}", json={"name": "Ada Byron", "tags": ["Friends"]})
    assert updated.status_code == 200
    assert updated.json()["tags"][0]["name"] == "Friends"

    viewed = client.patch(f"/contacts/{contact_id}/viewed")
    assert viewed.status_code == 200
    assert viewed.json()["last_viewed_at"] is not None

    deleted = client.delete(f"/contacts/{contact_id}")
    assert deleted.status_code == 200
    assert client.get(f"/contacts/{contact_id}").status_code == 404


def test_validation_requires_name_and_phone(client):
    response = client.post("/contacts/", json={"name": "Missing phone"})
    assert response.status_code == 422


def test_import_validates_rows_and_skips_duplicates(client):
    response = client.post(
        "/contacts/import",
        json={
            "rows": [
                {"name": "Imported One", "phone_number": "9000000001", "email": "one@example.com", "address": None, "tags": []},
                {"name": "Duplicate", "phone_number": "9000000001", "email": "two@example.com", "address": None, "tags": []},
            ]
        },
    )

    assert response.status_code == 200
    assert response.json()["imported"] == 1
    assert response.json()["skipped"] == 1
    assert response.json()["errors"][0]["row"] == 3

    forbidden = client.post(
        "/contacts/import",
        json={"rows": [{"name": "Unsafe", "phone_number": "9000000002", "id": 99}]},
    )
    assert forbidden.status_code == 422
