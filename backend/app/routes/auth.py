from flask import Blueprint, request, jsonify
from app.services.supabase_service import authenticate_user, create_user

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400
    
    auth_result = authenticate_user(email, password)
    return jsonify(auth_result)

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    
    if not all([email, password, name]):
        return jsonify({'error': 'Todos os campos são obrigatórios'}), 400
    
    user = create_user(email, password, name)
    return jsonify(user)
