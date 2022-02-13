import unittest

import mock_data_generation
from API import create_app, db, Config
import os

# This gives us the root directory for the project
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

    def test_graphql_endpoint_returns_empty_query_result(self):
        """
        checks to see that our endpoint returns an empty data structure when no database rows exist
        """
        endpoint = f'{TestConfig.API_DOMAIN}/graphql'
        response = self.app.post(endpoint, json={
            "query": "{appointments{"
                     "edges{"
                     "node{"
                     "id,"
                     "startTimeUnixSeconds,"
                     "durationSeconds,"
                     "therapistId,"
                     "type,specialism""}}}}"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"data": {"appointments": {'edges': []}}})

    def test_graphql_endpoint_returns_error_response_for_non_existent_object(self):
        """
        Checks to see that error messages are being returned from Graphene via our endpoint
        """
        endpoint = f'{TestConfig.API_DOMAIN}/graphql'
        response = self.app.post(endpoint, json={"query": "query{non_existent_object{non_existent_field}}"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'errors': [
            {'message': 'Cannot query field "non_existent_object" on type "Query".',
             'locations': [{'line': 1, 'column': 7}]}]})

    def test_graphql_endpoint_returns_error_response_for_non_existent_field(self):
        """
        Checks to see that error messages are being returned from GraphQL-Core
        """
        endpoint = f'{TestConfig.API_DOMAIN}/graphql'
        response = self.app.post(endpoint, json={"query": "query{appointments{non_existent_field}}"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'errors': [
            {'message': 'Cannot query field "non_existent_field" on type "AppointmentsConnection".',
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

    def test_graphql_endpoint_returns_required_appointment_fields(self):
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
          appointments{
            edges {
              node {
                therapists {
                  firstName
                  lastName
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
                                    "lastName": "smith"
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
                                    "lastName": "smith"
                                },
                                "startTimeUnixSeconds": 1644780000,
                                "durationSeconds": 3600,
                                "type": "consultation"
                            }
                        }
                    ]
                }
            }
        })

    def test_graphql_endpoint_returns_required_appointment_fields_with_all_filters(self):
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
              appointments(filters: {hasSpecialisms: ["ADHD"], type: "one-off", startTimeUnixSecondsRange: {begin: 1644747500, end: 1644790000}}) {
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
