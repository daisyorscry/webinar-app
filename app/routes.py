from datetime import datetime, timedelta
from uuid import uuid4
import os
import csv
from io import StringIO
from flask import Blueprint, flash, redirect, render_template, request, session, url_for, Response, current_app, has_request_context
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from .auth import admin_required, user_required
from .extensions import db, oauth
from .models import Admin, Certificate, Event, Mentor, Participant, ParticipantResetToken, Registration
from .security import generate_token, hash_token, token_expiry
from .services.email import send_registration_approved_email

bp = Blueprint("main", __name__)


@bp.app_context_processor
def inject_user_sidebar_registrations():
    if not has_request_context():
        return {"sidebar_registrations": []}

    participant_id = session.get("participant_id")
    if not participant_id:
        return {"sidebar_registrations": []}

    now = datetime.utcnow()
    sidebar_registrations = (
        Registration.query.join(Event, Registration.event_id == Event.id)
        .filter(Registration.participant_id == participant_id)
        .filter(Event.end_at >= now)
        .order_by(Event.start_at.asc())
        .limit(5)
        .all()
    )
    return {"sidebar_registrations": sidebar_registrations}


def _generate_invitation_code() -> str:
    return uuid4().hex[:8].upper()


def _generate_certificate_number() -> str:
    date_part = datetime.utcnow().strftime("%Y%m%d")
    rand_part = uuid4().hex[:6].upper()
    return f"CERT-{date_part}-{rand_part}"


def _generate_participant_id() -> str:
    date_part = datetime.utcnow().strftime("%Y%m%d")
    rand_part = uuid4().hex[:6].upper()
    return f"P-{date_part}-{rand_part}"


def _allowed_image(filename: str) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in current_app.config.get("ALLOWED_IMAGE_EXTENSIONS", set())


def _generate_meet_code() -> str:
    raw = uuid4().hex[:10].lower()
    return f"{raw[:3]}-{raw[3:7]}-{raw[7:]}"


def _maybe_generate_meet_link(event: Event) -> bool:
    if event.meet_link:
        return False
    now = datetime.utcnow()
    if now >= event.start_at.replace(tzinfo=None) - timedelta(minutes=15):
        event.meet_link = f"https://meet.google.com/{_generate_meet_code()}"
        event.meet_generated_at = now
        return True
    return False


@bp.route("/")
def home():
    now = datetime.utcnow()
    active_events = Event.query.filter(Event.start_at <= now, Event.end_at >= now).order_by(Event.start_at).all()
    upcoming_events = Event.query.filter(Event.start_at > now).order_by(Event.start_at).all()
    past_events = Event.query.filter(Event.end_at < now).order_by(Event.end_at.desc()).limit(6).all()
    return render_template(
        "home.html",
        active_events=active_events,
        upcoming_events=upcoming_events,
        past_events=past_events,
    )


@bp.route("/events/<int:event_id>")
def event_detail(event_id: int):
    event = Event.query.get_or_404(event_id)
    if _maybe_generate_meet_link(event):
        db.session.commit()
    referral = request.args.get("ref")
    registered_count = Registration.query.filter_by(event_id=event.id, status="approved").count()
    remaining_quota = max(event.quota - registered_count, 0)
    existing_registration = None
    participant_session_id = session.get("participant_id")
    if participant_session_id:
        existing_registration = Registration.query.filter_by(
            event_id=event.id,
            participant_id=participant_session_id,
        ).first()
    return render_template(
        "event_detail.html",
        event=event,
        referral=referral,
        now=datetime.utcnow(),
        registered_count=registered_count,
        remaining_quota=remaining_quota,
        existing_registration=existing_registration,
    )


