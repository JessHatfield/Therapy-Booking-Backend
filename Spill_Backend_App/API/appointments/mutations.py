import graphene
import logging
from Spill_Backend_App.API import db
from Spill_Backend_App.API.authentication import header_must_have_jwt
from Spill_Backend_App.API.models import Appointment as AppointmentModel
from Spill_Backend_App.API.appointments.schema import AppointmentsSchema

logger = logging.getLogger(__name__)


class AppointmentMutation(graphene.Mutation):
    appointment = graphene.Field(AppointmentsSchema)

    class Arguments:
        therapist_id = graphene.Int()
        start_time_unix_seconds = graphene.Int()
        duration_seconds = graphene.Int()
        type = graphene.String()

    @header_must_have_jwt
    def mutate(self, info, therapist_id, start_time_unix_seconds, duration_seconds, type):
        """
        Creates a new appointment for a given therapist. AppointmentMutation is IDEMPOTENT. The exact same appointment cannot be created twice
        :param info: The GraphQL execution info. Meta info about the current GraphQL Query. Per Request Context Variable
        :param therapist_id: Integer - ID For the Therapist For Appointment
        :param start_time_unix_seconds: Integer
        :param duration_seconds: Integer
        :param type: Str - "one-off" or "consulting"
        :return: AppointmentMutation
        """

        appointment = AppointmentModel.query.filter_by(therapist_id=therapist_id,
                                                       start_time_unix_seconds=start_time_unix_seconds,
                                                       duration_seconds=duration_seconds, type=type).first()
        if appointment:
            logger.info(f"Returned Existing Appointment {appointment}")
            logger.debug({"message": "Returning Mutation", "mutation_submitted": info.context.json["query"],
                          "appointment_returned": appointment})
            return AppointmentMutation(appointment=appointment)

        if not appointment:
            appointment = AppointmentModel(therapist_id=therapist_id, start_time_unix_seconds=start_time_unix_seconds,
                                           duration_seconds=duration_seconds, type=type)
            db.session.add(appointment)
            db.session.commit()
        logger.info(f"Created New Appointment {appointment}")
        logger.debug({"message": "Returning Mutation", "mutation_submitted": info.context.json["query"],
                      "appointment_returned": appointment})
        return AppointmentMutation(appointment=appointment)
