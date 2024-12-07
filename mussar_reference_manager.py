import logging
from typing import List, Dict
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore

class MussarReferenceManager:
    """Gerencia a busca de referências do Mussar usando a base vetorial."""
    
    def __init__(self, supabase_client):
        """
        Inicializa o gerenciador de referências Mussar.
        
        Args:
            supabase_client: Cliente Supabase configurado
        """
        self.vector_store = SupabaseVectorStore(
            client=supabase_client,
            embedding=OpenAIEmbeddings(),
            table_name="documents"  # Usa a tabela existente
        )
        self.logger = logging.getLogger(__name__)

    def search_relevant_citations(self, topic: str, n_results: int = 3) -> List[Dict]:
        """
        Busca citações relevantes do Mussar para um tópico específico.
        
        Args:
            topic: Tópico para buscar citações relevantes
            n_results: Número de resultados a retornar
            
        Returns:
            Lista de citações relevantes com suas fontes
        """
        try:
            results = self.vector_store.similarity_search_with_score(
                topic,
                k=n_results
            )
            
            return [
                {
                    "source": doc.metadata.get("source", "Unknown"),
                    "citation": doc.page_content,
                    "relevance_score": score
                }
                for doc, score in results
            ]
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar citações: {str(e)}")
            return []  # Retorna lista vazia em caso de erro
