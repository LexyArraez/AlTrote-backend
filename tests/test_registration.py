from contextlib import ExitStack
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.db_connection import Base, get_db
from app.main import app


@pytest.fixture
def client():
    """Cliente de prueba con base de datos en memoria"""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)

    app.dependency_overrides[get_db] = lambda: TestSession()
    yield TestClient(app, headers={"Authorization": "Bearer fake-token"})
    app.dependency_overrides.clear()

def fake_auth(uid: str):
    stack = ExitStack()
    payload = {"uid": uid, "email": f"{uid}@example.com"}
    stack.enter_context(patch("app.auth.dependencies.verify_firebase_token", return_value=payload))
    return stack

def test_padre_se_registra_y_tiene_invite_code(client):
    with fake_auth("padre1"):
        r = client.post("/auth/register", json={"full_name": "Ana", "role": "padre"})
        assert r.status_code == 201

        household = client.get("/users/household").json()
        assert household["invite_code"]


def test_hijo_se_vincula_con_codigo_valido(client):
    with fake_auth("padre2"):
        client.post("/auth/register", json={"full_name": "Ana", "role": "padre"})
        code = client.get("/users/household").json()["invite_code"]

    with fake_auth("hijo2"):
        r = client.post("/auth/register", json={"full_name": "Alex", "role": "hijo", "invite_code": code})
        assert r.status_code == 201
        assert r.json()["household_id"] is not None


def test_hijo_con_codigo_invalido_falla(client):
    with fake_auth("hijo3"):
        r = client.post("/auth/register", json={"full_name": "Alex", "role": "hijo", "invite_code": "NO-EXISTE"})
        assert r.status_code == 400