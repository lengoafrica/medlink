from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, Email
from wtforms_sqlalchemy.fields import QuerySelectField


class AppointmentForm(FlaskForm):
    fullname = StringField('Full Name', validators=[DataRequired(), Length(min=4, max=30)])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    phone = IntegerField('Phone Number', validators=[DataRequired()])
    department = QuerySelectField('Select Department', validators=[DataRequired()], get_label='department_name', allow_blank=True)
    submit = SubmitField('Book Appointment')


class DepartmentAppointmentForm(FlaskForm):
    time = StringField('Enter time', validators=[DataRequired()])
    dep_id = StringField('Department', validators=[DataRequired()])
    submit = SubmitField('Add')


class DepartmentForm(FlaskForm):
    department = StringField('Enter Department', validators=[DataRequired()])
    submit = SubmitField('Add')
