import logging
from flask import Blueprint, request
from ..services.study_service import generate_study, get_study_history
from .utils import json_response, handle_errors, log_request, StudyRequest

logger = logging.getLogger(__name__)
bp = Blueprint('studies', __name__, url_prefix='/api/studies')

@bp.route('/generate', methods=['POST'])
@handle_errors
def create_study():
    """
    Gera um novo estudo baseado na parashá selecionada
    """
    log_request("study_generation_start")
    data = StudyRequest(**request.get_json())
    log_request("study_generation_data", **data.dict())
    
    study = generate_study(data.parasha, data.study_type, data.user_id)
    if not study:
        log_request("study_generation_failed", parasha=data.parasha)
        return json_response(False, error='Failed to generate study. Please try again.', status_code=500)
        
    log_request("study_generation_success", parasha=data.parasha)
    return json_response(True, data=study)

@bp.route('/history', methods=['GET'])
@handle_errors
def get_history():
    """
    Recupera o histórico de estudos de um usuário
    """
    log_request("study_history_request")
    user_id = request.args.get('user_id')
    
    if not user_id:
        log_request("study_history_missing_user_id")
        return json_response(False, error='ID do usuário não fornecido', status_code=400)
        
    history = get_study_history(user_id)
    log_request("study_history_success", user_id=user_id)
    return json_response(True, data=history)
