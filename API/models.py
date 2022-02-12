from API import db

#Models are defined here as per as normal just like a REST API


class Appointment(db.Model):
   __tablename__ = "Appointments"
   id = db.Column(db.Integer, primary_key=True)
   start_time_unix_seconds = db.Column(db.Integer)
   duration_seconds = db.Column(db.Integer)
   therapist_id = db.Column(db.Integer, db.ForeignKey("Therapists.id"))
   therapist = db.relationship("Therapist")
   type=db.Column(db.Text)
   specialism=db.Column(db.Text)


   def __repr__(self):
       return f"<User {self.id}>"

class Therapist(db.Model):
    __tablename__ = "Therapists"
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.Text)
