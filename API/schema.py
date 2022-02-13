import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from graphene_sqlalchemy_filter import FilterSet, FilterableConnectionField

from API.models import Appointment as AppointmentModel
from API.models import Therapist as TherapistModel
from API.models import Specialism as SpecialismModel

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

    @staticmethod
    def has_specialisms_filter(info, query, value):
        results = query.join(AppointmentModel.therapist).join(TherapistModel).join(SpecialismModel.therapist).filter(SpecialismModel.specialism_name=="Sexuality").all()


        filtered_appointments = query.filter(AppointmentModel.therapist.specialisms)
        typeof = type(query)

        return AppointmentModel


class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    therapists = SQLAlchemyConnectionField(TherapistsSchema.connection)
    therapy_specialism = SQLAlchemyConnectionField(SpecialismSchema.connection)
    appointments = FilterableConnectionField(connection=AppointmentsSchema, filters=AppointmentsFilter(),
                                             sort=AppointmentsSchema.sort_argument())


schema = graphene.Schema(query=Query, types=[AppointmentsSchema, TherapistsSchema, SpecialismSchema])
