import os
from flask import Flask
from flask_pymongo import PyMongo
from app.config import Config

mongo = PyMongo()

def create_app():
    app =  Flask(__name__)
    app.config.from_object(Config)

# Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    mongo.init_app(app)

    # Register blueprints
    from app.views.auth import auth_bp
    from app.views.citizen import citizen_bp
    from app.views.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(citizen_bp)
    app.register_blueprint(admin_bp)

    return app

