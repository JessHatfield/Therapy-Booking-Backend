def insert_api_users(db):
    from API.models import User

    test_user = User(username="test_user", email="test@test.com")
    test_user.set_password("password")
    db.session.add(test_user)
    db.session.commit()


def generate_nine_unique_appointments_for_testing_filter_combinations(db):
    """
     assuming a single value exists for each Model field there are a total of 9 different ways a filter model can differ
    :return: nine appointments which all differ from the other in one specific way - covering the full range of possible differences
    difference = at least one aspect of the appointment differs from appointment 3
    """
    from API.models import Therapist, Specialism, Appointment

    # Different Start Time
    therapist_3 = Therapist(first_name="charlie", last_name="kelly")
    specialism_3 = Specialism(specialism_name="ADHD")
    appointment_3 = Appointment(start_time_unix_seconds=0, duration_seconds=0, type="one-off")
    therapist_3.specialisms.append(specialism_3)
    appointment_3.therapists = therapist_3

    therapist_4 = Therapist(first_name="dennis", last_name="reynolds")
    specialism_4 = Specialism(specialism_name="ADHD")
    appointment_4 = Appointment(start_time_unix_seconds=1, duration_seconds=0, type="one-off")
    therapist_4.specialisms.append(specialism_4)
    appointment_4.therapists = therapist_4

    therapist_5 = Therapist(first_name="mac", last_name="mcdonald")
    specialism_5 = Specialism(specialism_name="ADHD")
    appointment_5 = Appointment(start_time_unix_seconds=2, duration_seconds=0, type="one-off")
    therapist_5.specialisms.append(specialism_5)
    appointment_5.therapists = therapist_5

    # Different specialism
    therapist_6 = Therapist(first_name="dee", last_name="reynolds")
    specialism_6 = Specialism(specialism_name="CBT")
    appointment_6 = Appointment(start_time_unix_seconds=0, duration_seconds=0, type="one-off")
    therapist_6.specialisms.append(specialism_6)
    appointment_6.therapists = therapist_6

    therapist_7 = Therapist(first_name="rickety", last_name="cricket")
    specialism_7 = Specialism(specialism_name="CBT")
    appointment_7 = Appointment(start_time_unix_seconds=0, duration_seconds=0, type="one-off")
    therapist_7.specialisms.append(specialism_7)
    appointment_7.therapists = therapist_7

    therapist_8 = Therapist(first_name="luther", last_name="vandross")
    specialism_8 = Specialism(specialism_name="CBT")
    appointment_8 = Appointment(start_time_unix_seconds=0, duration_seconds=0, type="one-off")
    therapist_8.specialisms.append(specialism_8)
    appointment_8.therapists = therapist_8

    # Different Type
    therapist_9 = Therapist(first_name="frank", last_name="reynolds")
    specialism_9 = Specialism(specialism_name="ADHD")
    appointment_9 = Appointment(start_time_unix_seconds=0, duration_seconds=0, type="consultation")
    therapist_9.specialisms.append(specialism_9)
    appointment_9.therapists = therapist_9

    therapist_10 = Therapist(first_name="bill", last_name="ponderosa")
    specialism_10 = Specialism(specialism_name="ADHD")
    appointment_10 = Appointment(start_time_unix_seconds=0, duration_seconds=0, type="consultation")
    therapist_10.specialisms.append(specialism_10)
    appointment_10.therapists = therapist_10

    therapist_11 = Therapist(first_name="doyle", last_name="mcpoyle")
    specialism_11 = Specialism(specialism_name="ADHD")
    appointment_11 = Appointment(start_time_unix_seconds=0, duration_seconds=0, type="consultation")
    therapist_11.specialisms.append(specialism_11)
    appointment_11.therapists = therapist_11

    db.session.add_all(
        [appointment_3, appointment_4, appointment_5, appointment_6, appointment_7, appointment_8, appointment_9,
         appointment_10, appointment_11])
    db.session.commit


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
    therapist_jeff.specialisms.append(addiction_specialism)
    therapist_jeff.specialisms.append(adhd_specialism)

    therapist_jane = Therapist(first_name="jane", last_name="smith")
    therapist_jane.specialisms.append(cbt_specialism)
    therapist_jane.specialisms.append(divorce_specialism)
    therapist_jane.specialisms.append(sexuality_specialism)

    appointment_sun_am.therapists = therapist_jeff
    appointment_sun_pm.therapists = therapist_jane
    db.session.add_all([appointment_sun_am, appointment_sun_pm])
    db.session.commit()


def generate_fake_data_for_development_db():
    from API import create_app, db, Config

    if input(
            f"Proceeding Will Wipe All Data In '{Config.SQLALCHEMY_DATABASE_URI}'- Do You Want To Proceed? Y/N") == "Y":
        app = create_app(Config)
        app_context = app.app_context()
        app_context.push()
        db.drop_all()
        db.create_all()
        insert_appointments_and_therapists(db)
        insert_api_users(db)

        print("Old Records Have Been Wiped And New Mock Records Created")
    else:
        print("You Did Not Select 'Y' - Exiting Function")


if __name__ == "__main__":
    generate_fake_data_for_development_db()
