import os
import logging
import json
import hashlib
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_community.document_loaders import PyPDFLoader
from supabase.client import create_client
from tqdm import tqdm

# Carrega variáveis de ambiente
from dotenv import load_dotenv
load_dotenv()

# Configuração básica do logging
pdf_logger = logging.getLogger('pdf_processor')

class PDFProcessor:
    def __init__(self, pdf_dir: str):
        """
        Inicializa o processador de PDF.
        
        Args:
            pdf_dir (str): Diretório contendo os PDFs
        """
        self.pdf_dir = pdf_dir
        self.version_file = "pdf_version.json"
        
        # Configuração do Supabase
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL e SUPABASE_SERVICE_KEY devem estar definidos nas variáveis de ambiente")
            
        try:
            self.supabase_client = create_client(supabase_url, supabase_key)
            self.embeddings = OpenAIEmbeddings()
        except Exception as e:
            pdf_logger.error(f"Erro ao inicializar clientes: {e}")
            raise
            
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # Reduzido para melhor granularidade
            chunk_overlap=200,  # Aumentado para manter mais contexto
            length_function=len,
        )

    @staticmethod
    def setup_logging():
        """Configura o logger do processador de PDF."""
        # Remove handlers existentes
        pdf_logger = logging.getLogger('pdf_processor')
        for handler in pdf_logger.handlers[:]:
            pdf_logger.removeHandler(handler)
        
        # Configura novo handler
        file_handler = logging.FileHandler('pdf_processor.log', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        pdf_logger.addHandler(file_handler)
        
        # Adiciona handler para console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        pdf_logger.addHandler(console_handler)
        
        pdf_logger.setLevel(logging.INFO)

    def calculate_pdfs_hash(self) -> str:
        """
        Calcula um hash que representa o estado atual dos PDFs.
        """
        pdf_files = sorted([f for f in os.listdir(self.pdf_dir) if f.endswith('.pdf')])
        
        # Combina os nomes dos arquivos e seus tamanhos
        pdf_info = []
        for filename in pdf_files:
            path = os.path.join(self.pdf_dir, filename)
            size = os.path.getsize(path)
            modified_time = os.path.getmtime(path)
            pdf_info.append(f"{filename}:{size}:{modified_time}")
        
        # Cria um hash da informação combinada
        return hashlib.md5(":".join(pdf_info).encode()).hexdigest()

    def load_version(self) -> str:
        """
        Carrega a versão anterior dos PDFs processados.
        """
        try:
            if os.path.exists(self.version_file):
                with open(self.version_file, 'r') as f:
                    data = json.load(f)
                return data.get('hash', '')
        except Exception as e:
            pdf_logger.error(f"Erro ao carregar versão: {e}")
        return ''

    def save_version(self, hash_value: str):
        """
        Salva a versão atual dos PDFs processados.
        """
        try:
            with open(self.version_file, 'w') as f:
                json.dump({'hash': hash_value}, f)
        except Exception as e:
            pdf_logger.error(f"Erro ao salvar versão: {e}")
        
    def process_pdf(self, pdf_path: str) -> List[str]:
        """
        Processa um único arquivo PDF e retorna seus chunks de texto.
        
        Args:
            pdf_path (str): Caminho para o arquivo PDF
            
        Returns:
            List[str]: Lista de chunks de texto do PDF
        """
        try:
            print(f"\nProcessando: {os.path.basename(pdf_path)}")
            loader = PyPDFLoader(pdf_path)
            pages = loader.load()
            if not pages:
                print(f"  - Aviso: Nenhuma página encontrada em {os.path.basename(pdf_path)}")
                return []
                
            print(f"  - {len(pages)} páginas encontradas")
            chunks = self.text_splitter.split_documents(pages)
            print(f"  - {len(chunks)} chunks gerados")
            return chunks
        except Exception as e:
            pdf_logger.error(f"Erro ao processar PDF {pdf_path}: {e}")
            print(f"  - ERRO: {e}")
            return []

    def process_all_pdfs(self) -> List[Dict]:
        """
        Processa todos os PDFs no diretório.
        
        Returns:
            List[Dict]: Lista de documentos processados
        """
        all_chunks = []
        pdf_files = [f for f in os.listdir(self.pdf_dir) if f.endswith('.pdf')]
        
        print(f"\nEncontrados {len(pdf_files)} arquivos PDF para processar")
        
        for filename in tqdm(pdf_files, desc="Processando PDFs"):
            pdf_path = os.path.join(self.pdf_dir, filename)
            chunks = self.process_pdf(pdf_path)
            # Adiciona metadados sobre a fonte
            for chunk in chunks:
                if chunk is not None:  # Verifica se o chunk é válido
                    chunk.metadata['source'] = filename
                    # Remove a extensão .pdf do nome do arquivo para melhor apresentação
                    chunk.metadata['source_display'] = filename.replace('.pdf', '')
                    all_chunks.append(chunk)
            
        print(f"\nTotal de chunks gerados: {len(all_chunks)}")
        return all_chunks

    def create_vector_store(self) -> SupabaseVectorStore:
        """
        Cria ou retorna o vector store no Supabase.
        
        Returns:
            SupabaseVectorStore: Instância do vector store
        """
        try:
            vector_store = SupabaseVectorStore(
                client=self.supabase_client,
                embedding=self.embeddings,
                table_name="documents",  # Nome da tabela no Supabase
                query_name="match_documents"  # Nome da função de busca no Supabase
            )
            
            # Verifica se os PDFs mudaram desde o último processamento
            current_hash = self.calculate_pdfs_hash()
            previous_hash = self.load_version()
            
            if current_hash == previous_hash:
                print("\nPDFs não foram modificados desde o último processamento.")
                print("Usando embeddings existentes...")
                return vector_store
            
            print("\nMudanças detectadas nos PDFs. Reprocessando...")
            
            # Limpa a tabela antes de adicionar novos documentos
            print("\nLimpando dados anteriores...")
            try:
                # Primeiro, obtém todos os IDs
                response = self.supabase_client.table("documents").select("id").execute()
                if response.data:
                    ids = [record['id'] for record in response.data]
                    
                    # Deleta em lotes de 100
                    batch_size = 100
                    for i in range(0, len(ids), batch_size):
                        batch_ids = ids[i:i + batch_size]
                        self.supabase_client.table("documents").delete().in_("id", batch_ids).execute()
                        print(f"  - Deletados {min(i + batch_size, len(ids))} de {len(ids)} registros")
            except Exception as e:
                pdf_logger.error(f"Erro ao limpar dados: {str(e)}")
                raise
            
            # Processa todos os PDFs e adiciona ao Supabase
            print("\nProcessando documentos...")
            documents = self.process_all_pdfs()
            
            if not documents:
                raise ValueError("Nenhum documento foi processado com sucesso")
                
            print(f"\nGerando embeddings e salvando no Supabase ({len(documents)} chunks)...")
            print("Este processo pode demorar alguns minutos dependendo da quantidade de texto...")
            
            # Adiciona os documentos em lotes para melhor feedback
            batch_size = 50
            for i in tqdm(range(0, len(documents), batch_size), desc="Salvando no Supabase"):
                batch = documents[i:i + batch_size]
                vector_store.add_documents(batch)
            
            print("\nTodos os documentos foram salvos com sucesso!")
            
            # Salva a nova versão
            self.save_version(current_hash)
            
            return vector_store
            
        except Exception as e:
            pdf_logger.error(f"Erro ao criar/acessar vector store: {e}")
            raise

    def clear_supabase_data(self):
        """Limpa todos os dados da tabela documents no Supabase."""
        try:
            # Conta total de registros
            count_response = self.supabase_client.table('documents').select('id', count='exact').execute()
            total_records = count_response.count if count_response.count is not None else 0
            
            print(f"\nTotal de registros a serem deletados: {total_records}")
            if total_records == 0:
                print("Nenhum registro para deletar.")
                return
                
            print("\nIniciando limpeza dos dados...")
            deleted_count = 0
            
            while True:
                # Busca 500 registros por vez
                response = self.supabase_client.table('documents').select('id').limit(500).execute()
                if not response.data:
                    break
                
                ids = [row['id'] for row in response.data]
                # Deleta os registros em um único lote
                self.supabase_client.table('documents').delete().in_('id', ids).execute()
                deleted_count += len(ids)
                print(f"  - Progresso: {deleted_count}/{total_records} registros deletados ({(deleted_count/total_records*100):.1f}%)")
                
            print("\nLimpeza concluída com sucesso!")
            logging.info("Dados do Supabase limpos com sucesso")
        except Exception as e:
            logging.error(f"Erro ao limpar dados do Supabase: {e}")
            raise

    def query_similar_content(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Busca conteúdo similar nos PDFs processados.
        
        Args:
            query (str): Texto para buscar
            n_results (int): Número de resultados a retornar
            
        Returns:
            List[Dict]: Lista de documentos similares
        """
        try:
            vector_store = self.create_vector_store()
            print("\nBuscando conteúdo similar...")
            
            # Busca mais resultados e inclui scores
            results_with_scores = vector_store.similarity_search_with_relevance_scores(query, k=n_results)
            
            if not results_with_scores:
                print("Nenhum resultado encontrado.")
                return []
                
            # Formata os resultados
            formatted_results = []
            for doc, score in results_with_scores:
                # O score já vem como uma porcentagem de similaridade
                similarity_percentage = score * 100
                
                # Só inclui resultados com similaridade acima de 50%
                if similarity_percentage > 50:
                    formatted_results.append({
                        'content': doc.page_content,
                        'source': doc.metadata['source_display'],
                        'page': doc.metadata.get('page', 0),
                        'similarity_score': similarity_percentage
                    })
            
            # Ordena por similaridade
            formatted_results.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            print(f"Encontrados {len(formatted_results)} resultados relevantes.")
            
            return formatted_results
        except Exception as e:
            pdf_logger.error(f"Erro ao buscar conteúdo similar: {str(e)}", exc_info=True)
            raise
