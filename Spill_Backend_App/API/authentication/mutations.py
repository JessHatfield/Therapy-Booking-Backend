from Spill_Backend_App.API.models import User
import graphene

from flask_graphql_auth import create_access_token, create_refresh_token, mutation_header_jwt_refresh_token_required, \
    get_jwt_identity, mutation_jwt_refresh_token_required
import logging

logger = logging.getLogger(__name__)


class AuthMutation(graphene.Mutation):
    access_token = graphene.String()
    refresh_token = graphene.String()

    class Arguments:
        username = graphene.String()
        password = graphene.String()

    def mutate(self, info, username, password):
        # username is a unique constraint in our model
        user = User.query.filter_by(username=username).first()
        user_password_matches = user.check_password(password=password)
        if not user or not user_password_matches:
            raise Exception('Authentication Failure : username or password not valid')

        logger.debug({"message": "Generated New Access + Refresh Token",
                      "user": user})

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

        logger.debug({"message": "Refreshed Access Token",
                      "user": current_user})
        return RefreshMutation(
            new_token=create_access_token(identity=current_user),
        )
