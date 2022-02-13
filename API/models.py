from API import db

##many specialisms can  exist
##a therapist can have many specialisms
# class Specialism
# ##Try loading this without graphene - probs an sqlalchemy error
SpecialismsForTherapists = db.Table("TherapistSpecialisms",
                                    db.Column("therapist_id", db.Integer, db.ForeignKey('therapist.therapist_id'),
                                              primary_key=True),
                                    db.Column("specialism_id", db.Integer,
                                              db.ForeignKey('specialism.specialism_id'), primary_key=True)
                                    )


# Models are defined here as per as normal just like a REST API
# SQlLite requires primary keys to be explicitly set to autoincrement https://www.sqlite.org/faq.html#q1

class Appointment(db.Model):
    __tablename__ = "Appointments"
    appointment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_time_unix_seconds = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)
    type = db.Column(db.Text)
    therapist_id=db.Column(db.Integer,db.ForeignKey('therapist.therapist_id'),nullable=True)

    def __repr__(self):
        return f"<User {self.id}>"



#Person
class Therapist(db.Model):
    ___tablename__="Therapists"
    therapist_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    appointments=db.relationship('Appointment',backref='therapists',lazy=True,primaryjoin="Appointment.therapist_id==Therapist.therapist_id")
    specialisms = db.relationship('Specialism', secondary=SpecialismsForTherapists, lazy='subquery',
                                 backref=db.backref('therapists', lazy=True))


class Specialism(db.Model):
    ___tablename__ = "Specialisms"
    specialism_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    specialism_name = db.Column(db.Text, nullable=False)
    # therapists = db.relationship('Therapist', secondary=SpecialismsForTherapists, lazy='subquery',
    #                              backref=db.backref('therapists', lazy=True))


