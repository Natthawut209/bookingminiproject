from datetime import date

from flask_wtf import FlaskForm
from wtforms import DateField, PasswordField, StringField, SubmitField, TextAreaField, TimeField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=128)])
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=128)])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Register")


class RoomForm(FlaskForm):
    name = StringField("Room Name", validators=[DataRequired(), Length(min=2, max=120)])
    description = TextAreaField("Description", validators=[DataRequired(), Length(min=5, max=255)])
    submit = SubmitField("Add Room")


class BookingForm(FlaskForm):
    booking_date = DateField("Booking Date", validators=[DataRequired()], format="%Y-%m-%d")
    start_time = TimeField("Start Time", validators=[DataRequired()], format="%H:%M")
    end_time = TimeField("End Time", validators=[DataRequired()], format="%H:%M")
    submit = SubmitField("Book Room")

    def validate_booking_date(self, field):
        if field.data < date.today():
            raise ValidationError("Booking date cannot be in the past.")

    def validate_end_time(self, field):
        if self.start_time.data and field.data and field.data <= self.start_time.data:
            raise ValidationError("End time must be later than start time.")
