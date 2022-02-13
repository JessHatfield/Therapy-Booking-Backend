
def insert_appointments_and_therapists(db):
    from API.models import Appointment, Therapist, Specialism

    # 1644747572 = Sun Feb 13th 2022 - 10:19:32
    appointment_sun_am = Appointment(start_time_unix_seconds=1644747572, duration_seconds=3600, type="one-off",
                                     )

    # 1644751572 = Sun Feb 13th 2022 - 19:20:12
    appointment_sun_pm = Appointment(start_time_unix_seconds=1644780000, duration_seconds=3600, type="consultation",
                                     )

    addiction_specialism = Specialism(specialism_name="Addiction")
    adhd_specialism = Specialism(specialism_name="ADHD")
    cbt_specialism = Specialism(specialism_name="CBT")
    divorce_specialism = Specialism(specialism_name="Divorce")
    sexuality_specialism = Specialism(specialism_name="Sexuality")

    therapist_jeff = Therapist(first_name="jeff", last_name="smith")
    therapist_jeff.specialisms = [addiction_specialism, adhd_specialism]

    therapist_jane = Therapist(first_name="jane", last_name="smith")
    therapist_jane.specialisms = [cbt_specialism, divorce_specialism, sexuality_specialism]

    appointment_sun_am.therapist = therapist_jeff
    appointment_sun_pm.therapist = therapist_jane
    db.session.add_all([appointment_sun_am, appointment_sun_pm])
    db.session.commit()



def generate_fake_data_for_development_db():



    from API import create_app, db, Config

    if input(f"Proceeding Will Wipe All Data In '{Config.SQLALCHEMY_DATABASE_URI}'- Do You Want To Proceed? Y/N" )=="Y":
        app = create_app(Config)
        app_context = app.app_context()
        app_context.push()
        db.drop_all()
        db.create_all()
        insert_appointments_and_therapists(db)
        print("Old Records Have Been Wiped And New Mock Records Created")
    else:
        print("You Did Not Select 'Y' - Exiting Function")



if __name__=="__main__":
    generate_fake_data_for_development_db()
