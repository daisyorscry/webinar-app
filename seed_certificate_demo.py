from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import Certificate, Event, Mentor, Participant, Registration


def main():
    app = create_app()
    with app.app_context():
        mentor = Mentor.query.filter_by(name="Demo Mentor Certificate").first()
        if not mentor:
            mentor = Mentor(
                name="Demo Mentor Certificate",
                bio="Mentor demo untuk preview sertifikat.",
                photo_url="https://cdn.shopify.com/s/files/1/0573/7569/files/hall_monitor_125_1000x.jpg?v=1724059545",
            )
            db.session.add(mentor)
            db.session.flush()

        participant = Participant.query.filter_by(email="certificate-demo@example.com").first()
        if not participant:
            participant = Participant(
                participant_id="P-DEMO-CERT-001",
                name="Certificate Demo User",
                email="certificate-demo@example.com",
                password_hash=generate_password_hash("demo12345"),
                email_verified=True,
                profile_photo_path="https://cdn.shopify.com/s/files/1/0573/7569/files/hall_monitor_125_1000x.jpg?v=1724059545",
            )
            db.session.add(participant)
            db.session.flush()

        event = Event.query.filter_by(title="Demo Certificate Event").first()
        if not event:
            end_at = datetime.utcnow() - timedelta(days=1)
            start_at = end_at - timedelta(hours=2)
            event = Event(
                title="Demo Certificate Event",
                description="Event demo untuk menampilkan preview sertifikat.",
                start_at=start_at,
                end_at=end_at,
                registration_deadline=start_at - timedelta(days=1),
                duration_minutes=120,
                quota=50,
                invitation_code="DEMO-CERT-EVT",
                mentor_id=mentor.id,
            )
            db.session.add(event)
            db.session.flush()

        registration = Registration.query.filter_by(participant_id=participant.id, event_id=event.id).first()
        if not registration:
            registration = Registration(
                participant_id=participant.id,
                event_id=event.id,
                referral_code="DEMO-CERT-REF",
                status="approved",
                approved_at=datetime.utcnow() - timedelta(hours=12),
            )
            db.session.add(registration)
            db.session.flush()

        certificate = Certificate.query.filter_by(registration_id=registration.id).first()
        if not certificate:
            certificate = Certificate(
                participant_id=participant.id,
                event_id=event.id,
                registration_id=registration.id,
                certificate_number="CERT-DEMO-20260304",
                issued_at=datetime.utcnow() - timedelta(hours=1),
                emailed_at=datetime.utcnow() - timedelta(minutes=30),
            )
            db.session.add(certificate)

        db.session.commit()

        print("Demo certificate seed ready")
        print(f"Registration ID: {registration.id}")
        print(f"Certificate Number: {certificate.certificate_number}")
        print(f"Preview URL: /certificates/{certificate.certificate_number}")
        print(f"Download URL: /certificates/{certificate.certificate_number}/download")


if __name__ == "__main__":
    main()
