from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign in")


class FarmerForm(FlaskForm):
    full_name = StringField("Full name", validators=[DataRequired(), Length(max=120)])
    phone = StringField("Phone", validators=[Optional(), Length(max=30)])
    village = StringField("Village", validators=[Optional(), Length(max=120)])
    district = StringField("District", validators=[Optional(), Length(max=120)])
    state = StringField("State", validators=[Optional(), Length(max=120)])
    land_area_ha = IntegerField("Land area (ha)", validators=[Optional(), NumberRange(min=0)])
    gps_lat = StringField("GPS latitude", validators=[Optional()])
    gps_lng = StringField("GPS longitude", validators=[Optional()])
    submit = SubmitField("Save farmer")


class ImplementationForm(FlaskForm):
    farmer_id = SelectField("Farmer", coerce=str, validators=[DataRequired()])
    activity_type = StringField("Activity type", validators=[DataRequired(), Length(max=80)])
    species_planted = StringField("Species planted", validators=[Optional(), Length(max=120)])
    number_of_saplings = IntegerField("Number of saplings", validators=[Optional(), NumberRange(min=0)])
    date_of_activity = DateField("Date of activity", validators=[DataRequired()])
    status = SelectField(
        "Status",
        choices=[("planned", "Planned"), ("in_progress", "In Progress"), ("completed", "Completed")],
        validators=[DataRequired()],
    )
    notes = TextAreaField("Notes", validators=[Optional()])
    photo_url = StringField("Photo URL", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Save record")


class UserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    full_name = StringField("Full name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    role = SelectField(
        "Role",
        choices=[("field_executive", "Field Executive"), ("field_manager", "Field Manager"), ("senior_manager", "Senior Manager")],
        validators=[DataRequired()],
    )
    manager_id = SelectField("Manager", coerce=str, validators=[Optional()])
    submit = SubmitField("Create user")
