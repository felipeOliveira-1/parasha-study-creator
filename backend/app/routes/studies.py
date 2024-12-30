import logging
from flask import Blueprint, jsonify, request, current_app
from ..services.study_service import generate_study, get_study_history

logger = logging.getLogger(__name__)
bp = Blueprint('studies', __name__, url_prefix='/api/studies')

@bp.route('/generate', methods=['POST'])
def create_study():
    """
    Gera um novo estudo baseado na parashá selecionada
    """
    try:
        logger.info("Received study generation request")
        data = request.get_json()
        logger.info(f"Request data: {data}")
        
        if not data:
            logger.error("No JSON data provided in request")
            return jsonify({
                'success': False,
                'error': 'Request data is required'
            }), 400
            
        parasha = data.get('parasha')
        logger.info(f"Parasha requested: {parasha}")
        
        if not parasha:
            logger.error("No parasha provided in request")
            return jsonify({
                'success': False,
                'error': 'Parasha name is required'
            }), 400
            
        study_type = data.get('study_type', 'default')
        logger.info(f"Study type requested: {study_type}")
        
        user_id = data.get('user_id')  # Optional for now
        logger.info(f"User ID provided: {user_id}")
        
        # Generate study
        study = generate_study(parasha, study_type, user_id)
        if not study:
            logger.error(f"Failed to generate study for parasha: {parasha}")
            return jsonify({
                'success': False,
                'error': 'Failed to generate study. Please try again.'
            }), 500
            
        logger.info("Study generated successfully")
        return jsonify({
            'success': True,
            'data': study
        })
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error generating study: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@bp.route('/history', methods=['GET'])
def get_history():
    """
    Recupera o histórico de estudos de um usuário
    """
    try:
        logger.info("Received study history request")
        user_id = request.args.get('user_id')
        logger.info(f"User ID provided: {user_id}")
        
        if not user_id:
            logger.error("No user ID provided in request")
            return jsonify({
                'success': False,
                'error': 'ID do usuário não fornecido'
            }), 400
            
        history = get_study_history(user_id)
        logger.info("Study history retrieved successfully")
        
        return jsonify({
            'success': True,
            'data': history
        })
        
    except Exception as e:
        logger.error(f"Error retrieving study history: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno ao recuperar histórico'
        }), 500