@bp.route("/events/<int:event_id>/register", methods=["POST"])
def event_register(event_id: int):
    event = Event.query.get_or_404(event_id)
    now = datetime.utcnow()

    if now > event.registration_deadline:
        flash("Pendaftaran sudah ditutup.", "error")
        return redirect(url_for("main.event_detail", event_id=event_id))

    current_count = Registration.query.filter_by(event_id=event.id, status="approved").count()
    if current_count >= event.quota:
        flash("Kuota sudah penuh.", "error")
        return redirect(url_for("main.event_detail", event_id=event_id))

    participant_session_id = session.get("participant_id")
    if not participant_session_id:
        flash("Silakan login untuk mendaftar event.", "error")
        return redirect(url_for("main.user_login"))

    participant = Participant.query.get_or_404(participant_session_id)
    if not participant.email_verified:
        flash("Verifikasi email dulu sebelum daftar event.", "error")
        return redirect(url_for("main.user_profile"))
    if not participant.has_profile_photo:
        flash("Upload foto profil dulu sebelum daftar event.", "error")
        return redirect(url_for("main.user_profile"))
    referral_code = request.form.get("referral_code", "").strip().upper() or None

    existing = Registration.query.filter_by(participant=participant, event=event).first()
    if existing:
        if existing.status == "pending":
            flash("Pendaftaran kamu sedang menunggu approval admin.", "error")
        else:
            flash("Anda sudah terdaftar untuk event ini.", "error")
        return redirect(url_for("main.event_detail", event_id=event_id))

    invited_by = None
    if referral_code:
        invited_by = Registration.query.filter_by(
            referral_code=referral_code,
            event=event,
            status="approved",
        ).first()

    registration = Registration(
        participant=participant,
        event=event,
        referral_code=_generate_invitation_code(),
        invited_by=invited_by,
        status="pending",
    )
    db.session.add(registration)
    db.session.commit()

    flash("Permintaan pendaftaran berhasil dikirim. Tunggu approval dari admin.", "success")
    return redirect(url_for("main.registration_success", registration_id=registration.id))


@bp.route("/registrations/<int:registration_id>")
def registration_success(registration_id: int):
    registration = Registration.query.get_or_404(registration_id)
    return render_template("registration_success.html", registration=registration)


@bp.route("/invite/<code>")
def invitation(code: str):
    registration = Registration.query.filter_by(referral_code=code.upper(), status="approved").first_or_404()
    return redirect(url_for("main.event_detail", event_id=registration.event_id, ref=code.upper()))


@bp.route("/admin")
@admin_required()
def admin_dashboard():
    events = Event.query.order_by(Event.start_at.desc()).all()
    mentors = Mentor.query.order_by(Mentor.name).all()
    total_events = Event.query.count()
    total_participants = Participant.query.count()
    total_registrations = Registration.query.count()
    top_referrers = (
        db.session.query(Registration.invited_by_registration_id, db.func.count(Registration.id))
        .filter(Registration.invited_by_registration_id.isnot(None))
        .group_by(Registration.invited_by_registration_id)
        .order_by(db.func.count(Registration.id).desc())
        .limit(5)
        .all()
    )
    top_referral_regs = [
        (Registration.query.get(reg_id), count) for reg_id, count in top_referrers
    ]
    return render_template(
        "admin_dashboard.html",
        events=events,
        mentors=mentors,
        total_events=total_events,
        total_participants=total_participants,
        total_registrations=total_registrations,
        top_referral_regs=top_referral_regs,
        api_token=session.pop("new_api_token", None),
    )


