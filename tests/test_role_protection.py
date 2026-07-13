import pytest
from fastapi.testclient import TestClient

from app.auth.dependencies import get_current_user
from app.main import app
from app.models.enums import UserRole
from app.models.user import User


def _fake_user(role: UserRole) -> User:
    """Cree un User "falso" en memoria, sin tocar la base de datos,
    solo para simular la identidad del usuario autenticado."""
    user = User(
        id=1,
        firebase_id="fake-uid",
        email="test@example.com",
        full_name="Usuario de Prueba",
        role=role,
        completed_tasks=0,
        level=1,
        tasks_toward_level=0,
        points_balance=0,
    )
    return user


@pytest.fixture
def client_as_padre():
    """Cliente de prueba que simula estar logueado como PADRE."""
    app.dependency_overrides[get_current_user] = lambda: _fake_user(UserRole.PADRE)
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def client_as_hijo():
    """Cliente de prueba que simula estar logueado como HIJO."""
    app.dependency_overrides[get_current_user] = lambda: _fake_user(UserRole.HIJO)
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def client_sin_auth():
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestGetMe:
    """GET /users/me deberia funcionar para CUALQUIER rol autenticado."""

    def test_padre_puede_ver_su_perfil(self, client_as_padre):
        response = client_as_padre.get("/users/me")
        assert response.status_code == 200
        assert response.json()["role"] == "padre"

    def test_hijo_puede_ver_su_perfil(self, client_as_hijo):
        response = client_as_hijo.get("/users/me")
        assert response.status_code == 200
        assert response.json()["role"] == "hijo"

    def test_sin_token_da_401_o_403(self, client_sin_auth):
        response = client_sin_auth.get("/users/me")
        assert response.status_code in (401, 403)


class TestListChildren:
    """GET /users/household/children SOLO deberia permitirlo un PADRE."""

    def test_padre_puede_ver_sus_hijos(self, client_as_padre):
        response = client_as_padre.get("/users/household/children")
        assert response.status_code == 200

    def test_hijo_NO_puede_ver_la_lista_de_hijos(self, client_as_hijo):
        response = client_as_hijo.get("/users/household/children")
        assert response.status_code == 403

    def test_sin_token_da_401_o_403(self, client_sin_auth):
        response = client_sin_auth.get("/users/household/children")
        assert response.status_code in (401, 403)