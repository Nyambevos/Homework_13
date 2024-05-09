from datetime import date, timedelta

import pytest
from unittest.mock import MagicMock, patch
from fastapi_limiter import FastAPILimiter
from sqlalchemy import and_

from src.database.models import User, Contact
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

@pytest.fixture(autouse=True)
def mock_auth_service_r():
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        r_mock.evalsha.return_value = 0
        yield r_mock






# get /contacts/birthdays


# post /contacts
# get /contacts
# get /contacts/search
# get /contacts/{contact_id}
# put /contacts/{contact_id}
# delete /contacts/{contact_id}

def test_create_contact(client, token):
    contact = {
            "firstname": "spider",
            "lastname": "man",
            "email": "spider@man.com",
            "phone": "1234567890",
            "birthday": str(date.today() + timedelta(days=5))
        }
    response = client.post(
        "/api/contacts",
        json=contact,
        headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["firstname"] == contact["firstname"]
    assert "id" in data

@pytest.mark.asyncio
async def test_read_contacts(client, token):
        await FastAPILimiter.init(auth_service.r)
        
        response = client.get(
            "/api/contacts",
            headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["firstname"] == "spider"

def test_search_contacts(client, token):
    response = client.get(
           "/api/contacts/search",
           params = {"email": "spider@man.com"},
           headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["email"] == "spider@man.com"

def test_read_contact(client, token):
    contact_id = 1
    response = client.get(
          f"/api/contacts/{contact_id}",
          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["firstname"] == "spider"

    fake_contact_id = 12
    response = client.get(
          f"/api/contacts/{fake_contact_id}",
          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404, response.text

def test_update_contact(client, token, session, user):
    contact_id = 1
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    contact: Contact = session.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == current_user.id)).first()
    
    assert contact is not None
    assert contact.user_id == current_user.id

    contact.firstname = "New_spider"

    serialized_contact = {
        "firstname": contact.firstname,
        "lastname": contact.lastname,
        "email": contact.email,
        "phone": contact.phone,
        "birthday": str(contact.birthday)
    }

    response = client.put(
          f"/api/contacts/{contact_id}",
          json=serialized_contact,
          headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["firstname"] == "New_spider"

    fake_contact_id = 12
    response = client.put(
          f"/api/contacts/{fake_contact_id}",
          json=serialized_contact,
          headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 404, response.text

def test_remove_contact(client, token):
    fake_contact_id = 12
    response = client.delete(
         f"/api/contacts/{fake_contact_id}",
         headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404, response.text

    contact_id = 1
    response = client.delete(
         f"/api/contacts/{contact_id}",
         headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["firstname"] == "New_spider"

    response = client.delete(
         f"/api/contacts/{contact_id}",
         headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404, response.text

def test_upcoming_birthdays(client, token, session, user):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    response = client.get(
          f"/api/contacts/birthdays",
          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert type(data) == list
    assert len(data) == 0

    contact = Contact(
        firstname = "spider",
        lastname = "man",
        email = "spider@man.com",
        phone = "1234567890",
        birthday = date.today() + timedelta(days=5),
        user = current_user)
    session.add(contact)
    session.commit()
    session.refresh(contact)

    response = client.get(
          f"/api/contacts/birthdays",
          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 1

    contact = Contact(
        firstname = "Tony",
        lastname = "Stark",
        email = "stark@marvel.com",
        phone = "0987654321",
        birthday = date(day=10, month=3, year=1973),
        user = current_user)
    session.add(contact)
    session.commit()
    session.refresh(contact)

    response = client.get(
          f"/api/contacts/birthdays",
          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 1

    contact = Contact(
        firstname = "Jack",
        lastname = "Kirby",
        email = "kirby@marvel.com",
        phone = "0987667890",
        birthday = date.today() + timedelta(days=2),
        user = current_user)
    session.add(contact)
    session.commit()
    session.refresh(contact)

    response = client.get(
          f"/api/contacts/birthdays",
          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 2