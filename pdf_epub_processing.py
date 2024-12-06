import os
import logging
from typing import List, Dict, Optional
from ebooklib import epub
from bs4 import BeautifulSoup
import html2text

class DocumentProcessor:
    def __init__(self, documents_folder: str):
        """
        Inicializa o processador de documentos.
        
        Args:
            documents_folder: Pasta contendo os documentos a serem processados
        """
        self.documents_folder = documents_folder
        self.logger = logging.getLogger(__name__)
        os.makedirs(documents_folder, exist_ok=True)

    def process_pdf(self, file_path: str) -> str:
        """
        Processa um arquivo PDF e retorna seu conteúdo como texto.
        
        Args:
            file_path: Caminho para o arquivo PDF
            
        Returns:
            str: Conteúdo do PDF como texto
        """
        try:
            with open(file_path, 'rb') as file:
                content = file.read()
                return content.decode('utf-8', errors='ignore')
        except Exception as e:
            self.logger.error(f"Erro ao processar PDF {file_path}: {str(e)}")
            return ""

    def process_epub(self, epub_path: str, chunk_size: int = 1000) -> List[Dict]:
        """
        Processa um arquivo EPUB e retorna uma lista de chunks de texto.
        
        Args:
            epub_path: Caminho para o arquivo EPUB
            chunk_size: Tamanho aproximado de cada chunk em caracteres
            
        Returns:
            List[Dict]: Lista de dicionários com o texto dividido em chunks e metadados
        """
        try:
            book = epub.read_epub(epub_path)
            
            title = book.get_metadata('DC', 'title')[0][0] if book.get_metadata('DC', 'title') else "Unknown"
            author = book.get_metadata('DC', 'creator')[0][0] if book.get_metadata('DC', 'creator') else "Unknown"
            
            h = html2text.HTML2Text()
            h.ignore_links = True
            h.ignore_images = True
            
            chunks = []
            current_chunk = ""
            chapter_number = 0
            
            for item in book.get_items():
                if item.get_type() == epub.ITEM_DOCUMENT:
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    text = h.handle(str(soup))
                    
                    text = "\n".join(line.strip() for line in text.split("\n") if line.strip())
                    
                    words = text.split()
                    for word in words:
                        current_chunk += word + " "
                        
                        if len(current_chunk) >= chunk_size:
                            chunks.append({
                                "content": current_chunk.strip(),
                                "source": f"{title} - Chapter {chapter_number}",
                                "metadata": {
                                    "title": title,
                                    "author": author,
                                    "chapter": chapter_number,
                                    "type": "epub"
                                }
                            })
                            current_chunk = ""
                            chapter_number += 1
            
            if current_chunk:
                chunks.append({
                    "content": current_chunk.strip(),
                    "source": f"{title} - Chapter {chapter_number}",
                    "metadata": {
                        "title": title,
                        "author": author,
                        "chapter": chapter_number,
                        "type": "epub"
                    }
                })
            
            return chunks
        
        except Exception as e:
            self.logger.error(f"Erro ao processar EPUB: {str(e)}")
            raise

    def query_similar_content(self, query: str) -> List[Dict]:
        """
        Busca conteúdo similar à query nos documentos processados.
        
        Args:
            query: Query para buscar
            
        Returns:
            List[Dict]: Lista de resultados encontrados
        """
        # TODO: Implementar busca semântica nos documentos
        # Por enquanto, retorna uma lista vazia
        return []
