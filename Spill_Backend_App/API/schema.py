import logging

import graphene

from graphene_sqlalchemy_filter import FilterableConnectionField

from Spill_Backend_App.API.models import Appointment as AppointmentModel

from Spill_Backend_App.API.authentication import AuthMutation, RefreshMutation, header_must_have_jwt
from Spill_Backend_App.API.appointments.schema import AppointmentsSchema
from Spill_Backend_App.API.appointments.filters import AppointmentsFilter
from Spill_Backend_App.API.appointments.mutations import AppointmentMutation

logger = logging.getLogger(__name__)


# This file handles the creation of the graphene.Schema object which is then processed by GraphQL core and then returned
# by flask_graphql.GraphQLView
# Schema Objects, Mutation Objects and Filter Objects per domain entity (e.g appointments,authentication) are imported
# here and included in the Query and Mutation classes which then define the available queries and mutations for our API


class Mutation(graphene.ObjectType):
    auth = AuthMutation.Field()
    refresh = RefreshMutation.Field()
    appointment = AppointmentMutation.Field()


class Query(graphene.ObjectType):
    '''
    https://docs.graphene-python.org/en/latest/types/objecttypes/
    Graphene ObjectType is the building block used to define the relationship between Fields in your Schema and how their data is retrieved.
        Each attribute of an object type represents a Field
        Each Field has a resolver method to fetch data
        The resolver method name should match the field name
    '''
    node = graphene.relay.Node.Field()
    appointments = FilterableConnectionField(connection=AppointmentsSchema, filters=AppointmentsFilter(),
                                             sort=AppointmentsSchema.sort_argument())

    @staticmethod
    @header_must_have_jwt
    def resolve_appointments(parent, info, filters=None, sort=None, **kwargs):
        """
        Generates an object representing one or more appointments and returns to graphene
        :param parent: The value object returned from the resolver of the parent field
        :param info: The GraphQL execution info. Meta info about the current GraphQL Query. Per Request Context Variable
        :param kwargs: Any arguments defined in the field itself
        :return: An object representing one or more appointments
        """

        query = AppointmentModel.query
        logger.debug({"message": "Resolving Appointment Query", "query_submitted": info.context.json["query"]})
        if filters is not None:
            query = AppointmentsFilter.filter(info, query, filters)

        return query


# constructs the complete Graphql Schema
schema = graphene.Schema(query=Query, types=[AppointmentsSchema], mutation=Mutation)
