import os


class Config:
    SECRET_KEY = '52eaf892e503af6001950ab4f7ef2459'
    SQLALCHEMY_DATABASE_URI = "sqlite:///medlink.db" or os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    ADMINS = os.environ.get('mail')
    MAIL_USERNAME = 'noreply.sifuna@gmail.com'
    MAIL_PASSWORD = 'yogeroyogerodinero33'
    SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
    NEXMO_NUMBER = 447700900025
    # NEXMO_API_KEY = abcd1234
    # NEXMO_API_SECRET = abcdef12345678
