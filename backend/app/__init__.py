import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def create_app(test_config=None):
    # Cria e configura a app
    app = Flask(__name__, instance_relative_config=True)
    
    # Habilita CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173"],  # Frontend Vite dev server
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "max_age": 3600
        }
    })
    
    # Configuração padrão
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        OPENAI_API_KEY=os.environ.get('OPENAI_API_KEY'),
        OPENAI_MODEL=os.environ.get('OPENAI_MODEL', 'gpt-4o'),
    )

    if test_config is None:
        # Carrega a instância config, se existir
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Carrega a config de teste
        app.config.update(test_config)

    # Registra blueprints
    from .routes import parasha, studies
    app.register_blueprint(parasha.bp)
    app.register_blueprint(studies.bp)
    
    # Remove autenticação
    app.config.pop('SUPABASE_URL', None)
    app.config.pop('SUPABASE_KEY', None)

    return app
