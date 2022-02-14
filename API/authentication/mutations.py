from API.authentication.decorators import header_must_have_jwt
from API.models import User
import graphene

from flask_graphql_auth import create_access_token, create_refresh_token, mutation_header_jwt_refresh_token_required, \
    get_jwt_identity, mutation_jwt_refresh_token_required


class AuthMutation(graphene.Mutation):
    access_token = graphene.String()
    refresh_token = graphene.String()

    class Arguments:
        username = graphene.String()
        password = graphene.String()

    def mutate(self, info, username, password):
        user = User.query.filter_by(username=username, password=password).first()
        print(user)
        if not user:
            raise Exception('Authentication Failure : username or password not valid')
        return AuthMutation(
            access_token=create_access_token(username),
            refresh_token=create_refresh_token(username)
        )


class RefreshMutation(graphene.Mutation):
    class Arguments(object):
        refresh_token = graphene.String()

    new_token = graphene.String()

    @classmethod
    @mutation_jwt_refresh_token_required
    def mutate(cls, _):
        current_user = get_jwt_identity()
        return RefreshMutation(
            new_token=create_access_token(identity=current_user),
        )