import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType


from Spill_Backend_App.API.models import Appointment as AppointmentModel
from Spill_Backend_App.API.models import Therapist as TherapistModel
from Spill_Backend_App.API.models import Specialism as SpecialismModel

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