@bp.route("/admin/events/new", methods=["GET", "POST"])
@admin_required()
def admin_create_event():
    mentors = Mentor.query.order_by(Mentor.name).all()
    if request.method == "GET":
        return render_template("admin_event_form.html", mentors=mentors)

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    objectives = request.form.get("objectives", "").strip()
    materials = request.form.get("materials", "").strip()
    benefits = request.form.get("benefits", "").strip()
    requirements = request.form.get("requirements", "").strip()
    agenda = request.form.get("agenda", "").strip()
    mentor_id = request.form.get("mentor_id")
    quota = request.form.get("quota")
    duration_minutes = request.form.get("duration_minutes")
    start_at = request.form.get("start_at")
    end_at = request.form.get("end_at")
    registration_deadline = request.form.get("registration_deadline")

    if not all([title, mentor_id, quota, duration_minutes, start_at, end_at, registration_deadline]):
        flash("Semua field wajib diisi.", "error")
        return redirect(url_for("main.admin_create_event"))

    try:
        event = Event(
            title=title,
            description=description,
            objectives=objectives,
            materials=materials,
            benefits=benefits,
            requirements=requirements,
            agenda=agenda,
            mentor_id=int(mentor_id),
            quota=int(quota),
            duration_minutes=int(duration_minutes),
            start_at=datetime.fromisoformat(start_at),
            end_at=datetime.fromisoformat(end_at),
            registration_deadline=datetime.fromisoformat(registration_deadline),
            invitation_code=_generate_invitation_code(),
        )
    except ValueError:
        flash("Format tanggal tidak valid.", "error")
        return redirect(url_for("main.admin_create_event"))

    db.session.add(event)
    db.session.commit()
    flash("Event berhasil dibuat.", "success")
    return redirect(url_for("main.admin_dashboard"))


@bp.route("/admin/events/<int:event_id>/edit", methods=["GET", "POST"])
@admin_required()
def admin_edit_event(event_id: int):
    event = Event.query.get_or_404(event_id)
    mentors = Mentor.query.order_by(Mentor.name).all()
    if request.method == "GET":
        return render_template("admin_event_form.html", mentors=mentors, event=event)

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    objectives = request.form.get("objectives", "").strip()
    materials = request.form.get("materials", "").strip()
    benefits = request.form.get("benefits", "").strip()
    requirements = request.form.get("requirements", "").strip()
    agenda = request.form.get("agenda", "").strip()
    mentor_id = request.form.get("mentor_id")
    quota = request.form.get("quota")
    duration_minutes = request.form.get("duration_minutes")
    start_at = request.form.get("start_at")
    end_at = request.form.get("end_at")
    registration_deadline = request.form.get("registration_deadline")

    if not all([title, mentor_id, quota, duration_minutes, start_at, end_at, registration_deadline]):
        flash("Semua field wajib diisi.", "error")
        return redirect(url_for("main.admin_edit_event", event_id=event.id))

    try:
        event.title = title
        event.description = description
        event.objectives = objectives
        event.materials = materials
        event.benefits = benefits
        event.requirements = requirements
        event.agenda = agenda
        event.mentor_id = int(mentor_id)
        event.quota = int(quota)
        event.duration_minutes = int(duration_minutes)
        event.start_at = datetime.fromisoformat(start_at)
        event.end_at = datetime.fromisoformat(end_at)
        event.registration_deadline = datetime.fromisoformat(registration_deadline)
    except ValueError:
        flash("Format tanggal tidak valid.", "error")
        return redirect(url_for("main.admin_edit_event", event_id=event.id))

    db.session.commit()
    flash("Event berhasil diperbarui.", "success")
    return redirect(url_for("main.admin_events"))


@bp.route("/admin/events/<int:event_id>/delete", methods=["POST"])
@admin_required()
def admin_delete_event(event_id: int):
    event = Event.query.get_or_404(event_id)
    Registration.query.filter_by(event_id=event.id).update(
        {Registration.invited_by_registration_id: None},
        synchronize_session=False,
    )
    db.session.delete(event)
    db.session.commit()
    flash("Event berhasil dihapus.", "success")
    return redirect(url_for("main.admin_events"))


@bp.route("/admin/mentors/new", methods=["GET", "POST"])
@admin_required()
def admin_create_mentor():
    if request.method == "GET":
        return render_template("admin_mentor_form.html")

    name = request.form.get("name", "").strip()
    bio = request.form.get("bio", "").strip()
    photo_url = request.form.get("photo_url", "").strip()

    if not name:
        flash("Nama mentor wajib diisi.", "error")
        return redirect(url_for("main.admin_create_mentor"))

    mentor = Mentor(name=name, bio=bio, photo_url=photo_url)
    db.session.add(mentor)
    db.session.commit()
    flash("Mentor berhasil ditambahkan.", "success")
    return redirect(url_for("main.admin_dashboard"))


