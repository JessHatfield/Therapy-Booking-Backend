from functools import wraps

import flask
from flask import request
from flask_graphql_auth.decorators import verify_jwt_in_argument, _extract_header_token_value
from graphql import GraphQLError
import logging

logger=logging.getLogger(__name__)

def get_token_auth_header(auth_header):
    """

    :param auth_header: str the authentication header returned from the request
    :return: the jwt token extracted from the authentication header
    """
    if not auth_header:
        raise GraphQLError({"code": "authorization_header_missing",
                            "description":
                                "Authorization header is expected"}, 401)

    parts = auth_header.split()

    if parts[0].lower() != "bearer":
        raise GraphQLError({"code": "invalid_header",
                            "description":
                                "Authorization header must start with"
                                " Bearer"}, 401)
    elif len(parts) == 1:
        raise GraphQLError({"code": "invalid_header",
                            "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise GraphQLError({"code": "invalid_header",
                            "description":
                                "Authorization header must be"
                                " Bearer token"}, 401)

    token = parts[1]
    return token


def header_must_have_jwt(fn):
    """
    A decorator to protect a query resolver.

    If you decorate an resolver with this, it will ensure that the requester
    has a valid access token before allowing the resolver to be called. This
    does not check the freshness of the access token.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):

        token = get_token_auth_header(request.headers.get("Authorization", None))

        try:
            verify_jwt_in_argument(token)
        except Exception as e:

            logger.error({"messages":"Token Decoding Error","error message":e})

            raise GraphQLError({"code": "Invalid Token",
                                "description":
                                    "Your Token Could Not Be Validated"
                                }, 401)

        return fn(*args, **kwargs)

    return wrapper
