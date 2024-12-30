from supabase import create_client
from flask import current_app

def get_supabase_client():
    """
    Retorna uma instância do cliente Supabase
    """
    url = current_app.config['SUPABASE_URL']
    key = current_app.config['SUPABASE_KEY']
    return create_client(url, key)

def authenticate_user(email, password):
    """
    Autentica um usuário usando o Supabase Auth
    """
    supabase = get_supabase_client()
    response = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })
    return response.user

def create_user(email, password, name):
    """
    Cria um novo usuário usando o Supabase Auth
    """
    supabase = get_supabase_client()
    response = supabase.auth.sign_up({
        "email": email,
        "password": password,
        "data": {
            "name": name
        }
    })
    return response.user
