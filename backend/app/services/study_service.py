import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from openai import OpenAI
from .supabase_service import get_supabase_client
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
    parasha = get_parasha(parasha_name)
    if not parasha:
        raise ValueError(f"Parashá '{parasha_name}' não encontrada")
    
    client = get_openai_client()
    study_content = generate_study_topics(parasha['text'], client)
    
    study = {
        'parasha': parasha_name,
        'type': study_type,
        'content': study_content,
        'created_at': datetime.now().isoformat(),
        'user_id': user_id
    }
    
    # Salvar o estudo no Supabase
    supabase = get_supabase_client()
    response = supabase.table('studies').insert(study).execute()
    return response.data[0]

def generate_study_topics(parasha_text: str, client: OpenAI, references: List[Dict] = None, retries: int = 3) -> Dict:
    """
    Gera tópicos de estudo baseados no texto da parashá
    """
    try:
        # Gera um resumo do texto da parashá
        completion = client.chat.completions.create(
            model=current_app.config.get('OPENAI_MODEL', 'gpt-4o'),
            messages=get_parasha_summary_prompt(parasha_text)
        )
        summary = completion.choices[0].message.content
        
        # Extrai temas principais
        themes_completion = client.chat.completions.create(
            model=current_app.config.get('OPENAI_MODEL', 'gpt-4o'),
            messages=get_themes_extraction_prompt(summary)
        )
        themes = themes_completion.choices[0].message.content
        
        # Gera os tópicos de estudo
        topics_completion = client.chat.completions.create(
            model=current_app.config.get('OPENAI_MODEL', 'gpt-4o'),
            messages=get_study_topics_prompt(summary, references)
        )
        topics = topics_completion.choices[0].message.content
        
        # Se houver referências, gera análise Mussar adicional
        mussar_analysis = None
        if references:
            mussar_completion = client.chat.completions.create(
                model=current_app.config.get('OPENAI_MODEL', 'gpt-4o'),
                messages=get_mussar_prompt(topics, references)
            )
            mussar_analysis = mussar_completion.choices[0].message.content
        
        return {
            "summary": summary,
            "themes": themes,
            "topics": topics,
            "mussar_analysis": mussar_analysis,
            "references": references if references else []
        }

    except Exception as e:
        logger.error(f"Erro ao gerar estudo: {str(e)}")
        if retries > 0:
            logger.info(f"Tentando novamente... ({retries} tentativas restantes)")
            return generate_study_topics(parasha_text, client, references, retries - 1)
        raise

def get_study_history(user_id: str) -> List[Dict]:
    """
    Recupera o histórico de estudos de um usuário
    """
    supabase = get_supabase_client()
    response = supabase.table('studies').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
    return response.data
