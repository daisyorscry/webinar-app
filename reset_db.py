from sqlalchemy import text
from app import create_app
from app.extensions import db


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.session.execute(text("DROP TABLE IF EXISTS alembic_version"))
        db.session.commit()
        print("All tables dropped.")
