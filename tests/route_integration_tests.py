import unittest
from API import create_app,db,Config
import os

#This gives us the root directory for the project
basedir = os.path.abspath(os.path.dirname(__file__))
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{basedir}/tests/test_app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_DOMAIN = 'http://127.0.0.1:5000'


class API_Integration_Tests(unittest.TestCase):

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

    def test_api_running_and_queryable(self):
        endpoint=f'{TestConfig.API_DOMAIN}/graphql'
        response=self.app.post(endpoint,json={"query":"query{appointments{id,therapistId,specialism}}"})
        self.assertEqual(response.status_code,200)



if __name__ == '__main__':
    unittest.main()
