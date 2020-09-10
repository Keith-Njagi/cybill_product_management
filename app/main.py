import os

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from flask import Flask, jsonify
from flask_cors import CORS
from marshmallow import ValidationError

from configurations import *
from resources import blueprint, jwt 
from models import db
from schemas import ma

app = Flask(__name__)

app.config.from_object(Development)

sentry_sdk.init(
    dsn="https://3991c8bcf1314bc48b49c1452e1eaca2@o431070.ingest.sentry.io/5380982",
    integrations=[FlaskIntegration()]
)

CORS(app)
app.register_blueprint(blueprint)
# mail.init_app(app)
jwt.init_app(app)
db.init_app(app)
ma.init_app(app)

basedir = os.path.abspath(os.path.dirname(__file__))

@app.before_first_request
def create_tables():
    db.create_all()

@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    return jsonify(err.messages), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3102)