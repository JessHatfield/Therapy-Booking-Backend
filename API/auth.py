from functools import wraps

from flask import request
from flask_graphql_auth.decorators import _extract_header_token_value, verify_jwt_in_argument
from graphql import GraphQLError


def query_header_jwt_required(fn):
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