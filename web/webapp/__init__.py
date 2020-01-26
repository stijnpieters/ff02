from flask import Flask
from flask_cors import CORS
import os


def create_app():
    app = Flask(__name__)
    CORS(app)

    with app.app_context():
        # Imports
        from . import routes

        return app
