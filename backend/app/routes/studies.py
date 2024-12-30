from flask import Blueprint, request, jsonify
from app.services.study_service import generate_study, get_study_history

bp = Blueprint('studies', __name__, url_prefix='/api/studies')

@bp.route('/generate', methods=['POST'])
def create_study():
    data = request.get_json()
    parasha_name = data.get('parasha_name')
    study_type = data.get('study_type', 'default')
    
    if not parasha_name:
        return jsonify({'error': 'Nome da parashá não fornecido'}), 400
    
    study = generate_study(parasha_name, study_type)
    return jsonify(study)

@bp.route('/history', methods=['GET'])
def list_studies():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'ID do usuário não fornecido'}), 400
    
    history = get_study_history(user_id)
    return jsonify(history)
