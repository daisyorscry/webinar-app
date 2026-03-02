from functools import wraps
from flask import request, session, redirect, url_for, flash
from .models import Admin
from .security import hash_token


def admin_required(view=None, role: str | None = None):
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            admin = None
            admin_id = session.get("admin_id")
            if admin_id:
                admin = Admin.query.get(admin_id)

            if not admin:
                auth = request.headers.get("Authorization", "")
                if auth.startswith("Bearer "):
                    raw = auth.replace("Bearer ", "", 1).strip()
                    token_hash = hash_token(raw)
                    admin = Admin.query.filter_by(api_token_hash=token_hash).first()

            if not admin:
                flash("Silakan login sebagai admin.", "error")
                return redirect(url_for("main.admin_login"))

            if role and admin.role not in {role, "superadmin"}:
                flash("Akses ditolak.", "error")
                return redirect(url_for("main.admin_dashboard"))

            return func(*args, **kwargs)

        return wrapped

    if callable(view):
        return decorator(view)
    return decorator


def user_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("participant_id"):
            flash("Silakan login sebagai peserta.", "error")
            return redirect(url_for("main.user_login"))
        return view(*args, **kwargs)

    return wrapped
