from flask import render_template, url_for
from flask_mail import Message
from medlink import mail


def send_reset_email(doctor):
    token = doctor.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply.sifuna@gmail.com', recipients=[doctor.email])
    msg.body = f"""
    To reset your password follow the following link:
    {url_for('doctors.reset_token', token=token, _external=True)}



    if you did not make this request just ignore this email.
    """
    mail.send(msg)
