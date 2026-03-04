import smtplib
from email.message import EmailMessage

from flask import current_app, url_for


def _send_email(message: EmailMessage) -> bool:
    smtp_host = current_app.config.get("SMTP_HOST")
    mail_from = current_app.config.get("MAIL_FROM_EMAIL")
    if not smtp_host or not mail_from:
        return False

    smtp_port = current_app.config.get("SMTP_PORT", 587)
    smtp_username = current_app.config.get("SMTP_USERNAME")
    smtp_password = current_app.config.get("SMTP_PASSWORD")
    smtp_use_tls = current_app.config.get("SMTP_USE_TLS", True)

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as smtp:
            smtp.ehlo()
            if smtp_use_tls:
                smtp.starttls()
                smtp.ehlo()
            if smtp_username:
                smtp.login(smtp_username, smtp_password or "")
            smtp.send_message(message)
    except Exception:
        return False

    return True


def send_registration_approved_email(registration) -> bool:
    mail_from = current_app.config.get("MAIL_FROM_EMAIL")
    if not mail_from:
        return False

    participant = registration.participant
    event = registration.event
    detail_url = url_for("main.registration_success", registration_id=registration.id, _external=True)

    message = EmailMessage()
    from_name = current_app.config.get("MAIL_FROM_NAME", "ITTS Community")
    message["Subject"] = f"Pendaftaran Event Disetujui: {event.title}"
    message["From"] = f"{from_name} <{mail_from}>"
    message["To"] = participant.email
    message.set_content(
        "\n".join(
            [
                f"Halo {participant.name},",
                "",
                f"Pendaftaran kamu untuk event '{event.title}' sudah disetujui.",
                "Sekarang kamu sudah resmi terdaftar.",
                "",
                f"Kode referral: {registration.referral_code}",
                f"Detail registrasi: {detail_url}",
                "",
                "Terima kasih.",
            ]
        )
    )

    return _send_email(message)


def send_certificate_ready_email(certificate) -> bool:
    mail_from = current_app.config.get("MAIL_FROM_EMAIL")
    if not mail_from:
        return False

    registration = certificate.registration
    participant = registration.participant
    event = registration.event
    view_url = url_for("main.certificate_view", certificate_number=certificate.certificate_number, _external=True)
    download_url = url_for("main.certificate_download", certificate_number=certificate.certificate_number, _external=True)

    message = EmailMessage()
    from_name = current_app.config.get("MAIL_FROM_NAME", "ITTS Community")
    message["Subject"] = f"Sertifikat Siap Diunduh: {event.title}"
    message["From"] = f"{from_name} <{mail_from}>"
    message["To"] = participant.email
    message.set_content(
        "\n".join(
            [
                f"Halo {participant.name},",
                "",
                f"Sertifikat untuk event '{event.title}' sudah siap.",
                f"Nomor sertifikat: {certificate.certificate_number}",
                "",
                f"Lihat sertifikat: {view_url}",
                f"Download sertifikat: {download_url}",
                "",
                "Terima kasih.",
            ]
        )
    )

    return _send_email(message)
