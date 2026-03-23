import os

from flask import Flask

from booking import db, login_manager, migrate
from booking.models import Booking, Room, User
from booking.routes import main


def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    template_dir = os.path.join(base_dir, "booking", "templates")
    app = Flask(__name__, template_folder=template_dir)

    db_path = os.path.join(base_dir, "room_booking.db").replace("\\", "/")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "kwekxkkckakkseow!eooxcdada")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    main.template_folder = "templates"
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


if __name__ == "__main__":
    app.run(debug=True)
