"""
Serviço para gerenciar comentários rabínicos clássicos do Sefaria.
"""

import requests
import logging
import time
from typing import List, Dict, Optional, Union
from functools import lru_cache
from flask import current_app

logger = logging.getLogger(__name__)

# Lista de comentaristas clássicos principais
CLASSIC_COMMENTATORS = {
    "Rashi": {
        "categories": ["Commentary", "Tanakh", "Torah"],
        "period": "Rishonim",
        "priority": 1
    },
    "Ramban": {
        "categories": ["Commentary", "Tanakh", "Torah"],
        "period": "Rishonim",
        "priority": 2
    },
    "Ibn Ezra": {
        "categories": ["Commentary", "Tanakh", "Torah"],
        "period": "Rishonim",
        "priority": 3
    },
    "Sforno": {
        "categories": ["Commentary", "Tanakh", "Torah"],
        "period": "Rishonim",
        "priority": 4
    },
    "Or HaChaim": {
        "categories": ["Commentary", "Tanakh", "Torah"],
        "period": "Acharonim",
        "priority": 5
    },
    "Rashbam": {
        "categories": ["Commentary", "Tanakh", "Torah"],
        "period": "Rishonim",
        "priority": 6
    },
    "Kli Yakar": {
        "categories": ["Commentary", "Tanakh", "Torah"],
        "period": "Acharonim",
        "priority": 7
    }
}

def _validate_ref(ref: str) -> bool:
    """
    Valida se uma referência do Sefaria está em formato válido.
    """
    if not ref or not isinstance(ref, str):
        return False
        
    # Verifica se contém um comentarista válido
    has_valid_commentator = any(c in ref for c in CLASSIC_COMMENTATORS)
    
    # Verifica formato básico
    has_on = " on " in ref
    
    # Verifica formato de versículo (pode incluir ranges como 1-3)
    has_verse = any(char.isdigit() for char in ref)
    
    return has_valid_commentator and has_on and has_verse

def _process_text_content(data: Dict) -> tuple[str, str]:
    """
    Processa o conteúdo do texto retornado pela API.
    """
    def normalize_text(content: Union[str, list, None]) -> str:
        if content is None:
            return ""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return ' '.join([normalize_text(item) for item in content])
        return str(content)

    en_text = normalize_text(data.get('text', ''))
    he_text = normalize_text(data.get('he', ''))
    
    return en_text, he_text

def get_commentaries(reference: str, max_commentators: int = 3) -> Dict[str, Dict[str, str]]:
    """
    Busca comentários rabínicos clássicos do Sefaria para uma referência específica.
    
    Args:
        reference: Referência bíblica (ex: "Genesis 32:28")
        max_commentators: Número máximo de comentaristas a retornar
        
    Returns:
        dict: Dicionário com comentários por comentarista
    """
    base_url = "https://www.sefaria.org/api/v3/texts/"
    commentaries = {}
    
    try:
        # Ordena comentaristas por prioridade
        sorted_commentators = sorted(
            CLASSIC_COMMENTATORS.items(),
            key=lambda x: x[1]['priority']
        )[:max_commentators]
        
        for commentator, info in sorted_commentators:
            # Constrói a referência do comentário
            commentary_ref = f"{commentator} on {reference}"
            
            if not _validate_ref(commentary_ref):
                logger.warning(f"Referência inválida: {commentary_ref}")
                continue
            
            # Faz a requisição à API
            url = f"{base_url}{commentary_ref}?context=0&pad=0"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                en_text, he_text = _process_text_content(data)
                
                if en_text or he_text:
                    commentaries[commentator] = {
                        'en': en_text,
                        'he': he_text,
                        'period': info['period']
                    }
            
            # Delay para evitar sobrecarregar a API
            time.sleep(0.1)
            
    except Exception as e:
        logger.error(f"Erro ao buscar comentários: {str(e)}")
    
    return commentaries

def translate_commentaries(commentaries: Dict[str, Dict[str, str]], client) -> Dict[str, Dict[str, str]]:
    """
    Traduz os comentários do inglês para português usando a OpenAI.
    """
    translated = {}
    
    try:
        for commentator, content in commentaries.items():
            en_text = content.get('en', '')
            if not en_text:
                continue
                
            completion = client.chat.completions.create(
                model=current_app.config.get('OPENAI_MODEL', 'gpt-4o'),
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um tradutor especializado em textos judaicos. "
                                 "Traduza o comentário rabínico do inglês para o português, "
                                 "mantendo a precisão teológica e usando linguagem clara."
                    },
                    {
                        "role": "user",
                        "content": f"Traduza o seguinte comentário de {commentator}:\n\n{en_text}"
                    }
                ]
            )
            
            translated[commentator] = {
                'en': en_text,
                'he': content.get('he', ''),
                'pt': completion.choices[0].message.content,
                'period': content.get('period')
            }
            
    except Exception as e:
        logger.error(f"Erro ao traduzir comentários: {str(e)}")
        
    return translated or commentaries  # Retorna original se tradução falhar

def format_commentaries(commentaries: Dict[str, Dict[str, str]], include_original: bool = False) -> str:
    """
    Formata os comentários rabínicos para exibição.
    """
    if not commentaries:
        return "Nenhum comentário encontrado."
        
    formatted = []
    for commentator, content in commentaries.items():
        period = content.get('period', '')
        pt_text = content.get('pt', content.get('en', ''))  # Usa inglês se português não disponível
        
        formatted.append(f"## {commentator} ({period})")
        formatted.append(pt_text)
        
        if include_original:
            he_text = content.get('he', '')
            en_text = content.get('en', '')
            if he_text:
                formatted.append(f"\nTexto original (hebraico):\n{he_text}")
            if en_text:
                formatted.append(f"\nTexto em inglês:\n{en_text}")
        
        formatted.append("\n---\n")
    
    return "\n".join(formatted)
