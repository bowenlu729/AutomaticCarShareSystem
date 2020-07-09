import os
from flask import Flask
from flask_mail import Mail


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = '1'

app = Flask(__name__)
app.config.from_object(__name__)

if os.environ.get("FLASK_UNIT_TEST") is None:
    app.config["MYSQL_DATABASE_HOST"] = "127.0.0.1"
    app.config["MYSQL_DATABASE_USER"] = "root"
    app.config["MYSQL_DATABASE_PASSWORD"] = "123456"
    app.config["MYSQL_DATABASE_DB"] = "piot2db"
    app.config["SECRET_KEY"] = "00ab62088ecf78c3a272d478f9de994e"
else:
    app.config["TESTING"] = True
    app.config["MYSQL_DATABASE_HOST"] = "127.0.0.1"
    app.config["MYSQL_DATABASE_USER"] = "root"
    app.config["MYSQL_DATABASE_PASSWORD"] = "123456"
    app.config["MYSQL_DATABASE_DB"] = "piot2db"
    app.config["MYSQL_DATABASE_DB"] = "utestdb"
    app.config["SECRET_KEY"] = "unit-tests"

app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_TLS = False,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = 'piotbwl729@gmail.com',
    MAIL_PASSWORD = '123456lbw',
    MAIL_DEFAULT_SENDER = 'piotbwl729@gmail.com',
))

mail = Mail(app)

from api.controllers import api
app.register_blueprint(api, url_prefix="/api")

from web import web
app.register_blueprint(web)

from oauth import oauth
app.register_blueprint(oauth)

app.debug = True

if __name__ == "__main__":
    app.run()