@bp.route("/admin/mentors")
@admin_required()
def admin_mentors():
    q = request.args.get("q", "").strip()
    query = Mentor.query.order_by(Mentor.name)

    if q:
        like_value = f"%{q}%"
        query = query.filter(
            db.or_(
                Mentor.name.ilike(like_value),
                Mentor.bio.ilike(like_value),
            )
        )

    mentors = query.all()
    return render_template("admin_mentors.html", mentors=mentors, filters={"q": q})


@bp.route("/admin/approvals")
@admin_required()
def admin_approvals():
    pending_approvals = (
        Registration.query.join(Event, Registration.event_id == Event.id)
        .filter(Registration.status == "pending")
        .order_by(Registration.created_at.desc())
        .all()
    )
    return render_template("admin_approvals.html", pending_approvals=pending_approvals)


@bp.route("/admin/events/<int:event_id>/registrations")
@admin_required()
def admin_event_registrations(event_id: int):
    event = Event.query.get_or_404(event_id)
    registrations = Registration.query.filter_by(event_id=event_id).order_by(Registration.created_at.desc()).all()
    return render_template("admin_registrations.html", event=event, registrations=registrations)


@bp.route("/admin/registrations/<int:registration_id>/approve", methods=["POST"])
@admin_required()
def admin_approve_registration(registration_id: int):
    registration = Registration.query.get_or_404(registration_id)
    if registration.status == "approved":
        flash("Pendaftar ini sudah di-approve.", "error")
        return redirect(url_for("main.admin_event_registrations", event_id=registration.event_id))

    approved_count = Registration.query.filter_by(event_id=registration.event_id, status="approved").count()
    if approved_count >= registration.event.quota:
        flash("Kuota event sudah penuh. Tidak bisa approve pendaftar baru.", "error")
        return redirect(url_for("main.admin_event_registrations", event_id=registration.event_id))

    registration.status = "approved"
    registration.approved_at = datetime.utcnow()
    registration.approved_by_admin_id = session.get("admin_id")

    if not registration.certificate:
        db.session.add(
            Certificate(
                participant_id=registration.participant_id,
                event_id=registration.event_id,
                registration=registration,
                certificate_number=_generate_certificate_number(),
            )
        )

    db.session.commit()

    email_sent = send_registration_approved_email(registration)
    if email_sent:
        flash("Pendaftar berhasil di-approve dan email notifikasi sudah dikirim.", "success")
    else:
        flash("Pendaftar berhasil di-approve, tapi email notifikasi belum terkirim.", "success")
    return redirect(url_for("main.admin_event_registrations", event_id=registration.event_id))


@bp.route("/admin/events/<int:event_id>/meet-generate", methods=["POST"])
@admin_required()
def admin_generate_meet(event_id: int):
    event = Event.query.get_or_404(event_id)
    now = datetime.utcnow()
    if now < event.start_at.replace(tzinfo=None) - timedelta(minutes=15):
        flash("Link webinar bisa dibuat 15 menit sebelum mulai.", "error")
        return redirect(url_for("main.admin_dashboard"))
    if not event.meet_link:
        event.meet_link = f"https://meet.google.com/{_generate_meet_code()}"
        event.meet_generated_at = now
        db.session.commit()
        flash("Link webinar berhasil dibuat.", "success")
    return redirect(url_for("main.admin_dashboard"))


@bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        return redirect(url_for("main.user_login"))
    return redirect(url_for("main.user_login"))


@bp.route("/admin/logout")
def admin_logout():
    session.pop("admin_id", None)
    flash("Logout berhasil.", "success")
    return redirect(url_for("main.home"))


