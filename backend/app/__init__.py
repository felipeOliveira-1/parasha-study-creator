from flask import Flask
from flask_cors import CORS
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(config_class)

    # Registrar blueprints
    from app.routes import parasha, studies, auth
    app.register_blueprint(parasha.bp)
    app.register_blueprint(studies.bp)
    app.register_blueprint(auth.bp)

    return app
