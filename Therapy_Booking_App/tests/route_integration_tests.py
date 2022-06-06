import unittest
from unittest import mock

from API import create_app, db, Config
import mock_data_generation as mock_data_generation

import os


class TestConfig(Config):
    basedir = os.path.abspath(os.path.dirname(__file__))
    basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
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

    @mock.patch('API.authentication.decorators.get_token_auth_header')
    @mock.patch('API.authentication.decorators.verify_jwt_in_argument')
    def test_graphql_endpoint_returns_empty_query_result(self, *args):
        """
        checks to see that our endpoint returns an empty data structure when no database rows exist
        """
        endpoint = f'{TestConfig.API_DOMAIN}/graphql'
        response = self.app.post(endpoint, json={
            "query": """
                        {
              appointments {
                edges {
                  node {
                    startTimeUnixSeconds
                    durationSeconds
                  }
                }
              }
            }
            """})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"data": {"appointments": {'edges': []}}})

    @mock.patch('API.authentication.decorators.get_token_auth_header')
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

    @mock.patch('API.authentication.decorators.get_token_auth_header')
    @mock.patch('API.authentication.decorators.verify_jwt_in_argument')
    def test_graphql_endpoint_returns_error_response_for_non_existent_field(self, *args):
        """
        Checks to see that error messages are being returned from GraphQL-Core
        """
        endpoint = f'{TestConfig.API_DOMAIN}/graphql'
        response = self.app.post(endpoint, json={"query": "query{appointments{edges{node{non_existent_field}}}}"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'errors': [
            {'message': 'Cannot query field "non_existent_field" on type "AppointmentsSchema".',
             'locations': [{'line': 1, 'column': 31}]}]})


