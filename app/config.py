import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://app_user:secret123@localhost:5432/app_db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ATTENDANCE_API_URL = os.getenv("ATTENDANCE_API_URL", "")
    ATTENDANCE_API_KEY = os.getenv("ATTENDANCE_API_KEY", "")
    USE_MOCK_API = os.getenv("USE_MOCK_API", "0") == "1"

    GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
    GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")

    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "app/static/uploads")
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "svg"}
