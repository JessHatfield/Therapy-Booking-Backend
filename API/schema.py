
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType

from API.models import Appointment as AppointmentModel

#This file handles the definition of GraphQL Schemas and the resolving of graph querys to our underlying data model
#graphene_sqlalchemy provides helper methods to query data from SQlAlchemy
#https://github.com/graphql-python/graphene-sqlalchemy

class Appointments(SQLAlchemyObjectType):
    class Meta:
        model=AppointmentModel

class Query(graphene.ObjectType):

    appointments=graphene.List(Appointments)

    def resolve_appointments(self,info):
        query=Appointments.get_query(info)
        return query.all()



schema = graphene.Schema(query=Query)
