from unittest.mock import patch
from contextlib import ExitStack

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.db_connection import Base, get_db
from app.main import app


@pytest.fixture
def client():
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


def _crear_familia_con_hijo(client):
    with fake_auth("padre-x"):
        padre = client.post("/auth/register", json={"full_name": "Padre X", "role": "padre"}).json()
        code = client.get("/users/household").json()["invite_code"]

    with fake_auth("hijo-x"):
        hijo = client.post(
            "/auth/register", json={"full_name": "Hijo X", "role": "hijo", "invite_code": code}
        ).json()

    return padre, hijo


def test_padre_crea_tarea_para_su_hijo(client):
    padre, hijo = _crear_familia_con_hijo(client)

    with fake_auth("padre-x"):
        r = client.post("/tasks/", json={
            "title": "Sacar la basura",
            "priority": 1,
            "points_value": 15,
            "assigned_to_id": hijo["id"],
        })
    assert r.status_code == 201
    assert r.json()["title"] == "Sacar la basura"
    assert r.json()["status"] == "pendiente"


def test_hijo_no_puede_crear_tareas(client):
    padre, hijo = _crear_familia_con_hijo(client)

    with fake_auth("hijo-x"):
        r = client.post("/tasks/", json={
            "title": "Intento de hijo",
            "priority": 1,
            "points_value": 10,
            "assigned_to_id": hijo["id"],
        })
    assert r.status_code == 403


def test_padre_no_puede_asignar_tarea_a_hijo_ajeno(client):
    padre, hijo = _crear_familia_con_hijo(client)

    with fake_auth("padre-x"):
        r = client.post("/tasks/", json={
            "title": "Tarea para hijo inventado",
            "priority": 1,
            "points_value": 10,
            "assigned_to_id": 9999,
        })
    assert r.status_code == 400


def test_padre_ve_tareas_de_su_hijo_hijo_ve_solo_las_suyas(client):
    padre, hijo = _crear_familia_con_hijo(client)

    with fake_auth("padre-x"):
        client.post("/tasks/", json={
            "title": "Tarea 1", "priority": 1, "points_value": 10, "assigned_to_id": hijo["id"],
        })
        client.post("/tasks/", json={
            "title": "Tarea 2", "priority": 2, "points_value": 20, "assigned_to_id": hijo["id"],
        })
        r_padre = client.get("/tasks/")
    assert len(r_padre.json()) == 2

    with fake_auth("hijo-x"):
        r_hijo = client.get("/tasks/")
    assert len(r_hijo.json()) == 2


def test_editar_tarea(client):
    padre, hijo = _crear_familia_con_hijo(client)

    with fake_auth("padre-x"):
        created = client.post("/tasks/", json={
            "title": "Titulo original", "priority": 1, "points_value": 10, "assigned_to_id": hijo["id"],
        }).json()

        r = client.put(f"/tasks/{created['id']}", json={"title": "Titulo editado", "points_value": 25})
    assert r.status_code == 200
    assert r.json()["title"] == "Titulo editado"
    assert r.json()["points_value"] == 25


def test_eliminar_tarea(client):
    padre, hijo = _crear_familia_con_hijo(client)

    with fake_auth("padre-x"):
        created = client.post("/tasks/", json={
            "title": "Para borrar", "priority": 1, "points_value": 10, "assigned_to_id": hijo["id"],
        }).json()

        r_delete = client.delete(f"/tasks/{created['id']}")
        assert r_delete.status_code == 204

        r_get = client.get(f"/tasks/{created['id']}")
        assert r_get.status_code == 404


def test_crear_tarea_sin_titulo_falla(client):
    padre, hijo = _crear_familia_con_hijo(client)

    with fake_auth("padre-x"):
        r = client.post("/tasks/", json={
            "priority": 1, "points_value": 10, "assigned_to_id": hijo["id"],
        })
    assert r.status_code == 422


def test_frequency_por_defecto_es_unica(client):
    padre, hijo = _crear_familia_con_hijo(client)

    with fake_auth("padre-x"):
        r = client.post("/tasks/", json={
            "title": "Sin frequency especificada", "priority": 1, "points_value": 10, "assigned_to_id": hijo["id"],
        })
    assert r.status_code == 201
    assert r.json()["frequency"] == "unica"


def test_crear_tarea_semanal(client):
    padre, hijo = _crear_familia_con_hijo(client)

    with fake_auth("padre-x"):
        r = client.post("/tasks/", json={
            "title": "Regar las plantas", "priority": 2, "frequency": "semanal",
            "points_value": 10, "assigned_to_id": hijo["id"],
        })
    assert r.status_code == 201
    assert r.json()["frequency"] == "semanal"