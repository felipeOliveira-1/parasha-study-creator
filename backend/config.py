import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-replace-in-production'
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'livros')
    STUDIES_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'estudos')
