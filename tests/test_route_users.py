import io
from PIL import Image

from unittest.mock import MagicMock, patch

import pytest

from src.database.models import User
from src.services.auth import auth_service


@pytest.fixture()
def token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    client.post("/api/auth/signup", json=user)
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    data = response.json()
    return data["access_token"]


def test_read_users_me(client, token):
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, dict)
        assert data["username"] == "deadpool"
        assert "id" in data


def test_update_avatar_user(client, token):
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        file_avatar = Image.new("RGB", (300, 200), "white")
        buffer = io.BytesIO()
        file_avatar.save(buffer, format='JPEG')
        binary_file_avatar = buffer.getvalue()

        response = client.patch(
            "/api/users/avatar",
            files={"file": binary_file_avatar},
            headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, dict)
        assert data["username"] == "deadpool"
        assert "id" in data