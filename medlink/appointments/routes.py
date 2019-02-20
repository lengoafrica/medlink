from flask import Blueprint, url_for, redirect, render_template, abort, flash
from flask_login import current_user, login_required
from datetime import datetime, timedelta
from medlink import db
from medlink.models import Appointment, Department, DepartmentAppointment
from medlink.appointments.forms import AppointmentForm, DepartmentForm, DepartmentAppointmentForm

appointments = Blueprint('appointments', __name__)


@appointments.route('/appointments')
@login_required
def appointments_route():
    if current_user.user_role != "Adminstrator":
        return redirect(url_for('doctors.doc_client'))
    now = datetime.utcnow()
    tdelta = timedelta(hours=3)
    now = now + tdelta
    appointments = Appointment.query.order_by(Appointment.date_of_booking.desc()).all()

    return render_template('appointments.html', appointments=appointments, now=now)


def getdepartment():
    return Department.query.all()


def get_pk(obj):
    return str(obj)


@appointments.route('/book', methods=['GET', 'POST'])
def book():
    form = AppointmentForm()
    form.department.get_pk = get_pk
    form.department.query_factory = getdepartment
    if form.validate_on_submit():
        appointment = Appointment(fullname=form.fullname.data, email=form.email.data, phone=form.phone.data, appointment_department=form.department.data.department_name)
        db.session.add(appointment)
        db.session.commit()
        # flash("Appointment booked successfully. You will be contacted soon", "success")
        return redirect(url_for('doctors.dashboard'))
    return render_template('book.html', form=form)


@appointments.route('/add_department', methods=['GET', 'POST'])
@login_required
def add_department():
    if current_user.user_role != "Adminstrator":
        abort(403)
    form = DepartmentForm()
    if form.validate_on_submit():
        department = Department(department_name=form.department.data)
        db.session.add(department)
        db.session.commit()

        flash('Department added successfully', 'success')
        return redirect(url_for("appointments.view_department"))
    return render_template('add_department.html', form=form)


@appointments.route('/view_department')
@login_required
def view_department():
    if current_user.user_role != "Adminstrator":
        abort(403)
    departments = Department.query.all()
    now = datetime.utcnow()
    tdelta = timedelta(hours=3)
    now = now + tdelta
    return render_template('view_department.html', departments=departments, now=now)


@appointments.route('/department_timetable/<int:dep_id>')
@login_required
def department_timetable(dep_id):
    if current_user.user_role != "Adminstrator":
        abort(403)
    form = DepartmentAppointmentForm()
    form.dep_id.data = Department.query.get_or_404(dep_id).department_name
    if form.validate_on_submit():
        add_time = DepartmentAppointment(time=form.time.data, department_id=dep_id)
        db.session.add(add_time)
        db.session.commit()
        return redirect(url_for('view_department'))
    return render_template('add_dep_time.html', form=form)
