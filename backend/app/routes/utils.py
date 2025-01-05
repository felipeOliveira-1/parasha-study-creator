from functools import wraps
from flask import jsonify
import logging
from datetime import datetime
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

def json_response(success: bool, data=None, error=None, status_code=200):
    response = {'success': success}
    if data:
        response['data'] = data
    if error:
        response['error'] = error
    return jsonify(response), status_code

def handle_errors(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return json_response(False, error=str(e), status_code=400)
        except ValidationError as e:
            logger.error(f"Schema validation error: {str(e)}")
            return json_response(False, error=str(e), status_code=400)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return json_response(False, error="Internal server error", status_code=500)
    return wrapper

def log_request(action: str, **kwargs):
    logger.info(f"[{datetime.now()}] {action} - {kwargs}")

class StudyRequest(BaseModel):
    parasha: str
    study_type: str = 'default'
    user_id: str | None = None
