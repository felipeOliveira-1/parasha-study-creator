"""
Módulo para gerenciar comentários rabínicos clássicos do Sefaria.
"""

import requests
import logging
import time
from typing import List, Dict, Optional, Union
from functools import lru_cache
from sefaria_index import SefariaIndex

class CommentariesManager:
    def __init__(self, sefaria_index: SefariaIndex = None):
        """
        Inicializa o gerenciador de comentários rabínicos.
        
        Args:
            sefaria_index: Instância do SefariaIndex para acessar o índice
        """
        self.logger = logging.getLogger(__name__)
        self.sefaria_index = sefaria_index or SefariaIndex()
        self.base_url = "https://www.sefaria.org/api/v3/texts/"
        self.request_delay = 0.1  # 100ms delay between requests
        
        # Lista de comentaristas clássicos principais
        self.classic_commentators = {
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
        
    def _validate_ref(self, ref: str) -> bool:
        """
        Valida se uma referência do Sefaria está em formato válido.
        
        Args:
            ref: Referência a ser validada
            
        Returns:
            bool: True se a referência é válida
        """
        if not ref or not isinstance(ref, str):
            return False
            
        # Verifica se contém um comentarista válido
        has_valid_commentator = any(c in ref for c in self.classic_commentators)
        
        # Verifica formato básico
        has_on = " on " in ref
        
        # Verifica formato de versículo (pode incluir ranges como 1-3)
        has_verse = any(char.isdigit() for char in ref)
        
        return has_valid_commentator and has_on and has_verse
        
    def _process_text_content(self, data: Dict) -> tuple[str, str]:
        """
        Processa o conteúdo do texto retornado pela API.
        
        Args:
            data: Dados do texto da API
            
        Returns:
            tuple[str, str]: Texto em inglês e hebraico processados
        """
        def normalize_text(content: Union[str, list, None]) -> str:
            if content is None:
                return ''
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                # Remove None values and empty strings
                filtered = [str(item) for item in content if item]
                # Handle nested lists
                result = []
                for item in filtered:
                    if isinstance(item, list):
                        result.extend(str(subitem) for subitem in item if subitem)
                    else:
                        result.append(item)
                return '\n'.join(result)
            return str(content)
            
        # Extrai texto e texto em hebraico
        text = normalize_text(data.get('text'))
        he_text = normalize_text(data.get('he'))
            
        return text, he_text
        
    @lru_cache(maxsize=128)
    def _fetch_text(self, ref: str) -> Optional[Dict]:
        """
        Busca texto do Sefaria com cache.
        
        Args:
            ref: Referência do texto
            
        Returns:
            Optional[Dict]: Dados do texto ou None se não encontrado
        """
        if not self._validate_ref(ref):
            self.logger.warning(f"Referência inválida: {ref}")
            return None
            
        try:
            time.sleep(self.request_delay)  # Rate limiting
            
            # Adiciona parâmetros para melhorar a resposta
            params = {
                'context': 0,  # Não inclui contexto extra
                'commentary': 0,  # Não inclui comentários aninhados
                'version': None  # Usa versão padrão
            }
            
            response = requests.get(
                f"{self.base_url}{ref}",
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                self.logger.warning(f"Texto não encontrado: {ref}")
                return None
            else:
                self.logger.error(
                    f"Erro ao buscar texto {ref}. "
                    f"Status code: {response.status_code}"
                )
                return None
                
        except requests.RequestException as e:
            self.logger.error(f"Erro de requisição para {ref}: {str(e)}")
            return None
            
    def get_commentaries_for_parasha(self, parasha_name: str, limit_per_commentator: int = 3) -> Dict[str, List[Dict]]:
        """
        Busca comentários clássicos para uma parashá específica.
        
        Args:
            parasha_name: Nome da parashá em inglês
            limit_per_commentator: Número máximo de comentários por comentarista
            
        Returns:
            Dict[str, List[Dict]]: Dicionário mapeando comentaristas aos seus comentários
        """
        commentaries = {}
        
        try:
            for commentator, info in self.classic_commentators.items():
                commentaries[commentator] = []
                ref = f"{commentator} on {parasha_name}"
                
                data = self._fetch_text(ref)
                if not data:
                    continue
                    
                text, he_text = self._process_text_content(data)
                
                if text or he_text:
                    commentaries[commentator].append({
                        'commentator': commentator,
                        'period': info['period'],
                        'text': text,
                        'he': he_text,
                        'ref': ref
                    })
                    
        except Exception as e:
            self.logger.error(f"Erro ao buscar comentários clássicos: {str(e)}")
            
        return {k: v for k, v in commentaries.items() if v}
        
    def get_commentary_by_ref(self, ref: str) -> Optional[Dict]:
        """
        Busca um comentário específico por sua referência no Sefaria.
        
        Args:
            ref: Referência do comentário no formato Sefaria
            
        Returns:
            Optional[Dict]: Comentário e metadados se encontrado
        """
        try:
            data = self._fetch_text(ref)
            if not data:
                return None
                
            commentator = ref.split(" on ")[0]
            info = self.classic_commentators.get(commentator, {})
            text, he_text = self._process_text_content(data)
            
            return {
                'commentator': commentator,
                'period': info.get('period', 'Unknown'),
                'text': text,
                'he': he_text,
                'ref': ref
            }
        except Exception as e:
            self.logger.error(f"Erro ao buscar comentário {ref}: {str(e)}")
        return None
        
    def get_available_commentators(self) -> List[Dict]:
        """
        Retorna lista de todos os comentaristas clássicos disponíveis.
        
        Returns:
            List[Dict]: Lista de comentaristas com seus metadados
        """
        return [
            {
                'name': commentator,
                'period': info['period'],
                'priority': info['priority']
            }
            for commentator, info in sorted(
                self.classic_commentators.items(),
                key=lambda x: x[1]['priority']
            )
        ]