@bp.route("/admin/events")
@admin_required()
def admin_events():
    q = request.args.get("q", "").strip()
    start_from = request.args.get("start_from", "").strip()
    start_to = request.args.get("start_to", "").strip()

    query = Event.query.join(Mentor).order_by(Event.start_at.asc())

    if q:
        like_value = f"%{q}%"
        query = query.filter(
            db.or_(
                Event.title.ilike(like_value),
                Event.description.ilike(like_value),
                Event.invitation_code.ilike(like_value),
                Mentor.name.ilike(like_value),
            )
        )

    try:
        if start_from:
            query = query.filter(Event.start_at >= datetime.fromisoformat(f"{start_from}T00:00:00"))
        if start_to:
            query = query.filter(
                Event.start_at <= datetime.fromisoformat(f"{start_to}T00:00:00") + timedelta(days=1) - timedelta(microseconds=1)
            )
    except ValueError:
        flash("Format filter tanggal tidak valid.", "error")
        return redirect(url_for("main.admin_events"))

    events = query.all()
    now = datetime.utcnow()
    return render_template(
        "admin_events.html",
        events=events,
        now=now,
        filters={
            "q": q,
            "start_from": start_from,
            "start_to": start_to,
        },
    )


@bp.route("/admin/token/regenerate", methods=["POST"])
@admin_required()
def admin_regenerate_token():
    admin = None
    admin_id = session.get("admin_id")
    if admin_id:
        admin = Admin.query.get(admin_id)
    if not admin:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            raw = auth.replace("Bearer ", "", 1).strip()
            admin = Admin.query.filter_by(api_token_hash=hash_token(raw)).first()
    if not admin:
        flash("Admin tidak ditemukan.", "error")
        return redirect(url_for("main.admin_login"))
    raw = generate_token()
    admin.api_token_hash = hash_token(raw)
    db.session.commit()
    session["new_api_token"] = raw
    flash("API token baru dibuat. Simpan token di dashboard.", "success")
    return redirect(url_for("main.admin_dashboard"))


@bp.route("/admin/events/<int:event_id>/registrations.csv")
@admin_required()
def admin_registrations_csv(event_id: int):
    event = Event.query.get_or_404(event_id)
    registrations = Registration.query.filter_by(event_id=event_id).all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "Nama",
            "Email",
            "Referral",
            "Invited By",
            "Status",
            "Certificate Number",
            "Created At",
        ]
    )
    for reg in registrations:
        writer.writerow(
            [
                reg.participant.name,
                reg.participant.email,
                reg.referral_code or "",
                reg.invited_by.referral_code if reg.invited_by else "",
                reg.status,
                reg.certificate.certificate_number if reg.certificate else "",
                reg.created_at.isoformat() if reg.created_at else "",
            ]
        )

    csv_data = output.getvalue()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=registrations_event_{event.id}.csv"
        },
    )


