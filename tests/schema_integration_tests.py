import unittest
from unittest import mock

from API import create_app, db, Config
import os

import mock_data_generation

# This gives us the root directory for the project
basedir = os.path.abspath(os.path.dirname(__file__))
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
import graphene

from API.schema import Query


# We can test Schemas we have created here and compare the result of a graphQL query with an expected response
# Model specific tests  live here (can we retrieve all the fields we need successfully can we filter correctly e.t.c)
# Route integration tests should then test API related things (like auth/access control,success result return, error result returned) in our route integration tests

# https://docs.graphene-python.org/en/latest/testing/

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{basedir}/tests/test_app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_DOMAIN = 'http://127.0.0.1:5000'





class AppointmentsQueryAndFilterTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.app = self.app.test_client()
        db.create_all()
        mock_data_generation.insert_appointments_and_therapists(db)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @mock.patch("flask_graphql_auth.decorators._extract_header_token_value")
    def test_query_for_all_fields(self,*args):
        schema = graphene.Schema(query=Query)
        result = schema.execute("""
            {
              appointments{
                edges {
                  node {
                    appointmentId
                    startTimeUnixSeconds
                    durationSeconds
                    therapistId
                    type
                  }
                }
              }
            }""")
        self.assertEqual(result.data, {'appointments': {'edges': [{'node': {'appointmentId': '1',
                                                                            'startTimeUnixSeconds': 1644747572,
                                                                            'durationSeconds': 3600, 'therapistId': 1,
                                                                            'type': 'one-off'}}, {
                                                                      'node': {'appointmentId': '2',
                                                                               'startTimeUnixSeconds': 1644780000,
                                                                               'durationSeconds': 3600,
                                                                               'therapistId': 2,
                                                                               'type': 'consultation'}}]}})

    def test_filter_appointment_type_equals(self):
        schema = graphene.Schema(query=Query)
        result = schema.execute("""
            {
              appointments(filters: {type: "one-off"}) {
                edges {
                  node {
                    appointmentId
                    startTimeUnixSeconds
                    durationSeconds
                    therapistId
                    type
                  }
                }
              }
            }""")
        self.assertEqual(result.data, {'appointments': {'edges': [{'node': {'appointmentId': '1',
                                                                            'startTimeUnixSeconds': 1644747572,
                                                                            'durationSeconds': 3600, 'therapistId': 1,
                                                                            'type': 'one-off'}}]}})

    def test_filter_appointment_typeIn_single_option(self):
        schema = graphene.Schema(query=Query)
        result = schema.execute("""
            {
              appointments(filters: {typeIn: ["one-off"]}) {
                edges {
                  node {
                    appointmentId
                    startTimeUnixSeconds
                    durationSeconds
                    therapistId
                    type
                  }
                }
              }
            }""")
        self.assertEqual(result.data, {'appointments': {'edges': [{'node': {'appointmentId': '1',
                                                                            'startTimeUnixSeconds': 1644747572,
                                                                            'durationSeconds': 3600, 'therapistId': 1,
                                                                            'type': 'one-off'}}]}})

    def test_filter_appointment_typeIn_multiple_options(self):
        schema = graphene.Schema(query=Query)
        result = schema.execute("""
                {
                  appointments(filters: {typeIn: ["one-off","consultation"]}) {
                    edges {
                      node {
                        appointmentId
                        startTimeUnixSeconds
                        durationSeconds
                        therapistId
                        type
                      }
                    }
                  }
                }""")
        self.assertEqual(result.data, {'appointments': {'edges': [{'node': {'appointmentId': '1',
                                                                            'startTimeUnixSeconds': 1644747572,
                                                                            'durationSeconds': 3600, 'therapistId': 1,
                                                                            'type': 'one-off'}}, {
                                                                      'node': {'appointmentId': '2',
                                                                               'startTimeUnixSeconds': 1644780000,
                                                                               'durationSeconds': 3600,
                                                                               'therapistId': 2,
                                                                               'type': 'consultation'}}]}})

    def test_filter_appointment_in_startTimeUnixSecondsRange_Get_Both_Appointments(self):
        """Filters on a Range of unixTimeStamps - The range contains both test appointments created"""
        schema = graphene.Schema(query=Query)
        result = schema.execute("""
            {
              appointments(filters: {startTimeUnixSecondsRange:{begin:1644747570 end:1644790000}}) {
                edges {
                  node {
                    appointmentId
                    startTimeUnixSeconds
                    durationSeconds
                    therapistId
                    type
                  }
                }
              }
            }""")
        self.assertEqual(result.data, {'appointments': {'edges': [{'node': {'appointmentId': '1',
                                                                            'startTimeUnixSeconds': 1644747572,
                                                                            'durationSeconds': 3600, 'therapistId': 1,
                                                                            'type': 'one-off'}}, {
                                                                      'node': {'appointmentId': '2',
                                                                               'startTimeUnixSeconds': 1644780000,
                                                                               'durationSeconds': 3600,
                                                                               'therapistId': 2,
                                                                               'type': 'consultation'}}]}})

    def test_filter_appointment_in_startTimeUnixSecondsRange_Get_Latest_Appointment(self):
        """Filters on a Range of unixTimeStamps - The range contains both test appointments created"""
        schema = graphene.Schema(query=Query)
        result = schema.execute("""
            {
              appointments(filters: {startTimeUnixSecondsRange:{begin:1644747580 end:1644790000}}) {
                edges {
                  node {
                    appointmentId
                    startTimeUnixSeconds
                    durationSeconds
                    therapistId
                    type
                  }
                }
              }
            }""")
        self.assertEqual(result.data, {'appointments': {'edges': [{
            'node': {'appointmentId': '2',
                     'startTimeUnixSeconds': 1644780000,
                     'durationSeconds': 3600,
                     'therapistId': 2,
                     'type': 'consultation'}}]}})

    def test_filter_specialismsIn_single_option(self):
        schema = graphene.Schema(query=Query)
        result = schema.execute("""
            {
          appointments(filters: {hasSpecialisms: ["ADHD"]}) {
            edges {
              node {
                appointmentId
                type
                startTimeUnixSeconds
                durationSeconds
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
              }
            }
          }
        }
        """)
        self.assertEqual(result.data, {"appointments": {
            "edges": [
                {
                    "node": {
                        "appointmentId": "1",
                        "type": "one-off",
                        "startTimeUnixSeconds": 1644747572,
                        "durationSeconds": 3600,
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
                        }
                    }
                }
            ]
        }})

    def test_filter_specialismsIn_AllOptions(self):
        schema = graphene.Schema(query=Query)
        result = schema.execute("""
            {
              appointments(filters: {hasSpecialisms: ["Addiction","ADHD","CBT","Divorce","Sexuality"]}) {
                edges {
                  node {
                    appointmentId
                    type
                    startTimeUnixSeconds
                    durationSeconds
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
                  }
                }
              }
            }
        """)
        self.assertEqual(result.data, {"appointments": {
            "edges": [
                {
                    "node": {
                        "appointmentId": "1",
                        "type": "one-off",
                        "startTimeUnixSeconds": 1644747572,
                        "durationSeconds": 3600,
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
                        }
                    }
                },
                {
                    "node": {
                        "appointmentId": "2",
                        "type": "consultation",
                        "startTimeUnixSeconds": 1644780000,
                        "durationSeconds": 3600,
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
                        }
                    }
                }
            ]
        }})


if __name__ == '__main__':
    unittest.main()
