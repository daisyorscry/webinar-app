import time

from sqlalchemy import text

from app import create_app
from app.extensions import db


def wait_for_db(max_attempts=30, delay=1):
    app = create_app()

    for attempt in range(1, max_attempts + 1):
        try:
            with app.app_context():
                db.session.execute(text("SELECT 1"))
                db.session.commit()
            print("Database is ready.")
            return
        except Exception as exc:
            if attempt == max_attempts:
                raise
            print(f"Waiting for database ({attempt}/{max_attempts}): {exc}")
            time.sleep(delay)


if __name__ == "__main__":
    wait_for_db()
