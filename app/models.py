from datetime import datetime
from .extensions import db


class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(32), nullable=False, default="admin")
    api_token_hash = db.Column(db.String(64), unique=True, index=True)

    reset_tokens = db.relationship(
        "AdminResetToken", back_populates="admin", cascade="all, delete-orphan"
    )


class Mentor(db.Model):
    __tablename__ = "mentors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    bio = db.Column(db.Text)
    photo_url = db.Column(db.String(255))

    events = db.relationship("Event", back_populates="mentor")


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    objectives = db.Column(db.Text)
    materials = db.Column(db.Text)
    benefits = db.Column(db.Text)
    requirements = db.Column(db.Text)
    agenda = db.Column(db.Text)
    start_at = db.Column(db.DateTime, nullable=False)
    end_at = db.Column(db.DateTime, nullable=False)
    registration_deadline = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    quota = db.Column(db.Integer, nullable=False)
    invitation_code = db.Column(db.String(32), unique=True, index=True, nullable=False)
    meet_link = db.Column(db.String(255))
    meet_generated_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    mentor_id = db.Column(db.Integer, db.ForeignKey("mentors.id"), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey("admins.id"), nullable=True)

    mentor = db.relationship("Mentor", back_populates="events")
    registrations = db.relationship("Registration", back_populates="event", cascade="all, delete-orphan")


class Participant(db.Model):
    __tablename__ = "participants"

    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.String(64), unique=True, index=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    github_id = db.Column(db.String(64), unique=True, index=True)
    github_username = db.Column(db.String(120))
    avatar_url = db.Column(db.String(255))
    profile_photo_path = db.Column(db.String(255))
    email_verified = db.Column(db.Boolean, nullable=False, default=False)
    email_verification_token = db.Column(db.String(64), unique=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    registrations = db.relationship("Registration", back_populates="participant", cascade="all, delete-orphan")
    reset_tokens = db.relationship(
        "ParticipantResetToken", back_populates="participant", cascade="all, delete-orphan"
    )

    @property
    def has_profile_photo(self) -> bool:
        return bool(self.profile_photo_path or self.avatar_url)


class Registration(db.Model):
    __tablename__ = "registrations"

    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey("participants.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    referral_code = db.Column(db.String(32))
    invited_by_registration_id = db.Column(db.Integer, db.ForeignKey("registrations.id"))
    status = db.Column(db.String(32), nullable=False, default="pending")
    approved_at = db.Column(db.DateTime)
    approved_by_admin_id = db.Column(db.Integer, db.ForeignKey("admins.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    participant = db.relationship("Participant", back_populates="registrations")
    event = db.relationship("Event", back_populates="registrations")
    invited_by = db.relationship("Registration", remote_side=[id])
    approved_by_admin = db.relationship("Admin")
    certificate = db.relationship(
        "Certificate", back_populates="registration", uselist=False, cascade="all, delete-orphan"
    )

    @property
    def is_approved(self) -> bool:
        return self.status == "approved"


class GraduationStatus(db.Model):
    __tablename__ = "graduation_status"

    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey("participants.id"), nullable=False)
    passed = db.Column(db.Boolean, nullable=False, default=False)
    reason = db.Column(db.String(255))
    evaluated_at = db.Column(db.DateTime, default=datetime.utcnow)


class Certificate(db.Model):
    __tablename__ = "certificates"

    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey("participants.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    registration_id = db.Column(db.Integer, db.ForeignKey("registrations.id"), nullable=False)
    certificate_number = db.Column(db.String(64), unique=True, index=True, nullable=False)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    emailed_at = db.Column(db.DateTime)

    registration = db.relationship("Registration", back_populates="certificate")


class AdminResetToken(db.Model):
    __tablename__ = "admin_reset_tokens"

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("admins.id"), nullable=False)
    token_hash = db.Column(db.String(64), unique=True, index=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime)

    admin = db.relationship("Admin", back_populates="reset_tokens")


class ParticipantResetToken(db.Model):
    __tablename__ = "participant_reset_tokens"

    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey("participants.id"), nullable=False)
    token_hash = db.Column(db.String(64), unique=True, index=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime)

    participant = db.relationship("Participant", back_populates="reset_tokens")
