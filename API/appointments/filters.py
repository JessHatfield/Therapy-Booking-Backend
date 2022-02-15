import graphene
from graphene_sqlalchemy_filter import FilterSet

from API.models import Appointment as AppointmentModel
from API.models import Therapist as TherapistModel
from API.models import Specialism as SpecialismModel
from sqlalchemy import and_


class AppointmentsFilter(FilterSet):
    # Available Operations = ['eq', 'ne', 'like', 'ilike', 'is_null', 'in', 'not_in', 'lt', 'lte', 'gt', 'gte', 'range']
    # details on each filter operation can be found here
    # https://github.com/art1415926535/graphene-sqlalchemy-filter#automatically-generated-filters
    has_specialisms = graphene.List(of_type=graphene.String)

    class Meta:
        model = AppointmentModel
        fields = {
            'start_time_unix_seconds': ['range'],
            'type': ['eq'],
        }

    @classmethod
    def has_specialisms_filter(cls, info, query, value):
        therapists = cls.aliased(query, TherapistModel, name='member_of')
        specialisms = cls.aliased(query, SpecialismModel, name="specialism_of")

        query = query.join(therapists, and_(AppointmentModel.therapist_id == therapists.therapist_id, )).join(
            specialisms, therapists.specialisms)

        return query, specialisms.specialism_name.in_(value)
