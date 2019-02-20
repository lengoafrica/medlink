from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from medlink.models import Doctors, Subscribers
from wtforms_sqlalchemy.fields import QuerySelectField


class RegistrationForm(FlaskForm):
    fullname = StringField('Full Name', validators=[DataRequired(), Length(min=4, max=30)])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    phone = IntegerField('Phone Number', validators=[DataRequired()])
    department = QuerySelectField('Select Department', validators=[], get_label='department_name', allow_blank=True)
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=8), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_fullname(self, fullname):
        doctor = Doctors.query.filter_by(fullname=fullname.data).first()
        if doctor:
            raise ValidationError('That name is taken. Please check your Name.')

    def validate_email(self, email):
        doctor = Doctors.query.filter_by(email=email.data).first()
        if doctor:
            raise ValidationError('That email is taken. Please check your email.')

    def validate_phone(self, phone):
        doctor = Doctors.query.filter_by(phone=phone.data).first()
        if doctor:
            raise ValidationError('That phone Number is taken. Please check your Phone number.')


class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    remember = BooleanField('Remember Me?')
    submit = SubmitField('Sign In')


class ProfileForm(FlaskForm):
    fullname = StringField('Full Name', validators=[DataRequired(), Length(min=4, max=30)])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    phone = IntegerField('Phone Number', validators=[DataRequired()])
    status = SelectField('Status', choices=[('Active', 'Active'), ('InActive', 'InActive')])
    submit = SubmitField('Update Status')


class AssignForm(FlaskForm):
    fullname = StringField('Full Name', validators=[DataRequired(), Length(min=4, max=30)])
    doctor = QuerySelectField('Assign Doctor', validators=[DataRequired()], get_label='fullname', allow_blank=True)
    submit = SubmitField('Assign')


class ResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        doctor = Doctors.query.filter_by(email=email.data).first()
        if doctor is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), Length(min=8), EqualTo('password')])
    submit = SubmitField('Reset Password')


class SubscribeForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])

    def validate_email(self, email):
        subscriber = Subscribers.query.filter_by(email=email.data).first()
        if subscriber:
            raise ValidationError('That email is already subscribed. Please check your email.')