class API_Acceptance_Tests(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.app = self.app.test_client()
        db.create_all()
        # generate our mock data
        mock_data_generation.insert_appointments_and_therapists(db)
        mock_data_generation.insert_api_users(db)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @mock.patch('API.authentication.decorators.get_token_auth_header')
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
                }
            }
        })

    @mock.patch('API.authentication.decorators.get_token_auth_header')
    @mock.patch('API.authentication.decorators.verify_jwt_in_argument')
    def test_graphql_endpoint_returns_required_appointment_fields_with_typeEq_filter(self, *args):
        """
        Checks to see that the user can retrieve
            *Therapists Name
            *Appointment Time
            *Appointment Duration
            *Appointment Type

        With Filters Applied
            *Appointment Type
        """

        endpoint = f'{TestConfig.API_DOMAIN}/graphql'
        response = self.app.post(endpoint, json={"query": """
           {
          appointments(filters: {type: "one-off"}) {
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

    @mock.patch('API.authentication.decorators.get_token_auth_header')
    @mock.patch('API.authentication.decorators.verify_jwt_in_argument')
    def test_graphql_endpoint_returns_required_appointment_fields_with_typeIn_filter_single_option(self, *args):
        """
        Checks to see that the user can retrieve
            *Therapists Name
            *Appointment Time
            *Appointment Duration
            *Appointment Type

        With Filters Applied
            *Appointment Type one of one option
        """

        endpoint = f'{TestConfig.API_DOMAIN}/graphql'
        response = self.app.post(endpoint, json={"query": """
              {
             appointments(filters: {typeIn:["one-off"]}) {
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

    @mock.patch('API.authentication.decorators.get_token_auth_header')
    @mock.patch('API.authentication.decorators.verify_jwt_in_argument')
    def test_graphql_endpoint_returns_required_appointment_fields_with_typeIn_filter_multiple_options(self, *args):
        """
        Checks to see that the user can retrieve
            *Therapists Name
            *Appointment Time
            *Appointment Duration
            *Appointment Type

        With Filters Applied
            *Appointment Type one of many options
        """

        endpoint = f'{TestConfig.API_DOMAIN}/graphql'
        response = self.app.post(endpoint, json={"query": """
                 {
                appointments(filters: {typeIn: ["one-off", "consultation"]}) {
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
                }
            }
        })

    @mock.patch('API.authentication.decorators.get_token_auth_header')
    @mock.patch('API.authentication.decorators.verify_jwt_in_argument')
    def test_graphql_endpoint_returns_required_appointment_fields_with_startTimeUnixSecondsRange_filter(self, *args):
        """
        Checks to see that the user can retrieve
            *Therapists Name
            *Appointment Time
            *Appointment Duration
            *Appointment Type

        With Filters Applied
            *Appointment startTimeUnixSeconds within Range
        """

        endpoint = f'{TestConfig.API_DOMAIN}/graphql'
        response = self.app.post(endpoint, json={"query": """
                         {
                          appointments(filters: {startTimeUnixSecondsRange: {begin: 1644747580, end: 1644790000}}) {
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
                }
            }
        })

    @mock.patch('API.authentication.decorators.get_token_auth_header')
    @mock.patch('API.authentication.decorators.verify_jwt_in_argument')
    def test_graphql_endpoint_returns_required_appointment_fields_with_specialismsIn_filter_one_specialism(self, *args):
        """
        Checks to see that the user can retrieve
            *Therapists Name
            *Appointment Time
            *Appointment Duration
            *Appointment Type

        With Filters Applied
            *Appointment specialsmsIn
        """

        endpoint = f'{TestConfig.API_DOMAIN}/graphql'
        response = self.app.post(endpoint, json={"query": """
                             {
                              appointments(filters: {hasSpecialisms: ["ADHD"]}) {
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

    @mock.patch('API.authentication.decorators.get_token_auth_header')
    @mock.patch('API.authentication.decorators.verify_jwt_in_argument')
    def test_graphql_endpoint_returns_required_appointment_fields_with_all_filters(self, *args):
        """
        Checks to see that the user can retrieve
            *Therapists Name
            *Appointment Time
            *Appointment Duration
            *Appointment Type

            We add a few new rows to our mock data for this test to confirm that filters are "AND" filters
            and that appointments not matching the filter are ignored




        With Filters Applied
            *Date Range
            *Appointment Type
            *Therapist Specialism
        """

        mock_data_generation.generate_nine_unique_appointments_for_testing_filter_combinations(db)

        endpoint = f'{TestConfig.API_DOMAIN}/graphql'
        response = self.app.post(endpoint, json={"query": """
                {
               appointments(filters: {hasSpecialisms: ["ADHD"], type: "one-off", startTimeUnixSecondsRange: {begin: 0, end: 0}}) {
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
        self.assertEqual(response.json, {'data': {'appointments': {'edges': [{'node': {
            'therapists': {'firstName': 'charlie', 'lastName': 'kelly',
                           'specialisms': {'edges': [{'node': {'specialismName': 'ADHD'}}]}}, 'startTimeUnixSeconds': 0,
            'durationSeconds': 0, 'type': 'one-off'}}]}}})

    @mock.patch('API.authentication.decorators.get_token_auth_header')
    @mock.patch('API.authentication.decorators.verify_jwt_in_argument')
    def test_appointment_mutate_on_graphql_endpoint(self, *args):
        endpoint = f'{TestConfig.API_DOMAIN}/graphql'
        response = self.app.post(endpoint, json={"query": """
           mutation {
              appointment(therapistId: 1, startTimeUnixSeconds: 1644874120, durationSeconds: 3600, type: "one-off") {
                appointment {
                  appointmentId
                  startTimeUnixSeconds
                  durationSeconds
                  type
                  therapists {
                    therapistId
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
            """})

        self.assertEqual(response.json, {
            "data": {
                "appointment": {
                    "appointment": {
                        "appointmentId": "3",
                        "startTimeUnixSeconds": 1644874120,
                        "durationSeconds": 3600,
                        "type": "one-off",
                        "therapists": {
                            "therapistId": "1",
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
            }
        })

    @mock.patch('API.authentication.decorators.get_token_auth_header')
    @mock.patch('API.authentication.decorators.verify_jwt_in_argument')
    def test_appointment_mutate_on_graphql_endpoint_idempotent_on_multiple_calls(self, *args):
        endpoint = f'{TestConfig.API_DOMAIN}/graphql'
        query = """
              mutation {
                 appointment(therapistId: 1, startTimeUnixSeconds: 1644874120, durationSeconds: 3600, type: "one-off") {
                   appointment {
                     appointmentId
                     startTimeUnixSeconds
                     durationSeconds
                     type
                     therapists {
                       therapistId
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
               """
        expected_data = {
            "data": {
                "appointment": {
                    "appointment": {
                        "appointmentId": '3',
                        "startTimeUnixSeconds": 1644874120,
                        "durationSeconds": 3600,
                        "type": "one-off",
                        "therapists": {
                            "therapistId": "1",
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
            }
        }
        # The new appointment is created
        response = self.app.post(endpoint, json={"query": query})

        self.assertEqual(response.json, expected_data)

        # The same query is sent again
        response_2 = self.app.post(endpoint, json={"query": query})

        # But no new appointment is created
        self.assertEqual(response_2.json, expected_data)

        new_appointment = self.app.post(endpoint, json={"query": """
              mutation {
                 appointment(therapistId: 2, startTimeUnixSeconds: 1644874120, durationSeconds: 3600, type: "one-off") {
                   appointment {
                     appointmentId
                     startTimeUnixSeconds
                     durationSeconds
                     type
                     therapists {
                       therapistId
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
               """})

        # an appointment for a different therapist can be created
        self.assertEqual(new_appointment.json, {
            "data": {
                "appointment": {
                    "appointment": {
                        "appointmentId": '4',
                        "startTimeUnixSeconds": 1644874120,
                        "durationSeconds": 3600,
                        "type": "one-off",
                        "therapists": {
                            "therapistId": "2",
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
            }
        })

    def test_can_generate_access_token_and_refresh_token_for_username_and_password_and_then_query_api_with_filters(
            self):
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

    def test_unauthorized_requests_are_rejected_missing_header(self):
        endpoint = f'{TestConfig.API_DOMAIN}/graphql'

        response = self.app.post(endpoint, json={"query": """
                       {
                         appointments {
                           edges {
                             node {
                               startTimeUnixSeconds
                               durationSeconds
                             }
                           }
                         }
                       }
                """})

        self.assertEqual(response.json, {'errors': [
            {'message': "{'code': 'authorization_header_missing', 'description': 'Authorization header is expected'}",
             'locations': [{'line': 3, 'column': 26}], 'path': ['appointments']}], 'data': {'appointments': None}})

    def test_unauthorized_requests_are_rejected_invalid_token(self):
        endpoint = f'{TestConfig.API_DOMAIN}/graphql'

        response = self.app.post(endpoint, headers={"authorization": f"Bearer InvalidToken"}, json={"query": """
                    {
                      appointments {
                        edges {
                          node {
                            startTimeUnixSeconds
                            durationSeconds
                          }
                        }
                      }
                    }
             """})

        self.assertEqual(response.json, {'errors': [
            {'message': "{'code': 'Invalid Token', 'description': 'Your Token Could Not Be Validated'}",
             'locations': [{'line': 3, 'column': 23}], 'path': ['appointments']}], 'data': {'appointments': None}})

    def test_access_token_can_be_refreshed_and_then_the_api_queries_with_filters(self):
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

        self.assertEqual(final_request.status_code, 200)
        self.assertEqual(final_request.json, {
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