@bp.route("/user/register", methods=["GET", "POST"])
def user_register():
    if request.method == "GET":
        return render_template("user_register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm = request.form.get("confirm", "")

    if not name or not email or not password:
        flash("Semua field wajib diisi.", "error")
        return redirect(url_for("main.user_register"))
    if password != confirm:
        flash("Password tidak cocok.", "error")
        return redirect(url_for("main.user_register"))

    if Participant.query.filter_by(email=email).first():
        flash("Email sudah terdaftar.", "error")
        return redirect(url_for("main.user_register"))

    participant = Participant(
        participant_id=_generate_participant_id(),
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
        email_verified=False,
        email_verification_token=uuid4().hex,
    )
    db.session.add(participant)
    db.session.commit()
    session["participant_id"] = participant.id
    flash("Registrasi berhasil. Cek link verifikasi email di halaman profil.", "success")
    return redirect(url_for("main.user_profile"))


@bp.route("/user/login", methods=["GET", "POST"])
def user_login():
    if request.method == "GET":
        return render_template("user_login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    participant = Participant.query.filter_by(email=email).first()
    if participant and check_password_hash(participant.password_hash, password):
        session.pop("admin_id", None)
        session["participant_id"] = participant.id
        flash("Login berhasil.", "success")
        return redirect(url_for("main.user_dashboard"))

    admin = Admin.query.filter_by(email=email).first()
    if admin and check_password_hash(admin.password_hash, password):
        session.pop("participant_id", None)
        session["admin_id"] = admin.id
        flash("Login admin berhasil.", "success")
        return redirect(url_for("main.admin_dashboard"))

    flash("Email atau password salah.", "error")
    return redirect(url_for("main.user_login"))


@bp.route("/auth/github")
def github_login():
    if not current_app.config.get("GITHUB_CLIENT_ID"):
        flash("GitHub OAuth belum dikonfigurasi.", "error")
        return redirect(url_for("main.user_login"))
    redirect_uri = url_for("main.github_callback", _external=True)
    return oauth.github.authorize_redirect(redirect_uri)


@bp.route("/auth/github/callback")
def github_callback():
    token = oauth.github.authorize_access_token()
    if not token:
        flash("Login GitHub gagal.", "error")
        return redirect(url_for("main.user_login"))

    user_resp = oauth.github.get("user")
    user_data = user_resp.json() if user_resp else {}
    email_resp = oauth.github.get("user/emails")
    emails = email_resp.json() if email_resp else []

    primary_email = None
    for item in emails:
        if item.get("primary") and item.get("verified"):
            primary_email = item.get("email")
            break
    if not primary_email and emails:
        primary_email = emails[0].get("email")

    github_id = str(user_data.get("id") or "")
    github_username = user_data.get("login") or ""
    avatar_url = user_data.get("avatar_url") or ""

    if not github_id:
        flash("GitHub OAuth tidak mengembalikan ID pengguna.", "error")
        return redirect(url_for("main.user_login"))

    participant = Participant.query.filter_by(github_id=github_id).first()
    if not participant and primary_email:
        participant = Participant.query.filter_by(email=primary_email).first()

    if not participant:
        participant = Participant(
            participant_id=_generate_participant_id(),
            name=user_data.get("name") or github_username or "GitHub User",
            email=primary_email or f"{github_username}@users.noreply.github.com",
            password_hash=generate_password_hash(uuid4().hex),
            github_id=github_id,
            github_username=github_username,
            avatar_url=avatar_url,
            email_verified=True,
        )
        db.session.add(participant)
    else:
        participant.github_id = github_id
        participant.github_username = github_username
        participant.avatar_url = avatar_url

    db.session.commit()
    session["participant_id"] = participant.id
    flash("Login GitHub berhasil.", "success")
    return redirect(url_for("main.user_dashboard"))


@bp.route("/user/reset", methods=["GET", "POST"])
def user_reset_request():
    if request.method == "GET":
        return render_template("user_reset_request.html")

    email = request.form.get("email", "").strip().lower()
    participant = Participant.query.filter_by(email=email).first()
    if not participant:
        flash("Email peserta tidak ditemukan.", "error")
        return redirect(url_for("main.user_reset_request"))

    raw = generate_token()
    token = ParticipantResetToken(
        participant=participant,
        token_hash=hash_token(raw),
        expires_at=token_expiry(30),
    )
    db.session.add(token)
    db.session.commit()
    return render_template("user_reset_sent.html", token=raw)


@bp.route("/user/reset/<token>", methods=["GET", "POST"])
def user_reset_form(token: str):
    token_hash = hash_token(token)
    reset = ParticipantResetToken.query.filter_by(token_hash=token_hash, used_at=None).first()
    if not reset or reset.expires_at < datetime.utcnow():
        flash("Token reset tidak valid atau sudah kadaluarsa.", "error")
        return redirect(url_for("main.user_login"))

    if request.method == "GET":
        return render_template("user_reset_form.html", token=token)

    password = request.form.get("password", "")
    confirm = request.form.get("confirm", "")
    if not password or password != confirm:
        flash("Password tidak cocok.", "error")
        return redirect(url_for("main.user_reset_form", token=token))

    reset.participant.password_hash = generate_password_hash(password)
    reset.used_at = datetime.utcnow()
    db.session.commit()
    flash("Password berhasil direset. Silakan login.", "success")
    return redirect(url_for("main.user_login"))


@bp.route("/user/logout")
def user_logout():
    session.pop("participant_id", None)
    flash("Logout berhasil.", "success")
    return redirect(url_for("main.home"))


@bp.route("/user/dashboard")
@user_required
def user_dashboard():
    participant = Participant.query.get_or_404(session.get("participant_id"))
    now = datetime.utcnow()
    all_registrations = (
        Registration.query.join(Event, Registration.event_id == Event.id)
        .filter(Registration.participant_id == participant.id)
        .order_by(Event.start_at.desc())
        .all()
    )
    registrations = [reg for reg in all_registrations if reg.is_approved and reg.event.end_at >= now]
    pending_registrations = [reg for reg in all_registrations if not reg.is_approved and reg.event.end_at >= now]
    history_registrations = [reg for reg in all_registrations if reg.is_approved and reg.event.end_at < now]

    referrals = []
    for reg in all_registrations:
        invited = Registration.query.filter_by(invited_by_registration_id=reg.id, status="approved").all()
        referrals.append((reg, invited))

    return render_template(
        "user_dashboard.html",
        participant=participant,
        registrations=registrations,
        pending_registrations=pending_registrations,
        total_registrations=len(all_registrations),
        pending_count=len(pending_registrations),
        history_count=len(history_registrations),
        referrals=referrals,
    )


@bp.route("/user/events")
@user_required
def user_events():
    now = datetime.utcnow()
    participant = Participant.query.get_or_404(session.get("participant_id"))
    active_events = Event.query.filter(Event.start_at <= now, Event.end_at >= now).order_by(Event.start_at).all()
    upcoming_events = Event.query.filter(Event.start_at > now).order_by(Event.start_at).all()
    pending_registrations = (
        Registration.query.join(Event, Registration.event_id == Event.id)
        .filter(Registration.participant_id == participant.id)
        .filter(Registration.status == "pending")
        .filter(Event.end_at >= now)
        .order_by(Event.start_at.asc())
        .all()
    )
    return render_template(
        "user_events.html",
        active_events=active_events,
        upcoming_events=upcoming_events,
        pending_registrations=pending_registrations,
    )


@bp.route("/user/history")
@user_required
def user_history():
    participant = Participant.query.get_or_404(session.get("participant_id"))
    now = datetime.utcnow()
    history_registrations = (
        Registration.query.join(Event, Registration.event_id == Event.id)
        .filter(Registration.participant_id == participant.id)
        .filter(Registration.status == "approved")
        .filter(Event.end_at < now)
        .order_by(Event.end_at.desc())
        .all()
    )
    return render_template(
        "user_history.html",
        participant=participant,
        history_registrations=history_registrations,
    )


@bp.route("/user/profile", methods=["GET"])
@user_required
def user_profile():
    participant = Participant.query.get_or_404(session.get("participant_id"))
    return render_template("user_profile.html", participant=participant)


@bp.route("/user/profile/photo", methods=["POST"])
@user_required
def user_profile_photo():
    participant = Participant.query.get_or_404(session.get("participant_id"))
    file = request.files.get("photo")
    if not file or not file.filename:
        flash("Pilih file foto dulu.", "error")
        return redirect(url_for("main.user_profile"))
    if not _allowed_image(file.filename):
        flash("Format foto harus png/jpg/jpeg/svg.", "error")
        return redirect(url_for("main.user_profile"))

    filename = secure_filename(file.filename)
    ext = filename.rsplit(".", 1)[1].lower()
    new_name = f"avatar_{participant.id}_{uuid4().hex[:8]}.{ext}"
    upload_dir = os.path.join(current_app.root_path, "static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    save_path = os.path.join(upload_dir, new_name)
    file.save(save_path)
    participant.profile_photo_path = f"uploads/{new_name}"
    db.session.commit()
    flash("Foto profil berhasil diupdate.", "success")
    return redirect(url_for("main.user_profile"))


@bp.route("/user/verify/<token>")
def user_verify_email(token: str):
    participant = Participant.query.filter_by(email_verification_token=token).first()
    if not participant:
        flash("Token verifikasi tidak valid.", "error")
        return redirect(url_for("main.user_login"))
    participant.email_verified = True
    participant.email_verification_token = None
    db.session.commit()
    flash("Email berhasil diverifikasi.", "success")
    return redirect(url_for("main.user_profile"))
