import unittest

from graphql import GraphQLError

from API.authentication.decorators import get_token_auth_header


class Auth_Tests(unittest.TestCase):

    def test_get_token_auth_header_valid_input(self):
        auth = "Bearer eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL2Rldi12bS1vZTZmZS5ldS5hdXRoMC5jb20vIiwic3ViIjoiZ29vZ2xlLW9hdXRoMnx0aGlzaXNhZmFrZWFjY291bnRpZCIsImF1ZCI6WyJodHRwczovY3JlYXRpdmVfYXBwcm92YWxzX3Rvb2wvYXBpIiwiaHR0cHM6Ly9kZXYtdm0tb2U2ZmUuZXUuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTYxNTk4ODQ5OSwiZXhwIjoxNjE2MDc0ODk5LCJhenAiOiJaY0NmanNDUGtFTDcyb1ZxRGw1eTNDQXJpQUpyb1R2eSIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwifQ.p0c6YpqWlw9EzM9gCMlemWX_3nh5Pg-Hy3fuSpkpOEI"
        token = get_token_auth_header(auth)
        self.assertEqual(token,
                         "eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL2Rldi12bS1vZTZmZS5ldS5hdXRoMC5jb20vIiwic3ViIjoiZ29vZ2xlLW9hdXRoMnx0aGlzaXNhZmFrZWFjY291bnRpZCIsImF1ZCI6WyJodHRwczovY3JlYXRpdmVfYXBwcm92YWxzX3Rvb2wvYXBpIiwiaHR0cHM6Ly9kZXYtdm0tb2U2ZmUuZXUuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTYxNTk4ODQ5OSwiZXhwIjoxNjE2MDc0ODk5LCJhenAiOiJaY0NmanNDUGtFTDcyb1ZxRGw1eTNDQXJpQUpyb1R2eSIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwifQ.p0c6YpqWlw9EzM9gCMlemWX_3nh5Pg-Hy3fuSpkpOEI")

    def test_get_token_auth_header_invalid_header(self):
        auth = "sdfkhfsajkfhjsdahfj"
        self.assertRaises(GraphQLError, get_token_auth_header, auth)

    # def test_get_account_id_ideal_input(self):
    #     auth = "Bearer eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL2Rldi12bS1vZTZmZS5ldS5hdXRoMC5jb20vIiwic3ViIjoiZ29vZ2xlLW9hdXRoMnx0aGlzaXNhZmFrZWFjY291bnRpZCIsImF1ZCI6WyJodHRwczovY3JlYXRpdmVfYXBwcm92YWxzX3Rvb2wvYXBpIiwiaHR0cHM6Ly9kZXYtdm0tb2U2ZmUuZXUuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTYxNTk4ODQ5OSwiZXhwIjoxNjE2MDc0ODk5LCJhenAiOiJaY0NmanNDUGtFTDcyb1ZxRGw1eTNDQXJpQUpyb1R2eSIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwifQ.p0c6YpqWlw9EzM9gCMlemWX_3nh5Pg-Hy3fuSpkpOEI"
    #     user_sub = get_account_id(auth)
    #     self.assertEqual(user_sub, "google-oauth2|thisisafakeaccountid")
    #
    # def test_get_account_id_no_account_id_present_input(self):
    #     auth = "Bearer eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL2Rldi12bS1vZTZmZS5ldS5hdXRoMC5jb20vIiwiYXVkIjpbImh0dHBzOi9jcmVhdGl2ZV9hcHByb3ZhbHNfdG9vbC9hcGkiLCJodHRwczovL2Rldi12bS1vZTZmZS5ldS5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNjE1OTg4NDk5LCJleHAiOjE2MTYwNzQ4OTksImF6cCI6IlpjQ2Zqc0NQa0VMNzJvVnFEbDV5M0NBcmlBSnJvVHZ5Iiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCJ9.1vXv27j3AzSu8EeIQtrHwJMi_dmePG0bpWW_PVX6zSY"
    #     self.assertRaises(KeyError, get_account_id, auth)