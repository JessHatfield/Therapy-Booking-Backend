import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphene_sqlalchemy_filter import FilterSet, FilterableConnectionField

from API.auth import query_header_jwt_required
from API.models import Appointment as AppointmentModel
from API.models import Therapist as TherapistModel
from API.models import Specialism as SpecialismModel
from sqlalchemy import and_
from API.mutations import Mutation


from functools import wraps


# This file handles the definition of GraphQL Schemas and the resolving of graph querys to our underlying data model
# graphene_sqlalchemy provides helper methods to query data from SQlAlchemy
# https://github.com/graphql-python/graphene-sqlalchemy

# full list of available filter operations can be found here
# https://github.com/art1415926535/graphene-sqlalchemy-filter#automatically-generated-filters
ALL_OPERATIONS = ['eq', 'ne', 'like', 'ilike', 'is_null', 'in', 'not_in', 'lt', 'lte', 'gt', 'gte', 'range']


class AppointmentsSchema(SQLAlchemyObjectType):
    class Meta:
        model = AppointmentModel
        interfaces = (graphene.relay.Node,)


class TherapistsSchema(SQLAlchemyObjectType):
    class Meta:
        model = TherapistModel
        interfaces = (graphene.relay.Node,)


class SpecialismSchema(SQLAlchemyObjectType):
    class Meta:
        model = SpecialismModel
        interfaces = (graphene.relay.Node,)


class SpecialismFilter(FilterSet):
    class Meta:
        model = AppointmentModel
        fields = {
            'specialism_name': ALL_OPERATIONS,
        }


class AppointmentsFilter(FilterSet):
    has_specialisms = graphene.List(of_type=graphene.String)

    class Meta:
        model = AppointmentModel
        fields = {
            'appointment_id': ALL_OPERATIONS,
            'start_time_unix_seconds': ALL_OPERATIONS,
            'duration_seconds': ALL_OPERATIONS,
            'therapist_id': ALL_OPERATIONS,
            'type': ALL_OPERATIONS,
        }

    @classmethod
    def has_specialisms_filter(cls, info, query, value):
        therapists = cls.aliased(query, TherapistModel, name='member_of')
        specialisms = cls.aliased(query, SpecialismModel, name="specialism_of")

        query = query.join(therapists, and_(AppointmentModel.therapist_id == therapists.therapist_id, )).join(
            specialisms, therapists.specialisms)

        return query, specialisms.specialism_name.in_(value)


class MessageField(graphene.ObjectType):
    message = graphene.String()


class ErrorType(graphene.Scalar):
    @staticmethod
    def serialize(errors):
        if isinstance(errors, dict):
            if errors.get("__all__", False):
                errors["non_field_errors"] = errors.pop("__all__")
            return errors
        raise Exception("`errors` should be dict!")




class Query(graphene.ObjectType):
    '''
    https://docs.graphene-python.org/en/latest/types/objecttypes/
    Graphene ObjectType is the building block used to define the relationship between Fields in your Schema and how their data is retrieved.
        Each attribute of an object type represents a Field
        Each Field has a resolver method to fetch data
        The resolver method name should match the field name
    '''
    node = graphene.relay.Node.Field()
    errors=graphene.Field(ErrorType)
    appointments = FilterableConnectionField(connection=AppointmentsSchema, filters=AppointmentsFilter(),
                                         sort=AppointmentsSchema.sort_argument())


    @staticmethod
    @query_header_jwt_required
    def resolve_appointments(parent, info, **kwargs):
        """
        Generates an object representing one or more appointments and returns to graphene
        :param parent: The value object returned from the resolver of the parent field
        :param info: The GraphQL execution info. Meta info about the current GraphQL Query. Per Request Context Variable
        :param kwargs: Any arguments defined in the field itself
        :return: An object representing one or more appointments
        """
        return FilterableConnectionField(connection=AppointmentsSchema, filters=AppointmentsFilter(),
                                         sort=AppointmentsSchema.sort_argument()).get_query(AppointmentModel, info)


# flask-graphql-auth checks for jwt in header when the resolver function is run
# before the resolver function is run the decorator is executed
# the decorated function extracts the token from the Flask Request variable
# if the headers are found the decorator allows the resolver function to continue
# if it fails to auth it returns an AuthInfoField instead of the data which was to be resolved


# constructs the complete Graphql Schema
schema = graphene.Schema(query=Query, types=[AppointmentsSchema], mutation=Mutation)
