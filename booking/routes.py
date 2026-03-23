from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import func

from booking import db
from booking.forms import BookingForm, LoginForm, RegisterForm, RoomForm
from booking.models import Booking, Room, User


main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.rooms"))

    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        existing_user = User.query.filter(func.lower(User.username) == username.lower()).first()

        if existing_user:
            flash("Username is already taken.", "danger")
        else:
            user = User(username=username)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("main.login"))

    return render_template("user/register.html", form=form)


@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.rooms"))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        user = User.query.filter(func.lower(User.username) == username.lower()).first()

        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Welcome back!", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("main.rooms"))

        flash("Invalid username or password.", "danger")

    return render_template("user/login.html", form=form)


@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


@main.route("/rooms")
@login_required
def rooms():
    form = RoomForm()
    all_rooms = Room.query.order_by(Room.name.asc()).all()
    return render_template("booking/rooms.html", form=form, rooms=all_rooms)


@main.route("/add_room", methods=["POST"])
@login_required
def add_room():
    form = RoomForm()

    if form.validate_on_submit():
        room_name = form.name.data.strip()
        existing_room = Room.query.filter(func.lower(Room.name) == room_name.lower()).first()

        if existing_room:
            flash("Room name already exists.", "danger")
        else:
            room = Room(name=room_name, description=form.description.data.strip())
            db.session.add(room)
            db.session.commit()
            flash("Room added successfully.", "success")
    else:
        for field_errors in form.errors.values():
            for err in field_errors:
                flash(err, "danger")

    return redirect(url_for("main.rooms"))


@main.route("/delete_room/<int:id>", methods=["POST"])
@login_required
def delete_room(id):
    room = db.session.get(Room, id)

    if not room:
        flash("Room not found.", "danger")
    else:
        db.session.delete(room)
        db.session.commit()
        flash("Room deleted.", "success")

    return redirect(url_for("main.rooms"))


@main.route("/book/<int:room_id>", methods=["GET", "POST"])
@login_required
def book(room_id):
    room = db.session.get(Room, room_id)

    if not room:
        flash("Room not found.", "danger")
        return redirect(url_for("main.rooms"))

    form = BookingForm()
    if form.validate_on_submit():
        booking_date = form.booking_date.data
        start_time = form.start_time.data
        end_time = form.end_time.data

        conflict = Booking.query.filter(
            Booking.room_id == room.id,
            Booking.booking_date == booking_date,
            Booking.start_time < end_time,
            Booking.end_time > start_time,
        ).first()

        if conflict:
            flash("Time conflict: this room is already booked in the selected time range.", "danger")
        else:
            booking = Booking(
                user_id=current_user.id,
                room_id=room.id,
                booking_date=booking_date,
                start_time=start_time,
                end_time=end_time,
            )
            db.session.add(booking)
            db.session.commit()
            flash("Room booked successfully.", "success")
            return redirect(url_for("main.bookings"))

    return render_template("booking/book.html", form=form, room=room)


@main.route("/bookings")
@login_required
def bookings():
    user_bookings = (
        Booking.query.filter_by(user_id=current_user.id)
        .order_by(Booking.booking_date.asc(), Booking.start_time.asc())
        .all()
    )
    return render_template("booking/bookings.html", bookings=user_bookings)


@main.route("/delete_booking/<int:id>", methods=["POST"])
@login_required
def delete_booking(id):
    target_booking = db.session.get(Booking, id)

    if not target_booking:
        flash("Booking not found.", "danger")
    elif target_booking.user_id != current_user.id:
        flash("You are not allowed to delete this booking.", "danger")
    else:
        db.session.delete(target_booking)
        db.session.commit()
        flash("Booking deleted.", "success")

    return redirect(url_for("main.bookings"))
