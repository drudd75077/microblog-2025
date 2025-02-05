import logging
from logging.handlers import RotatingFileHandler
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

if not app.debug:
    class SendGridEmailHandler(logging.Handler):
        def __init__(self, api_key, to_email):
            super().__init__()
            self.api_key = api_key
            self.to_email = to_email

        def emit(self, record):
            message = self.format(record)
            self.send_email(message)

        def send_email(self, message):
            sg = SendGridAPIClient(self.api_key)
            email = Mail(
                from_email=app.config['MAIL_DEFAULT_SENDER'],
                to_emails=self.to_email,
                subject='Error Log Notification',
                plain_text_content=message
            )
            try:
                sg.send(email)
            except Exception as e:
                print(f"Failed to send email: {e}")
            
# Configure logging
logger = logging.getLogger('EmailLogger')
logger.setLevel(logging.ERROR)

# Set up SendGrid email handler
api_key = app.config['SENDGRID_API_KEY']
email_handler = SendGridEmailHandler(api_key, app.config['SENDGRID_RECIPIENTS'])
print('email handler', vars(email_handler))
formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
email_handler.setFormatter(formatter)
logger.addHandler(email_handler)

#sending log to text file
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                       backupCount=10)
file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.ERROR)

from app import routes, models, errors