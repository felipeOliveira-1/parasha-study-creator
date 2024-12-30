from flask import Blueprint, request, jsonify
from app.services.parasha_service import get_parasha, list_parashot

bp = Blueprint('parasha', __name__, url_prefix='/api/parasha')

@bp.route('/', methods=['GET'])
def get_parasha_by_name():
    name = request.args.get('name')
    if not name:
        return jsonify({'error': 'Nome da parashá não fornecido'}), 400
    
    parasha = get_parasha(name)
    if not parasha:
        return jsonify({'error': 'Parashá não encontrada'}), 404
    
    return jsonify(parasha)

@bp.route('/list', methods=['GET'])
def get_parashot_list():
    parashot = list_parashot()
    return jsonify(parashot)
