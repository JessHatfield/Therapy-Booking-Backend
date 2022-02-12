from flask import Flask
from config import Config
from flask_graphql import GraphQLView
import API
from API.schema import schema

app = API.create_app(config_class=Config)

##flask_graphql is a helper library using GraphQL-Server which itself uses GraphQL-core the python implementation of GraphQL
##It handles the parsing of SDL sent to our API passes it to our graphene schema object for querying and returns the results
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True  # for having the GraphiQL interface
    )
)

if __name__ == "__main__":
    app.run()
