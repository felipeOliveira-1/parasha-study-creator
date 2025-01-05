import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from .parasha_service import get_parasha
from .prompts import (
    get_parasha_summary_prompt,
    get_themes_extraction_prompt,
    get_study_topics_prompt,
    get_mussar_prompt
)
from flask import current_app

logger = logging.getLogger(__name__)

def get_openai_client() -> OpenAI:
    """
    Retorna um cliente OpenAI configurado
    """
    api_key = current_app.config['OPENAI_API_KEY']
    return OpenAI(api_key=api_key)

def generate_study(parasha_name: str, study_type: str = 'default', user_id: Optional[str] = None) -> Dict:
    """
    Gera um novo estudo baseado na parashá
    """
    try:
        parasha = get_parasha(parasha_name)
        if not parasha:
            raise ValueError(f"Parashá '{parasha_name}' não encontrada")
        
        client = get_openai_client()
        study_content = generate_study_topics(parasha['text'], client)
        
        study = {
            'parasha': parasha_name,
            'type': study_type,
            'content': study_content,
            'created_at': datetime.now().isoformat()
        }
        
        return study
    
    except Exception as e:
        logger.error(f"Erro ao gerar estudo: {str(e)}")
        raise

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def _call_openai(messages: List[Dict], client: OpenAI) -> str:
    response = client.chat.completions.create(
        model=current_app.config.get('OPENAI_MODEL', 'gpt-4o'),
        messages=messages,
        temperature=0.13,
        max_tokens=5000,
        timeout=30  # Adicionar timeout
    )
    return response.choices[0].message.content

def generate_study_topics(parasha_text: str, client: OpenAI, references: List[Dict] = None) -> Dict:
    """
    Gera tópicos de estudo baseados no texto da parashá
    """
    try:
        summary = _call_openai(get_parasha_summary_prompt(parasha_text), client)
        themes = _call_openai(get_themes_extraction_prompt(summary), client)
        topics = _call_openai(get_study_topics_prompt(summary, references), client)
        mussar = _call_openai(get_mussar_prompt(topics, references), client)

        return {
            'summary': summary,
            'themes': themes,
            'topics': topics,
            'mussar_analysis': mussar,
            'references': references or [],
            'generated_at': datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to generate study topics: {str(e)}")
        raise

def get_study_history(user_id: str) -> List[Dict]:
    """
    Recupera o histórico de estudos de um usuário
    """
    try:
        # TO DO: implementar lógica para recuperar histórico de estudos
        return []
    except Exception as e:
        logger.error(f"Erro ao recuperar histórico: {str(e)}")
        raise
