"""
Módulo para gerenciar comentários rabínicos clássicos do Sefaria.
"""

import requests
import logging
from typing import List, Dict, Optional
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
        self.base_url = "https://www.sefaria.org/api/texts/"
        
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
                
                # Busca o comentário completo do comentarista para a parashá
                try:
                    response = requests.get(f"{self.base_url}{commentator} on {parasha_name}")
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('he') or data.get('text'):
                            commentaries[commentator].append({
                                'commentator': commentator,
                                'period': info['period'],
                                'text': data.get('text', ''),
                                'he': data.get('he', ''),
                                'ref': f"{commentator} on {parasha_name}"
                            })
                            
                except Exception as e:
                    self.logger.error(f"Erro ao buscar comentário de {commentator} para {parasha_name}: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Erro ao buscar comentários clássicos: {str(e)}")
            
        return {k: v for k, v in commentaries.items() if v}  # Remove comentaristas sem comentários
        
    def get_commentary_by_ref(self, ref: str) -> Optional[Dict]:
        """
        Busca um comentário específico por sua referência no Sefaria.
        
        Args:
            ref: Referência do comentário no formato Sefaria
            
        Returns:
            Optional[Dict]: Comentário e metadados se encontrado
        """
        try:
            response = requests.get(f"{self.base_url}{ref}")
            if response.status_code == 200:
                data = response.json()
                
                # Extrai o nome do comentarista da referência
                commentator = ref.split(" on ")[0]
                info = self.classic_commentators.get(commentator, {})
                
                return {
                    'commentator': commentator,
                    'period': info.get('period', 'Unknown'),
                    'text': data.get('text', ''),
                    'he': data.get('he', ''),
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
