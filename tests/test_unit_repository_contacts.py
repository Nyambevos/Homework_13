from datetime import date
import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session
from fastapi import HTTPException

from src.database.models import Contact, User
from src.schemas import ContactModel
from src.repository.contacts import (
    get_contacts,
    get_contact,
    create_contact,
    update_contact,
    remove_contact,
    search_contacts,
    get_upcoming_birthdays,
)


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = await get_contacts(skip=0, limit=10, user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        body = ContactModel(firstname="test", lastname="tests", email="test@test.com", phone="25668151", birthday=date(year=1990, month=11, day=20))
        result = await create_contact(body=body, user=self.user, db=self.session)
        self.assertEqual(result.firstname, body.firstname)
        self.assertEqual(result.lastname, body.lastname)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.birthday, body.birthday)
        self.assertTrue(hasattr(result, "id"))

    async def test_remove_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_remove_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_contact_found(self):
        body = ContactModel(firstname="test", lastname="tests", email="test@test.com", phone="25668151", birthday=date(year=1990, month=11, day=20))
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_update_contact_not_found(self):
        body = ContactModel(firstname="test", lastname="tests", email="test@test.com", phone="25668151", birthday=date(year=1990, month=11, day=20))
        self.session.query().filter().first.return_value = None
        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_search_contacts_found(self):
        firstname = "test"
        lastname = "tests"
        email = "test@test.com"
        contacts = [
            Contact(firstname=firstname, lastname=lastname, email=email)
        ]
        self.session.query().filter().offset().limit().all.return_value = contacts

        result = await search_contacts(
            skip=0,
            limit=10,
            firstname=firstname,
            lastname=None,
            email=None,
            user=self.user,
            db=self.session)
        self.assertEqual(result, contacts)

        result = await search_contacts(
            skip=0,
            limit=10,
            firstname=None,
            lastname=lastname,
            email=None,
            user=self.user,
            db=self.session)
        self.assertEqual(result, contacts)

        result = await search_contacts(
            skip=0,
            limit=10,
            firstname=None,
            lastname=None,
            email=email,
            user=self.user,
            db=self.session)
        self.assertEqual(result, contacts)


    async def test_search_contacts_not_found(self):
        self.session.query().filter().offset().limit().all.return_value = []

        result = await search_contacts(
            skip=0,
            limit=10,
            firstname="test",
            lastname=None,
            email=None,
            user=self.user,
            db=self.session)
        self.assertRaises(HTTPException)

        result = await search_contacts(
            skip=0,
            limit=10,
            firstname=None,
            lastname="test",
            email=None,
            user=self.user,
            db=self.session)
        self.assertRaises(HTTPException)

        result = await search_contacts(
            skip=0,
            limit=10,
            firstname=None,
            lastname=None,
            email="test",
            user=self.user,
            db=self.session)
        self.assertRaises(HTTPException)

    async def test_get_upcoming_birthdays_found(self):
        contacts = [
            Contact(
                firstname="test",
                lastname="tests",
                email="test@test.com",
                phone="25668151",
                birthday=date(year=1990, month=5, day=10))
        ]
        self.session.query(Contact).filter().all.return_value = contacts
        result = await get_upcoming_birthdays(
            skip=0,
            limit=10,
            user=self.user,
            db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_upcoming_birthdays_not_found(self):
        self.session.query(Contact).filter().all.return_value = []
        result = await get_upcoming_birthdays(
            skip=0,
            limit=10,
            user=self.user,
            db=self.session)
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()