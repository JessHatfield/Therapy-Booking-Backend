import graphene
from API.models import User

from flask_graphql_auth import create_access_token, create_refresh_token, mutation_header_jwt_refresh_token_required, \
    get_jwt_identity


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
            raise Exception('Authentication Failure : User is not registered')
        return AuthMutation(
            access_token=create_access_token(username),
            refresh_token=create_refresh_token(username)
        )


class RefreshMutation(graphene.Mutation):
    class Arguments(object):
        pass

    new_token = graphene.String()

    @classmethod
    @mutation_header_jwt_refresh_token_required
    def mutate(cls, _):
        current_user = get_jwt_identity()
        return RefreshMutation(
            new_token=create_access_token(identity=current_user),
        )


class Mutation(graphene.ObjectType):
    auth = AuthMutation.Field()
    refresh = RefreshMutation.Field()
