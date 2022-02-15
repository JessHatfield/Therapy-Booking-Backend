from functools import wraps

import flask
from flask import request
from flask_graphql_auth.decorators import verify_jwt_in_argument, _extract_header_token_value
from graphql import GraphQLError


def header_must_have_jwt(fn):
    """
    A decorator to protect a query resolver.

    If you decorate an resolver with this, it will ensure that the requester
    has a valid access token before allowing the resolver to be called. This
    does not check the freshness of the access token.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):

        token = _extract_header_token_value(request.headers)

        try:
            verify_jwt_in_argument(token)
        except Exception as e:
            raise GraphQLError(e)

        return fn(*args, **kwargs)

    return wrapper
