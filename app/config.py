import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://app_user:S3cure_AppDb_2026!@localhost:5432/app_db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ATTENDANCE_API_URL = os.getenv("ATTENDANCE_API_URL", "")
    ATTENDANCE_API_KEY = os.getenv("ATTENDANCE_API_KEY", "")
    USE_MOCK_API = os.getenv("USE_MOCK_API", "0") == "1"

    GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
    GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")

    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "1") == "1"
    MAIL_FROM_EMAIL = os.getenv("MAIL_FROM_EMAIL", "")
    MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "ITTS Community")

    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "app/static/uploads")
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "svg"}
