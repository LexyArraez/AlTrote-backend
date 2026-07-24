from unittest.mock import patch
from contextlib import ExitStack

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.db_connection import Base, get_db
from app.main import app
from app.models.user import User
from app.models.household import Household
from app.models.task import Task
from app.models.enums import UserRole, TaskPriority, TaskStatus


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()

    app.dependency_overrides[get_db] = lambda: session
    yield session
    app.dependency_overrides.clear()
    session.close()


@pytest.fixture
def client(db_session):
    return TestClient(app, headers={"Authorization": "Bearer fake-token"})


def _crear_familia(db_session):
    """Crea un padre, su household, y un hijo vinculado. Devuelve (padre, hijo, household)."""
    padre = User(email="mama@x.com", firebase_id="uid-padre", full_name="Ana", role=UserRole.PADRE)
    db_session.add(padre)
    db_session.commit()

    hh = Household(name="Familia X", owner_id=padre.id)
    db_session.add(hh)
    db_session.commit()

    hijo = User(email="hijo@x.com", firebase_id="uid-hijo", full_name="Alex", role=UserRole.HIJO, household_id=hh.id)
    db_session.add(hijo)
    db_session.commit()

    return padre, hijo, hh


def _crear_tarea(db_session, hh, padre, hijo, priority, points):
    task = Task(
        title="Tarea de prueba",
        priority=priority,
        points_value=points,
        household_id=hh.id,
        assigned_to_id=hijo.id,
        created_by_id=padre.id,
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task


def fake_auth_as(uid: str):
    stack = ExitStack()
    payload = {"uid": uid}
    stack.enter_context(patch("app.auth.dependencies.verify_firebase_token", return_value=payload))
    return stack


class TestCompleteTask:
    def test_hijo_completa_su_propia_tarea(self, client, db_session):
        padre, hijo, hh = _crear_familia(db_session)
        task = _crear_tarea(db_session, hh, padre, hijo, TaskPriority.BAJA, 15)

        with fake_auth_as("uid-hijo"):
            r = client.post(f"/tasks/{task.id}/complete")

        assert r.status_code == 200
        data = r.json()
        assert data["task"]["status"] == "completada"
        assert data["points_balance"] == 15
        assert data["level"] == 1
        assert data["level_up"] is False

    def test_padre_no_puede_completar_tarea_de_hijo(self, client, db_session):
        padre, hijo, hh = _crear_familia(db_session)
        task = _crear_tarea(db_session, hh, padre, hijo, TaskPriority.BAJA, 10)

        with fake_auth_as("uid-padre"):
            r = client.post(f"/tasks/{task.id}/complete")

        assert r.status_code == 403

    def test_hijo_no_puede_completar_tarea_de_otro_hijo(self, client, db_session):
        padre, hijo, hh = _crear_familia(db_session)
        otro_hijo = User(email="otro@x.com", firebase_id="uid-otro", full_name="Otro", role=UserRole.HIJO, household_id=hh.id)
        db_session.add(otro_hijo)
        db_session.commit()

        task = _crear_tarea(db_session, hh, padre, hijo, TaskPriority.BAJA, 10)

        with fake_auth_as("uid-otro"):
            r = client.post(f"/tasks/{task.id}/complete")

        assert r.status_code == 403

    def test_no_se_puede_completar_dos_veces(self, client, db_session):
        padre, hijo, hh = _crear_familia(db_session)
        task = _crear_tarea(db_session, hh, padre, hijo, TaskPriority.BAJA, 10)

        with fake_auth_as("uid-hijo"):
            client.post(f"/tasks/{task.id}/complete")
            r = client.post(f"/tasks/{task.id}/complete")

        assert r.status_code == 400

    def test_subida_de_nivel_con_bono_de_puntos(self, client, db_session):
        padre, hijo, hh = _crear_familia(db_session)

        with fake_auth_as("uid-hijo"):
            for i in range(5):
                task = _crear_tarea(db_session, hh, padre, hijo, TaskPriority.BAJA, 10)
                r = client.post(f"/tasks/{task.id}/complete")
                assert r.status_code == 200

        data = r.json()
        assert data["level"] == 2
        assert data["level_up"] is True
        assert data["points_balance"] == 50 + 100  # 5 tareas de 10 pts + bono de 100

    def test_tarea_inexistente_da_404(self, client, db_session):
        padre, hijo, hh = _crear_familia(db_session)

        with fake_auth_as("uid-hijo"):
            r = client.post("/tasks/9999/complete")

        assert r.status_code == 404