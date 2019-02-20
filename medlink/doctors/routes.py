from flask import Blueprint, render_template, url_for, redirect, flash, request, abort
from medlink.doctors.forms import RegistrationForm, LoginForm, AssignForm, ProfileForm, ResetRequestForm, ResetPasswordForm, SubscribeForm
from medlink import db, bcrypt
import nexmo
from datetime import datetime, timedelta, date
from medlink.models import Doctors, Appointment, Subscribers, Department
from medlink.doctors.utils import send_reset_email
from flask_login import login_user, current_user, logout_user, login_required

doctors = Blueprint('doctors', __name__)


@doctors.route('/pending')
@login_required
def pending():
    now = datetime.utcnow()
    tdelta = timedelta(hours=3)
    now = now + tdelta
    appointments = Appointment.query.filter_by(complete="False").all()
    return render_template('pending_appointments.html', appointments=appointments, now=now)


@doctors.route('/week/<int:week_id>/print')
@login_required
def print_week(week_id):
    now = datetime.utcnow()
    tdelta = timedelta(hours=3)
    now = now + tdelta
    appointments = Appointment.query.filter_by(print_date=week_id)
    return render_template('week_pdfs.html', appointments=appointments, now=now, week_id=week_id)


@doctors.route('/week')
@login_required
def week():
    today_week = int(datetime.today().strftime('%U'))

    return render_template('week.html', today_week=today_week)


@doctors.route('/print_pdf/<int:doctor_id>')
@login_required
def print_pdf(doctor_id):
    today = date.today()
    # today_date = int(today.strftime('%d'))
    appointments = Appointment.query.filter_by(doctor_id=doctor_id, complete="False").all()
    doctor = Doctors.query.get_or_404(doctor_id)
    now = datetime.utcnow()
    tdelta = timedelta(hours=3)
    now = now + tdelta
    first, last = doctor.fullname.split(" ")
    return render_template('print_pdfs.html', first=first, last=last, appointments=appointments, doctor=doctor, now=now)


@doctors.route('/subscribers')
@login_required
def subscribers():
    if current_user.user_role == "Adminstrator":
        subscribers_list = Subscribers.query.all()
        now = datetime.utcnow()
        tdelta = timedelta(hours=3)
        now = now + tdelta
        return render_template('subscribers.html', subscribers_list=subscribers_list, now=now)
    else:
        abort(403)


@doctors.route('/', methods=['GET', 'POST'])
@doctors.route('/home', methods=['GET', 'POST'])
def home():
    form = SubscribeForm()
    if form.validate_on_submit():
        subscriber = Subscribers(email=form.email.data)
        db.session.add(subscriber)
        db.session.commit()
        # flash('Subscription successful', 'success')

    return render_template('index.html', form=form)


@doctors.route('/about')
def about():

    return render_template('b4.html')


@doctors.route('/send_sms/<int:appointment_id>')
@login_required
def send_sms(appointment_id):
    if current_user.user_role == "Adminstrator":
        appointment = Appointment.query.get_or_404(appointment_id)
        to_number = int("254" + appointment.doctor.phone)
        message = f"Dr.{appointment.doctor.fullname}, you have been scheduled an appointment with a client {appointment.fullname} , 0{appointment.phone}. thank you!"
        nexmo_client = nexmo.Client(key='e3a37e8d', secret='9hH7Brg17foyRlgs')
        sent = nexmo_client.send_message({
            'from': 12345,
            'to': 254713812939,
            'text': message,
        })
        if sent:
            appointment.sms_sent = "True"
            db.session.commit()
            flash(f"message successfully sent to Dr.{appointment.doctor.fullname}", 'success')
        return redirect(url_for('appointments.appointments_route'))
    else:
        abort(403)


@doctors.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.fullname = form.fullname.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        current_user.status = form.status.data
        db.session.commit()
    form.fullname.data = current_user.fullname
    form.email.data = current_user.email
    form.phone.data = current_user.phone
    form.status.data = current_user.status
    return render_template('profile.html', form=form)


def listnames(depart):
    docs = Doctors.query.filter_by(department=depart).all()
    name = []
    for doc in docs:
        if doc.user_role == "User" and doc.status == "Active":
            fullname = (doc.fullname, doc.fullname)
            name.append(fullname)
    return name


@doctors.route('/doctor')
@login_required
def doc_client():
    if current_user.user_role == "Adminstrator":
        return redirect(url_for('doctors.admin'))
    if current_user.is_authenticated:
        now = datetime.utcnow()
        tdelta = timedelta(hours=3)
        now = now + tdelta
        doctor_appointments = Appointment.query.filter_by(doctor=current_user).all()
    else:
        return redirect(url_for('doctors.login'))
    return render_template('doc-tasks.html', doctor_appointments=doctor_appointments, now=now)


