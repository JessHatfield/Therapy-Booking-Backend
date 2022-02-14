import unittest
from unittest import mock
from API import create_app, db, Config
import mock_data_generation

import os




class TestConfig(Config):
    basedir = os.path.abspath(os.path.dirname(__file__))
    basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{basedir}/tests/test_app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_DOMAIN = 'http://127.0.0.1:5000'


class Authentication_Integration_Tests(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.app = self.app.test_client()
        db.create_all()
        mock_data_generation.insert_appointments_and_therapists(db)
        mock_data_generation.insert_api_users(db)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_can_generate_access_token_and_refresh_token_for_username_and_password_and_then_access_api(self):
        """Tests that given a prexisting username and password an access token and refreshToken can be generated via graphQL Mutation
           Value of the access token and refresh token are different each time function is called. W
        """

        endpoint = f'{TestConfig.API_DOMAIN}/graphql'
        response = self.app.post(endpoint, json={"query": """
            mutation{auth(password:"password",username:"test_user"){
              accessToken
              refreshToken}
            }
        """})
        self.assertEqual(response.status_code, 200)

        access_token_generated = response.json['data']['auth']['accessToken']

        response = self.app.post(endpoint, headers={"authorization": f"Bearer {access_token_generated}"}, json={"query": """
                  {appointments{edges{node{startTimeUnixSeconds}}}}
          """})

        self.assertEqual(response.json, {'data': {'appointments': {
            'edges': [{'node': {'startTimeUnixSeconds': 1644747572}},
                      {'node': {'startTimeUnixSeconds': 1644780000}}]}}})

    def test_unauthorized_requests_are_rejected(self):
        """Tests that given a prexisting username and password an access token and refreshToken can be generated via graphQL Mutation
           Value of the access token and refresh token are different each time function is called. W
        """

        endpoint = f'{TestConfig.API_DOMAIN}/graphql'

        response = self.app.post(endpoint, headers={"authorization": f"Bearer InvalidToken"}, json={"query": """
                     {appointments{edges{node{startTimeUnixSeconds}}}}
             """})

        self.assertEqual(response.json, {'errors': [
            {'message': 'Not enough segments', 'locations': [{'line': 2, 'column': 23}], 'path': ['appointments']}],
            'data': {'appointments': None}})

    def test_access_token_can_be_refreshed_and_then_access_api(self):
        # gen access token

        endpoint = f'{TestConfig.API_DOMAIN}/graphql'
        response = self.app.post(endpoint, json={"query": """
                    mutation{auth(password:"password",username:"test_user"){
                      accessToken
                      refreshToken}
                    }
                """})

        access_token_generated = response.json['data']['auth']['accessToken']
        refresh_token_generated = response.json['data']['auth']['refreshToken']

        # generate refresh token
        response = self.app.post(endpoint,
                                 json={
                                     "query": 'mutation{refresh(refreshToken:"' + refresh_token_generated + '"){newToken}}'})

        new_access_token_generated = response.json['data']['refresh']['newToken']
        self.assertNotEqual(access_token_generated, new_access_token_generated)

        # make a protected request with new access token
        final_request = self.app.post(endpoint, headers={"authorization": f"Bearer {new_access_token_generated}"},
                                      json={"query": """
            {
              appointments {
                edges {
                  node {
                    startTimeUnixSeconds
                  }
                }
              }
            }
        """})

        self.assertEqual(final_request.status_code, 200)
        self.assertEqual(final_request.json, {'data': {'appointments': {
            'edges': [{'node': {'startTimeUnixSeconds': 1644747572}},
                      {'node': {'startTimeUnixSeconds': 1644780000}}]}}})


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

    @mock.patch('API.authentication.decorators._extract_header_token_value')
    @mock.patch('API.authentication.decorators.verify_jwt_in_argument')
    def test_graphql_endpoint_returns_empty_query_result(self, *args):
        """
        checks to see that our endpoint returns an empty data structure when no database rows exist
        """
        endpoint = f'{TestConfig.API_DOMAIN}/graphql'
        response = self.app.post(endpoint, json={
            "query": "{appointments{"
                     "edges{"
                     "node{"
                     "startTimeUnixSeconds,"
                     "durationSeconds,"
                     "}}}}"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"data": {"appointments": {'edges': []}}})

    @mock.patch('API.authentication.decorators._extract_header_token_value')
    @mock.patch('API.authentication.decorators.verify_jwt_in_argument')
    def test_graphql_endpoint_returns_error_response_for_non_existent_object(self, *args):
        """
        Checks to see that error messages are being returned from Graphene via our endpoint
        """
        endpoint = f'{TestConfig.API_DOMAIN}/graphql'
        response = self.app.post(endpoint, json={"query": "query{non_existent_object{non_existent_field}}"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'errors': [
            {'message': 'Cannot query field "non_existent_object" on type "Query".',
             'locations': [{'line': 1, 'column': 7}]}]})

    @mock.patch('API.authentication.decorators._extract_header_token_value')
    @mock.patch('API.authentication.decorators.verify_jwt_in_argument')
    def test_graphql_endpoint_returns_error_response_for_non_existent_field(self, *args):
        """
        Checks to see that error messages are being returned from GraphQL-Core
        """
        endpoint = f'{TestConfig.API_DOMAIN}/graphql'
        response = self.app.post(endpoint, json={"query": "query{appointments{non_existent_field}}"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'errors': [
            {'message': 'Cannot query field "non_existent_field" on type "AppointmentsSchemaConnection".',
             'locations': [{'line': 1, 'column': 20}]}]})


class API_Acceptance_Tests(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.app = self.app.test_client()
        db.create_all()
        # generate our mock data
        mock_data_generation.insert_appointments_and_therapists(db)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @mock.patch('API.authentication.decorators._extract_header_token_value')
    @mock.patch('API.authentication.decorators.verify_jwt_in_argument')
    def test_graphql_endpoint_returns_required_appointment_fields(self, *args):
        """
        Checks to see that the user can retrieve
            *Therapists Name
            *Appointment Time
            *Appointment Duration
            *Appointment Type

        With NO Filters Applied
        """
        endpoint = f'{TestConfig.API_DOMAIN}/graphql'
        response = self.app.post(endpoint, json={"query": """
           {
  appointments {
    edges {
      node {
        therapists {
          firstName
          lastName
          specialisms {
            edges {
              node {
                specialismName
              }
            }
          }
        }
        startTimeUnixSeconds
        durationSeconds
        type
      }
    }
  }
}"""})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {
            "data": {
                "appointments": {
                    "edges": [
                        {
                            "node": {
                                "therapists": {
                                    "firstName": "jeff",
                                    "lastName": "smith",
                                    "specialisms": {
                                        "edges": [
                                            {
                                                "node": {
                                                    "specialismName": "Addiction"
                                                }
                                            },
                                            {
                                                "node": {
                                                    "specialismName": "ADHD"
                                                }
                                            }
                                        ]
                                    }
                                },
                                "startTimeUnixSeconds": 1644747572,
                                "durationSeconds": 3600,
                                "type": "one-off"
                            }
                        },
                        {
                            "node": {
                                "therapists": {
                                    "firstName": "jane",
                                    "lastName": "smith",
                                    "specialisms": {
                                        "edges": [
                                            {
                                                "node": {
                                                    "specialismName": "CBT"
                                                }
                                            },
                                            {
                                                "node": {
                                                    "specialismName": "Divorce"
                                                }
                                            },
                                            {
                                                "node": {
                                                    "specialismName": "Sexuality"
                                                }
                                            }
                                        ]
                                    }
                                },
                                "startTimeUnixSeconds": 1644780000,
                                "durationSeconds": 3600,
                                "type": "consultation"
                            }
                        }
                    ]
                }}})

    @mock.patch('API.authentication.decorators._extract_header_token_value')
    @mock.patch('API.authentication.decorators.verify_jwt_in_argument')
    def test_graphql_endpoint_returns_required_appointment_fields_with_all_filters(self, *args):
        """
        Checks to see that the user can retrieve
            *Therapists Name
            *Appointment Time
            *Appointment Duration
            *Appointment Type

        With Filters Applied
            *Date Range
            *Appointment Type
            *Therapist Specialism
        """

        endpoint = f'{TestConfig.API_DOMAIN}/graphql'
        response = self.app.post(endpoint, json={"query": """
           {
              appointments(filters: {hasSpecialisms: ["ADHD"], type: "one-off", startTimeUnixSecondsRange: {begin: 1644747500, end: 1644790000}},sort) {
                edges {
                  node {
                    therapists {
                      firstName
                      lastName
                      specialisms {
                        edges {
                          node {
                            specialismName
                          }
                        }
                      }
                    }
                    startTimeUnixSeconds
                    durationSeconds
                    type
                  }
                }
              }
            }
        """})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {
            "data": {
                "appointments": {
                    "edges": [
                        {
                            "node": {
                                "therapists": {
                                    "firstName": "jeff",
                                    "lastName": "smith",
                                    "specialisms": {
                                        "edges": [
                                            {
                                                "node": {
                                                    "specialismName": "Addiction"
                                                }
                                            },
                                            {
                                                "node": {
                                                    "specialismName": "ADHD"
                                                }
                                            }
                                        ]
                                    }
                                },
                                "startTimeUnixSeconds": 1644747572,
                                "durationSeconds": 3600,
                                "type": "one-off"
                            }
                        }
                    ]
                }
            }
        })


if __name__ == '__main__':
    unittest.main()
