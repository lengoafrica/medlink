from medlink import db, lm
from flask import current_app as app
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@lm.user_loader
def load_user(doctor_id):
    return Doctors.query.get(int(doctor_id))


class Doctors(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    fullname = db.Column(db.String(30), unique=True, nullable=False)
    user_role = db.Column(db.String(30), default="User")
    department = db.Column(db.String(30), default="Adminstrator")
    status = db.Column(db.String(20), nullable=False, default="Active")
    email = db.Column(db.String(30), unique=True, nullable=False)
    phone = db.Column(db.String(10), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    appointment = db.relationship('Appointment', backref='doctor', lazy=True)

    def get_reset_token(self, expires_sec=18000):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'doctor_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            doctor_id = s.loads(token)['doctor_id']
        except Exception as e:
            return None
        return Doctors.query.get(doctor_id)

    def __repr__(self):
        return f"{self.fullname}"

    def __str__(self):
        return f"{self.fullname}"


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    fullname = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    appointment_department = db.Column(db.String(30), nullable=False)
    assigned = db.Column(db.String(30), nullable=False, default="False")
    sms_sent = db.Column(db.String(70), nullable=False, default="False")
    print_date = db.Column(db.Integer)
    date_of_booking = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    complete = db.Column(db.String(30), nullable=False, default="False")
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'))

    def __repr__(self):
        return f"{self.id},{self.fullname}"


class Subscribers(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    email = db.Column(db.String(30), nullable=False)


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    department_name = db.Column(db.String(30), nullable=False)
    appointment_time = db.relationship('DepartmentAppointment', backref='appointment', lazy=True)

    def __repr__(self):
        return f"{self.department_name}"

    def __str__(self):
        return f"{self.department_name}"


class DepartmentAppointment(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    time = db.Column(db.String(40), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
