#generates a schema file from the schema we have setup
#Could be used as part of a CI/CD pipeline to auto update documentation with latest changes

from Spill_Backend_App.API.schema import schema

from graphql.utils import schema_printer

my_schema_str = schema_printer.print_schema(schema)
fp = open("current_api_schema.graphql", "w")
fp.write(my_schema_str)
fp.close()