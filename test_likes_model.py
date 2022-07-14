"""Likes model tests."""
from app import app
import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Song, Likes

os.environ['DATABASE_URL'] = "postgresql:///genius-test"


db.create_all()


class LikesModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u1 = User.signup("test1", "email1@email.com", "password", None)
        uid1 = 1111
        u1.id = uid1

        u2 = User.signup("test2", "email2@email.com", "password", None)
        uid2 = 2222
        u2.id = uid2

        db.session.commit()

        u1 = User.query.get(uid1)
        u2 = User.query.get(uid2)

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_likes_model(self):
        """Does basic model work?"""

        l = Likes(
            user_id=2222,
            song_id=1,
			title="testitle",
            artist="testartist",
         	lyrics="testlyrics"
        )

        db.session.add(l)
        db.session.commit()

        self.assertEqual(len(Likes), 1)
