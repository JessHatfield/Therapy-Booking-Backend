import unittest
from Spill_Backend_App.API.models import User
from Spill_Backend_App.API.config import Config
from Spill_Backend_App.API import create_app, db
import os


class TestConfig(Config):
    basedir = os.path.abspath(os.path.dirname(__file__))
    basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{basedir}/tests/test_app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_DOMAIN = 'http://127.0.0.1:5000'


class User_Model_Tests(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.app = self.app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_can_hash_password_and_then_compare(self):
        test_user = User(username="test_user", email="test@test.com")
        test_user.set_password("password")
        db.session.add(test_user)
        db.session.commit()

        user_in_db=User.query.filter_by(user_id=1).first()
        match=user_in_db.check_password(password="password")

        self.assertEqual(match,True)

