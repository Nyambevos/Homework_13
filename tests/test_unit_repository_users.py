import unittest
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session
from libgravatar import Gravatar

from src.database.models import User
from src.schemas import UserModel
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    update_avatar
)

class TestUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_user_by_email(self):
        user = User(email="test@test.com")
        self.session.query().filter().first.return_value = user
        result = await get_user_by_email(email="test@test.com", db=self.session)
        self.assertEqual(result, user)

        self.session.query().filter().first.return_value = None
        result = await get_user_by_email(email="test@test.com", db=self.session)
        self.assertIsNone(result)

    async def test_create_user(self):
        body = UserModel(
            username="tester",
            email="test@test.com",
            password="Test123456",
            )
        gravatar = MagicMock(spec=Gravatar)

        gravatar.get_image.return_value = "None"
        self.session.add.return_value = None
        self.session.commit.return_value = None
        self.session.refresh.return_value = None

        result = await create_user(body=body, db=self.session)

        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)
        self.assertTrue(hasattr(result, "id"))

    async def test_update_token(self):
        self.session.commit.return_value = None

        result = await update_token(user=self.user, token="testTokenTest" ,db=self.session)
        self.assertIsNone(result)

    async def test_confirmed_email(self):
        user = User(email="test@test.com")
        with patch("src.repository.users.get_user_by_email", return_value=user):
            self.session.commit.return_value = None
    
            result = await confirmed_email(email="test@test.com", db=self.session)
            self.assertIsNone(result)

    async def test_update_avatar(self):
        user = User(email="test@test.com", password="Test123456")
        with patch("src.repository.users.get_user_by_email", return_value=user):
            self.session.commit.return_value = None

            result = await update_avatar(
                email="test@test.com",
                url="img.test.com/image.img",
                db=self.session)
            self.assertEqual(result, user)