@doctors.route('/doctors')
@login_required
def doctors_route():
    if current_user.user_role != "Adminstrator":
        return redirect(url_for('doctors.doc_client'))
    doctors_all = Doctors.query.filter_by(user_role="User").all()

    return render_template('doctors.html', doctors=doctors_all)


def getnames(depart):
    return Doctors.query.filter_by(department=depart, status="Active").all


def get_pk(obj):
    return str(obj)


@doctors.route('/assign/<int:appointment_id>/assign', methods=['GET', 'POST'])
def assign(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    form = AssignForm()
    form.doctor.get_pk = get_pk
    form.doctor.query_factory = getnames(appointment.appointment_department)
    form.fullname.data = appointment.fullname
    if form.validate_on_submit():
        today = date.today()
        appointment.assigned = "True"
        appointment.doctor = form.doctor.data
        appointment.print_date=today.strftime('%U')
        db.session.commit()
        flash('Appointment Assignation successfull', 'success')
        return redirect(url_for('appointments.appointments_route'))
    return render_template('assign.html', form=form)


@doctors.route('/admin')
@login_required
def admin():
    if current_user.user_role != "Adminstrator":
        return redirect(url_for('doctors.doc_client'))
    appointments_count = Appointment.query.filter_by(assigned="False").count()
    pending_appointments_count = Appointment.query.filter_by(complete="False").count()
    doctors_on_leave = Doctors.query.filter_by(status="InActive").count()
    subscribers_count = Subscribers.query.count()
    return render_template('admin.html', appointments_count=appointments_count, doctors_on_leave=doctors_on_leave, pending_appointments_count=pending_appointments_count, subscribers_count=subscribers_count)


def getdepartment():
    return Department.query.all()


def get_pk(obj):
    return str(obj)


@doctors.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if current_user.is_authenticated:
        return redirect(url_for('doctors.home'))

    else:
        form.department.get_pk = get_pk
        form.department.query_factory = getdepartment
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            doctor = Doctors(fullname=form.fullname.data, email=form.email.data, phone=form.phone.data, password=hashed_password, department=form.department.data.department_name)
            db.session.add(doctor)
            db.session.commit()
            flash("Registration successful you can now log in", "success")
            return redirect(url_for('doctors.login'))

    return render_template('register.html', form=form)


@doctors.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('doctors.home'))
    if form.validate_on_submit():
        doctor = Doctors.query.filter_by(email=form.email.data).first()
        if doctor and bcrypt.check_password_hash(doctor.password, form.password.data):
            login_user(doctor, remember=form.remember.data)
            if doctor.user_role == "Adminstrator":
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('doctors.admin'))
            else:
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('doctors.doc_client'))
        else:
            flash("Login unsuccessful. Please check email and password", "danger")
    return render_template('login.html', form=form)


@doctors.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('doctors.login'))


@doctors.route('/inactive')
@login_required
def inactive():
    inactive_doctors = Doctors.query.filter_by(status="InActive").all()
    return render_template('inactive.html', inactive_doctors=inactive_doctors)


@doctors.route('/dashboard')
def dashboard():

    return render_template('dashboard.html')


@doctors.route('/delete/<int:doc_id>')
@login_required
def delete(doc_id):
    if current_user.user_role == "Adminstrator":
        doc = Doctors.query.get_or_404(doc_id)
        appointments = Appointment.query.filter_by(doctor=doc).all()
        for appointment in appointments:
            if appointment.complete == "False":
                appointment.assigned = "False"
                appointment.doctor_id = " "
                appointment.sms_sent = "False"
            db.session.commit()
        db.session.delete(doc)
        db.session.commit()
        flash('Doctor deleted successfully', 'success')
        return redirect(url_for('doctors.doctors_route'))
    else:
        abort(403)


@doctors.route('/complete/<int:appointment_id>')
@login_required
def complete(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.doctor == current_user or current_user.user_role == "Adminstrator":
        appointment.complete = "True"
        db.session.commit()
        flash('Appointment status updated successfully', 'success')
        if current_user.user_role == "Adminstrator":
            return redirect(url_for('appointments.appointments_route'))
        else:
            return redirect(url_for('doctors.doc_client'))
    else:
        abort(403)


@doctors.route('/reset_password', methods=['POST', 'GET'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('doctors.doctors_route'))
    form = ResetRequestForm()
    if form.validate_on_submit():
        doctor = Doctors.query.filter_by(email=form.email.data).first()
        send_reset_email(doctor)
        flash("An email has been sent with instructions to reset your password", 'info')
        return redirect(url_for('doctors.login'))
    return render_template("reset_request.html", title="Reset Password", form=form)


@doctors.route('/reset_password/<token>', methods=['POST', 'GET'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('doctors.doctors_route'))
    doctor = Doctors.verify_reset_token(token)
    if doctor is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('doctors.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        doctor.password = password
        db.session.commit()
        flash(f'Your password has been updated. You can now log in', 'success')
        return redirect(url_for('doctors.login'))
    return render_template("reset_token.html", title="Reset Password", form=form)
