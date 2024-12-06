import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional

class ChatManager:
    def __init__(self, chat_history_folder: str):
        """
        Inicializa o gerenciador de chat.
        
        Args:
            chat_history_folder: Pasta onde serão salvos os históricos
        """
        self.chat_history_folder = chat_history_folder
        self.logger = logging.getLogger(__name__)
        os.makedirs(chat_history_folder, exist_ok=True)

    def save_chat_history(self, messages: List[Dict], conversation_name: Optional[str] = None) -> str:
        """
        Salva o histórico da conversa em um arquivo JSON.
        
        Args:
            messages: Lista de mensagens da conversa
            conversation_name: Nome opcional para a conversa
            
        Returns:
            str: Nome do arquivo onde a conversa foi salva
        """
        if not conversation_name:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            conversation_name = f"conversa_{timestamp}"
        
        if not conversation_name.endswith('.json'):
            conversation_name += '.json'
            
        filepath = os.path.join(self.chat_history_folder, conversation_name)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'messages': messages
                }, f, ensure_ascii=False, indent=2)
            return conversation_name
        except Exception as e:
            self.logger.error(f"Erro ao salvar histórico: {str(e)}")
            return None

    def load_chat_history(self, conversation_name: str) -> List[Dict]:
        """
        Carrega o histórico de uma conversa.
        
        Args:
            conversation_name: Nome do arquivo da conversa
            
        Returns:
            List[Dict]: Lista de mensagens da conversa
        """
        if not conversation_name.endswith('.json'):
            conversation_name += '.json'
            
        filepath = os.path.join(self.chat_history_folder, conversation_name)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data['messages']
        except Exception as e:
            self.logger.error(f"Erro ao carregar histórico: {str(e)}")
            return []

    def list_chat_histories(self) -> List[str]:
        """
        Lista todas as conversas salvas.
        
        Returns:
            List[str]: Lista de nomes dos arquivos de histórico
        """
        try:
            histories = [f for f in os.listdir(self.chat_history_folder) if f.endswith('.json')]
            return sorted(histories, reverse=True)  # Mais recentes primeiro
        except Exception as e:
            self.logger.error(f"Erro ao listar históricos: {str(e)}")
            return []

    def get_recent_messages(self, conversation_name: str, count: int = 6) -> List[Dict]:
        """
        Obtém as mensagens mais recentes de uma conversa.
        
        Args:
            conversation_name: Nome do arquivo da conversa
            count: Número de mensagens para retornar
            
        Returns:
            List[Dict]: Lista das últimas mensagens
        """
        messages = self.load_chat_history(conversation_name)
        return messages[-count:] if messages else []
