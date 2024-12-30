from flask import Blueprint, jsonify
from app.services.parasha_service import get_parasha, list_parashot

bp = Blueprint('parasha', __name__, url_prefix='/api/parashot')

@bp.route('/', methods=['GET'])
def list_all():
    """Lista todas as parashiot disponíveis"""
    try:
        parashot = list_parashot()
        return jsonify({
            'success': True,
            'data': parashot
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/<name>', methods=['GET'])
def get_one(name):
    """Retorna uma parashá específica"""
    try:
        parasha = get_parasha(name)
        if not parasha:
            return jsonify({
                'success': False,
                'error': 'Parashá não encontrada'
            }), 404
            
        return jsonify({
            'success': True,
            'data': parasha
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
