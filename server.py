import os
from flask import Flask

from booking import db, login_manager, migrate
from booking.models import Booking, Room, User
from booking.routes import main


def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    template_dir = os.path.join(base_dir, "booking", "templates")

    app = Flask(__name__, template_folder=template_dir)

    # 🔥 ใช้ PostgreSQL จาก Render เท่านั้น
    DATABASE_URL = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL not set")

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "secret123")
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    app.register_blueprint(main)

    @app.shell_context_processor
    def shell_context():
        return {
            "db": db,
            "User": User,
            "Room": Room,
            "Booking": Booking,
        }

    return app


app = create_app()

# 🔥 สร้าง DB อัตโนมัติ (ไม่ต้องใช้ shell)
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)