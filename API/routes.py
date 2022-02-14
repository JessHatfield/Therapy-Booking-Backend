from flask import Blueprint
from flask_graphql import GraphQLView
from API.schema import schema

bp = Blueprint('main', __name__)



##flask_graphql is a helper library using GraphQL-Server which itself uses GraphQL-core the python implementation of GraphQL
##It handles the parsing of SDL sent to our API passes it to our graphene schema object for querying and returns the results

bp.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True  # for having the GraphiQL interface
    )
)

