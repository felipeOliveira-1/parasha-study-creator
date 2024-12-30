import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from openai import OpenAI
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

def generate_study_topics(parasha_text: str, client: OpenAI, references: List[Dict] = None, retries: int = 3) -> Dict:
    """
    Gera tópicos de estudo baseados no texto da parashá
    """
    try:
        # Gera um resumo da parashá
        summary_messages = get_parasha_summary_prompt(parasha_text)
        summary_response = client.chat.completions.create(
            model=current_app.config.get('OPENAI_MODEL', 'gpt-4o'),
            messages=summary_messages,
            temperature=0.7,
            max_tokens=500
        )
        summary = summary_response.choices[0].message.content

        # Extrai os principais temas
        themes_messages = get_themes_extraction_prompt(summary)
        themes_response = client.chat.completions.create(
            model=current_app.config.get('OPENAI_MODEL', 'gpt-4o'),
            messages=themes_messages,
            temperature=0.7,
            max_tokens=300
        )
        themes = themes_response.choices[0].message.content

        # Gera tópicos de estudo
        topics_messages = get_study_topics_prompt(summary, references)
        topics_response = client.chat.completions.create(
            model=current_app.config.get('OPENAI_MODEL', 'gpt-4o'),
            messages=topics_messages,
            temperature=0.7,
            max_tokens=1000  # Aumentado para acomodar 3 tópicos detalhados
        )
        topics = topics_response.choices[0].message.content

        # Análise Mussar
        mussar_messages = get_mussar_prompt(topics, references)
        mussar_response = client.chat.completions.create(
            model=current_app.config.get('OPENAI_MODEL', 'gpt-4o'),
            messages=mussar_messages,
            temperature=0.7,
            max_tokens=800  # Aumentado para análise Mussar detalhada
        )
        mussar = mussar_response.choices[0].message.content

        return {
            'summary': summary,
            'themes': themes,
            'topics': topics,
            'mussar_analysis': mussar,
            'references': references or [],
            'generated_at': datetime.now().isoformat()
        }

    except Exception as e:
        if retries > 0:
            logger.warning(f"Error generating study topics, retrying... ({retries} attempts left)")
            return generate_study_topics(parasha_text, client, references, retries - 1)
        else:
            logger.error(f"Failed to generate study topics after all retries: {str(e)}")
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
