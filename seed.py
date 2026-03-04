from datetime import datetime, timedelta
import random

from app import create_app
from app.extensions import db
from app.models import Admin, Certificate, Event, Mentor, Participant, Registration
from werkzeug.security import generate_password_hash


MENTORS = [
    {
        "name": "Nadia Pramesti",
        "bio": "Product designer dengan pengalaman 8 tahun di startup.",
        "photo_url": "https://cdn.shopify.com/s/files/1/0573/7569/files/hall_monitor_125_1000x.jpg?v=1724059545",
    },
    {
        "name": "Raka Aditya",
        "bio": "Backend engineer fokus cloud & scalability.",
        "photo_url": "https://cdn.shopify.com/s/files/1/0573/7569/files/hall_monitor_125_1000x.jpg?v=1724059545",
    },
    {
        "name": "Salsa Putri",
        "bio": "Data analyst, expert dashboarding dan storytelling.",
        "photo_url": "https://cdn.shopify.com/s/files/1/0573/7569/files/hall_monitor_125_1000x.jpg?v=1724059545",
    },
    {
        "name": "Bima Wicaksono",
        "bio": "DevOps & infrastructure automation.",
        "photo_url": "https://cdn.shopify.com/s/files/1/0573/7569/files/hall_monitor_125_1000x.jpg?v=1724059545",
    },
]

EVENT_TITLES = [
    "Scaling Product with MVP",
    "Career Blueprint for Tech",
    "Data Storytelling 101",
    "Cloud Fundamentals",
    "AI for Productivity",
    "Webinar: UI UX Sprint",
    "Security Basics",
    "Growth Marketing for Dev",
    "Building SaaS Prototype",
    "Startup Metrics Deep Dive",
]

PARTICIPANTS = [
    ("Alya", "alya@example.com"),
    ("Bimo", "bimo@example.com"),
    ("Citra", "citra@example.com"),
    ("Dito", "dito@example.com"),
    ("Eka", "eka@example.com"),
    ("Fajar", "jerrykesysya@gmail.com"),
    ("Gita", "gita@example.com"),
    ("Hana", "jerrykeysya@gmail.com"),
    ("Indra", "indra@example.com"),
    ("Juna", "jerrysskeysya@gmail.com"),
]


def seed():
    db.create_all()
    now = datetime.utcnow()

    if not Mentor.query.first():
        mentors = []
        for data in MENTORS:
            mentor = Mentor(**data)
            db.session.add(mentor)
            mentors.append(mentor)
        db.session.commit()
    else:
        mentors = Mentor.query.all()

    if not Event.query.first():
        for idx, title in enumerate(EVENT_TITLES):
            mentor = random.choice(mentors)
            if idx < 3:
                start_at = now - timedelta(hours=1)
                end_at = now + timedelta(hours=1)
            elif idx < 7:
                start_at = now + timedelta(days=idx)
                end_at = start_at + timedelta(hours=2)
            else:
                start_at = now - timedelta(days=idx)
                end_at = start_at + timedelta(hours=2)

            event = Event(
                title=title,
                description=(
                    "Webinar intensif ini dirancang untuk membekali peserta dengan pemahaman praktis "
                    "dan strategi implementasi di dunia nyata. Materi dibahas step-by-step, disertai "
                    "contoh kasus yang relevan serta sesi diskusi interaktif."
                ),
                objectives=(
                    "Memahami konsep inti dan terminologi penting\\n"
                    "Menganalisis studi kasus nyata\\n"
                    "Menyusun rencana implementasi sederhana\\n"
                    "Berlatih problem solving bersama mentor\\n"
                    "Mempersiapkan langkah lanjut setelah webinar"
                ),
                materials=(
                    "Slide materi lengkap\\n"
                    "Demo tools dan workflow\\n"
                    "Checklist implementasi\\n"
                    "Template dokumen pendukung\\n"
                    "Rekaman sesi (jika tersedia)"
                ),
                benefits=(
                    "Sertifikat digital resmi\\n"
                    "Akses materi dan catatan ringkas\\n"
                    "Networking dengan peserta lain\\n"
                    "Insight langsung dari mentor industri\\n"
                    "Update peluang event berikutnya"
                ),
                requirements=(
                    "Laptop/HP dengan koneksi stabil\\n"
                    "Akun Google untuk akses webinar\\n"
                    "Siapkan tools/aplikasi yang direkomendasikan\\n"
                    "Komitmen waktu sesuai jadwal\\n"
                    "Semangat belajar dan bertanya"
                ),
                agenda=(
                    "Pembukaan & perkenalan mentor\\n"
                    "Materi inti dan demo singkat\\n"
                    "Studi kasus & diskusi kelompok\\n"
                    "Sesi tanya jawab\\n"
                    "Penutup & informasi lanjutan"
                ),
                start_at=start_at,
                end_at=end_at,
                registration_deadline=start_at - timedelta(hours=2),
                duration_minutes=120,
                quota=100,
                invitation_code=f"INV{idx+1:03d}",
                mentor_id=mentor.id,
            )
            db.session.add(event)
        db.session.commit()

    if not Participant.query.first():
        for idx, (name, email) in enumerate(PARTICIPANTS, start=1):
            participant = Participant(
                participant_id=f"P-20260301-{idx:03d}",
                name=name,
                email=email,
                password_hash=generate_password_hash("user123"),
                email_verified=True,
                profile_photo_path="https://cdn.shopify.com/s/files/1/0573/7569/files/hall_monitor_125_1000x.jpg?v=1724059545",
            )
            db.session.add(participant)
        db.session.commit()

    events = Event.query.all()
    participants = Participant.query.all()

    if not Registration.query.first():
        for participant in participants:
            event = random.choice(events)
            reg = Registration(
                participant=participant,
                event=event,
                referral_code=f"REF{participant.id:04d}",
            )
            db.session.add(reg)
        db.session.commit()

        regs = Registration.query.all()
        for reg in regs:
            invited = random.choice(regs)
            if invited.id != reg.id:
                reg.invited_by_registration_id = invited.id
        db.session.commit()

    if not Certificate.query.first():
        regs = Registration.query.all()
        for reg in regs:
            cert = Certificate(
                participant_id=reg.participant_id,
                event_id=reg.event_id,
                registration_id=reg.id,
                certificate_number=f"CERT-20260301-{reg.id:04d}",
            )
            db.session.add(cert)
        db.session.commit()

    if not Admin.query.first():
        admin = Admin(
            name="Admin",
            email="admin@example.com",
            password_hash=generate_password_hash("admin123"),
            role="superadmin",
        )
        db.session.add(admin)
        db.session.commit()

    print("Seed complete.")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed()
