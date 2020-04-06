from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from utils.fake_mail import FakeMail
import os

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

login_manager = LoginManager(app)

app.config['BASE_DOMAIN'] = os.getenv('BASE_DOMAIN')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

mail = None

if os.getenv('MAIL_ACTIVE'):
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
    app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD')
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('EMAIL')
    app.config['MAIL_DEBUG'] = True

    mail = Mail(app)
else:
    print('Warning: Mailing component not connected.')
    mail = FakeMail(app)
