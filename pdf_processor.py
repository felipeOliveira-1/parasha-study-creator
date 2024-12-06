import logging
import json
import os
import hashlib
from typing import List, Dict, Any
import warnings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import SupabaseVectorStore
from langchain.schema import Document
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from supabase.client import create_client
from tqdm import tqdm

# Carrega variáveis de ambiente
from dotenv import load_dotenv
load_dotenv()

# Configura logging
pdf_logger = logging.getLogger('pdf_processor')

# Silencia avisos específicos do ebooklib
warnings.filterwarnings('ignore', category=UserWarning, module='ebooklib.epub')
warnings.filterwarnings('ignore', category=FutureWarning, module='ebooklib.epub')

class PDFProcessor:
    """Classe para processar PDFs e criar embeddings."""
    
    def __init__(self, pdf_dir: str):
        """
        Inicializa o processador de PDFs.
        
        Args:
            pdf_dir (str): Diretório onde os PDFs estão armazenados
        """
        self.pdf_dir = pdf_dir
        self.version_file = "processed_files.json"
        
        # Configuração do Supabase
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL e SUPABASE_SERVICE_KEY devem estar definidos nas variáveis de ambiente")
            
        try:
            self.supabase_client = create_client(supabase_url, supabase_key)
            self.embeddings = OpenAIEmbeddings()
        except Exception as e:
            raise ValueError(f"Erro ao conectar com Supabase: {str(e)}")
            
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

    def get_processed_files(self):
        """Carrega a lista de arquivos já processados."""
        if os.path.exists(self.version_file):
            with open(self.version_file, 'r') as f:
                return json.load(f)
        return {}

    def save_processed_files(self, processed_files):
        """Salva a lista de arquivos processados."""
        with open(self.version_file, 'w') as f:
            json.dump(processed_files, f)

    def check_new_files(self):
        """
        Verifica se há novos arquivos para processar.
        
        Returns:
            tuple: (bool, list) - (há novos arquivos?, lista de novos arquivos)
        """
        processed_files = self.get_processed_files()
        current_files = []
        new_files = []
        
        # Lista todos os arquivos no diretório
        for root, _, files in os.walk(self.pdf_dir):
            for file in files:
                if file.lower().endswith(('.pdf', '.epub')):
                    file_path = os.path.join(root, file)
                    current_files.append(file_path)
                    
                    # Verifica se o arquivo é novo ou foi modificado
                    mtime = os.path.getmtime(file_path)
                    if file_path not in processed_files or mtime > processed_files[file_path]:
                        new_files.append(file_path)
        
        return len(new_files) > 0, new_files

    def create_vector_store(self):
        """
        Cria ou atualiza o vector store no Supabase.
        """
        has_new_files, new_files = self.check_new_files()
        
        if not has_new_files:
            print("\nNenhum arquivo novo encontrado.")
            print("Base de dados está atualizada.")
            return
        
        print(f"\nEncontrados {len(new_files)} novos arquivos para processar:")
        for file in new_files:
            print(f"  - {os.path.basename(file)}")
        
        # Processa apenas os novos arquivos
        processed_files = self.get_processed_files()
        
        # Inicializa o SupabaseVectorStore uma única vez
        vector_store = SupabaseVectorStore(
            client=self.supabase_client,
            embedding=self.embeddings,
            table_name="documents",
            query_name="match_documents"
        )
        
        for file_path in new_files:
            print(f"\nProcessando: {os.path.basename(file_path)}")
            try:
                if file_path.lower().endswith('.pdf'):
                    chunks = self.process_pdf(file_path)
                else:  # .epub
                    chunks = self.process_epub(file_path)
                
                if not chunks:
                    print(f"  - AVISO: Nenhum chunk gerado para {os.path.basename(file_path)}")
                    continue
                
                # Converte chunks para o formato Document do Langchain
                documents = []
                for chunk in chunks:
                    doc = Document(
                        page_content=chunk["content"],
                        metadata=chunk["metadata"]
                    )
                    documents.append(doc)
                
                # Adiciona chunks ao Supabase em lotes
                print(f"  - Adicionando {len(documents)} chunks ao Supabase...")
                try:
                    vector_store.add_documents(documents)
                    print(f"  - {len(documents)} chunks adicionados ao Supabase")
                except Exception as e:
                    print(f"  - ERRO ao adicionar chunks: {str(e)}")
                    continue
                
                # Atualiza o registro de arquivos processados
                processed_files[file_path] = os.path.getmtime(file_path)
                
            except Exception as e:
                print(f"  - ERRO ao processar {os.path.basename(file_path)}: {str(e)}")
        
        # Salva a lista atualizada de arquivos processados
        self.save_processed_files(processed_files)
        print("\nProcessamento concluído!")

    def setup_logging(self):
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
        
    def process_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Processa um único arquivo PDF e retorna seus chunks de texto.
        
        Args:
            pdf_path (str): Caminho para o arquivo PDF
            
        Returns:
            List[Dict]: Lista de chunks de texto com metadados
        """
        try:
            print(f"\nProcessando: {os.path.basename(pdf_path)}")
            loader = PyPDFLoader(pdf_path)
            pages = loader.load()
            print(f"  - {len(pages)} páginas encontradas")
            
            # Divide o texto em chunks
            chunks = []
            for page in pages:
                page_chunks = self.text_splitter.split_text(page.page_content)
                for chunk in page_chunks:
                    chunks.append({
                        "content": chunk,
                        "metadata": {
                            "source": os.path.basename(pdf_path),
                            "page": page.metadata.get("page", 0)
                        }
                    })
            
            print(f"  - {len(chunks)} chunks gerados")
            return chunks
            
        except Exception as e:
            pdf_logger.error(f"Erro ao processar PDF {pdf_path}: {e}")
            print(f"  - ERRO ao processar {os.path.basename(pdf_path)}: {str(e)}")
            return []

    def process_epub(self, epub_path: str) -> List[Dict]:
        """
        Processa um arquivo EPUB e retorna seus chunks de texto.
        
        Args:
            epub_path (str): Caminho para o arquivo EPUB
            
        Returns:
            List[Dict]: Lista de chunks de texto com metadados
        """
        try:
            print(f"\nProcessando: {os.path.basename(epub_path)}")
            book = epub.read_epub(epub_path)
            
            # Extrai o texto de todos os documentos HTML
            full_text = ""
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    # Converte HTML para texto
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    full_text += soup.get_text() + "\n\n"
            
            # Divide o texto em chunks
            chunks = self.text_splitter.split_text(full_text)
            processed_chunks = []
            
            for i, chunk in enumerate(chunks):
                processed_chunks.append({
                    "content": chunk,
                    "metadata": {
                        "source": os.path.basename(epub_path),
                        "chunk_number": i
                    }
                })
            
            print(f"  - {len(processed_chunks)} chunks gerados")
            return processed_chunks
            
        except Exception as e:
            pdf_logger.error(f"Erro ao processar EPUB {epub_path}: {e}")
            print(f"  - ERRO ao processar {os.path.basename(epub_path)}: {str(e)}")
            return []

    def process_all_pdfs(self) -> List[Dict]:
        """
        Processa todos os PDFs no diretório.
        
        Returns:
            List[Dict]: Lista de documentos processados
        """
        all_chunks = []
        pdf_files = [f for f in os.listdir(self.pdf_dir) if f.endswith('.pdf')]
        epub_files = [f for f in os.listdir(self.pdf_dir) if f.endswith('.epub')]
        
        print(f"\nEncontrados {len(pdf_files)} arquivos PDF e {len(epub_files)} arquivos EPUB para processar")
        
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
                    
        for filename in tqdm(epub_files, desc="Processando EPUBs"):
            epub_path = os.path.join(self.pdf_dir, filename)
            chunks = self.process_epub(epub_path)
            # Adiciona metadados sobre a fonte
            for chunk in chunks:
                if chunk is not None:  # Verifica se o chunk é válido
                    chunk.metadata['source'] = filename
                    # Remove a extensão .epub do nome do arquivo para melhor apresentação
                    chunk.metadata['source_display'] = filename.replace('.epub', '')
                    all_chunks.append(chunk)
            
        print(f"\nTotal de chunks gerados: {len(all_chunks)}")
        return all_chunks

    def add_to_supabase(self, content: str, source: str, metadata: Dict):
        """
        Adiciona um documento ao Supabase.
        
        Args:
            content (str): Conteúdo do documento
            source (str): Fonte do documento
            metadata (Dict): Metadados do documento
        """
        try:
            vector_store = SupabaseVectorStore(
                client=self.supabase_client,
                embedding=self.embeddings,
                table_name="documents",  # Nome da tabela no Supabase
                query_name="match_documents"  # Nome da função de busca no Supabase
            )
            vector_store.add_documents([{"content": content, "metadata": metadata}])
        except Exception as e:
            pdf_logger.error(f"Erro ao adicionar documento ao Supabase: {e}")

    def list_documents(self):
        """Lista todos os documentos armazenados no Supabase."""
        try:
            # Consulta a tabela documents
            response = self.supabase_client.table('documents').select('id, content, metadata').execute()
            
            if not response.data:
                print("\nNenhum documento encontrado no Supabase.")
                return
            
            print("\nDocumentos armazenados no Supabase:")
            print("-" * 50)
            
            # Agrupa documentos por fonte
            documents_by_source = {}
            for doc in response.data:
                source = doc['metadata'].get('source', 'Desconhecido')
                if source not in documents_by_source:
                    documents_by_source[source] = []
                documents_by_source[source].append(doc)
            
            # Mostra estatísticas por fonte
            for source, docs in documents_by_source.items():
                print(f"\nFonte: {source}")
                print(f"Número de chunks: {len(docs)}")
                print(f"Tamanho médio dos chunks: {sum(len(d['content']) for d in docs) / len(docs):.0f} caracteres")
                
                # Mostra uma amostra do primeiro chunk
                if docs:
                    print("\nAmostra do primeiro chunk:")
                    print(docs[0]['content'][:200] + "...")
                print("-" * 50)
                
        except Exception as e:
            print(f"\nErro ao listar documentos: {str(e)}")

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

    def query_similar_content(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Realiza uma busca híbrida (semântica + keywords) nos documentos.
        
        Args:
            query (str): Texto para buscar conteúdo similar
            limit (int, optional): Número máximo de resultados. Defaults to 5.
            
        Returns:
            List[Dict]: Lista de documentos similares
        """
        try:
            # Configuração do vector store
            vector_store = SupabaseVectorStore(
                client=self.supabase_client,
                embedding=self.embeddings,
                table_name="documents",
                query_name="match_documents"
            )
            print("\nRealizando busca semântica...")
            
            # Busca semântica (sem score já que não está disponível)
            docs = vector_store.similarity_search(
                query, 
                k=limit * 2  # Buscamos mais resultados para depois filtrar
            )
            
            semantic_docs = [
                {
                    'content': doc.page_content,
                    'source': doc.metadata.get('source', 'Desconhecido'),
                    'page': doc.metadata.get('page', doc.metadata.get('chunk_number', 'N/A')),
                    'semantic_score': 1.0  # Como não temos score real, usamos 1.0
                }
                for doc in docs
            ]
            
            keyword_docs = []
            SEMANTIC_WEIGHT = 1.0
            KEYWORD_WEIGHT = 0.0
            
            try:
                # Usando ilike para busca de texto em vez de textSearch
                keyword_results = self.supabase_client.table('documents').select(
                    'content', 'metadata'
                ).ilike('content', f'%{query}%').limit(limit * 5).execute()  # Aumentado para mais opções
                
                # Normaliza os scores de keywords e filtra por relevância
                if keyword_results.data:
                    # Extrai conceitos principais da query
                    query_concepts = set(query.lower().split())
                    
                    for doc in keyword_results.data:
                        content = doc['content'].lower()
                        
                        # Análise de relevância mais profunda
                        # 1. Frequência dos termos
                        term_count = sum(1 for term in query_concepts if term in content)
                        term_score = term_count / len(query_concepts)
                        
                        # 2. Proximidade dos termos
                        max_distance = 100  # caracteres
                        proximity_score = 0
                        
                        for term1 in query_concepts:
                            if term1 in content:
                                pos1 = content.index(term1)
                                for term2 in query_concepts:
                                    if term2 != term1 and term2 in content:
                                        pos2 = content.index(term2)
                                        distance = abs(pos2 - pos1)
                                        if distance <= max_distance:
                                            proximity_score += 1 - (distance / max_distance)
                        
                        if len(query_concepts) > 1:
                            proximity_score = proximity_score / (len(query_concepts) * (len(query_concepts) - 1))
                        
                        # 3. Contexto semântico
                        context_terms = {
                            'transformação': {'mudança', 'evolução', 'desenvolvimento', 'crescimento'},
                            'espiritual': {'alma', 'espírito', 'divino', 'sagrado', 'santo'},
                            'luta': {'batalha', 'desafio', 'confronto', 'superação'},
                            'moral': {'ética', 'virtude', 'caráter', 'conduta'}
                        }
                        
                        context_score = 0
                        for term in query_concepts:
                            if term in context_terms:
                                related_terms = context_terms[term]
                                context_matches = sum(1 for rt in related_terms if rt in content)
                                if related_terms:
                                    context_score += context_matches / len(related_terms)
                        
                        if query_concepts:
                            context_score = context_score / len(query_concepts)
                        
                        # Score final combinado
                        final_score = (
                            term_score * 0.4 +
                            proximity_score * 0.3 +
                            context_score * 0.3
                        )
                        
                        # Só inclui se tiver relevância mínima
                        if final_score > 0.4:  # Threshold mais rigoroso
                            keyword_docs.append({
                                'content': doc['content'],
                                'source': doc['metadata'].get('source', 'Desconhecido'),
                                'page': doc['metadata'].get('page', doc['metadata'].get('chunk_number', 'N/A')),
                                'keyword_score': final_score
                            })
                
                # Ajusta os pesos para dar ainda mais importância à relevância semântica
                SEMANTIC_WEIGHT = 0.85  # Aumentado para 0.85
                KEYWORD_WEIGHT = 0.15   # Diminuído para 0.15
                
            except Exception as e:
                logging.warning(f"Erro na busca por keywords: {str(e)}")
                # Se houve erro na busca por keywords, usamos apenas semântica
                SEMANTIC_WEIGHT = 1.0
                KEYWORD_WEIGHT = 0.0
                
            # Combina os resultados
            combined_results = {}
            
            # Adiciona resultados semânticos
            for doc in semantic_docs:
                key = (doc['source'], doc['content'])
                if key not in combined_results:
                    combined_results[key] = {
                        'content': doc['content'],
                        'source': doc['source'],
                        'page': doc['page'],
                        'semantic_score': doc['semantic_score'],
                        'keyword_score': 0
                    }
            
            # Adiciona resultados de keywords
            for doc in keyword_docs:
                key = (doc['source'], doc['content'])
                if key in combined_results:
                    combined_results[key]['keyword_score'] = doc['keyword_score']
                else:
                    combined_results[key] = {
                        'content': doc['content'],
                        'source': doc['source'],
                        'page': doc['page'],
                        'semantic_score': 0,
                        'keyword_score': doc['keyword_score']
                    }
            
            # Calcula score final (média ponderada)
            final_results = []
            for doc in combined_results.values():
                final_score = (
                    doc['semantic_score'] * SEMANTIC_WEIGHT +
                    doc['keyword_score'] * KEYWORD_WEIGHT
                )
                
                # Expande o contexto do resultado
                expanded_content = self.expand_context(
                    content=doc['content'],
                    source=doc['source'],
                    page=doc['page']
                )
                
                final_results.append({
                    'content': expanded_content,
                    'source': os.path.splitext(doc['source'])[0],  # Remove a extensão
                    'page': doc['page'],
                    'score': final_score
                })
            
            # Ordena por score e limita aos top resultados
            final_results.sort(key=lambda x: x['score'], reverse=True)
            return final_results[:limit]
        
        except Exception as e:
            pdf_logger.error(f"Erro ao buscar conteúdo similar: {str(e)}", exc_info=True)
            # Se algo der errado, tentamos retornar apenas os resultados semânticos básicos
            try:
                docs = vector_store.similarity_search(query, k=limit)
                return [
                    {
                        'content': doc.page_content,
                        'source': os.path.splitext(doc.metadata.get('source', 'Desconhecido'))[0],
                        'page': doc.metadata.get('page', doc.metadata.get('chunk_number', 'N/A')),
                        'score': 1.0
                    }
                    for doc in docs
                ]
            except:
                raise  # Se mesmo a busca básica falhar, aí sim levantamos o erro

    def expand_context(self, content: str, source: str, page: Any, full_content: bool = False) -> str:
        """
        Expande o contexto de um trecho encontrado, incluindo texto antes e depois.
        
        Args:
            content (str): O trecho original encontrado
            source (str): Nome do arquivo fonte
            page: Número da página ou chunk
            full_content (bool): Se True, busca o documento completo para expandir contexto
        
        Returns:
            str: Texto expandido com contexto
        """
        try:
            # Busca o documento original
            results = self.supabase_client.table('documents').select(
                'content', 'metadata'
            ).eq('metadata->>source', source).execute()
            
            if not results.data:
                return content
            
            # Organiza os chunks por página/número
            chunks_by_page = {}
            for doc in results.data:
                doc_page = doc['metadata'].get('page', doc['metadata'].get('chunk_number', 0))
                if doc_page not in chunks_by_page:
                    chunks_by_page[doc_page] = []
                chunks_by_page[doc_page].append(doc['content'])
            
            # Se page não é um número, tenta converter
            if isinstance(page, str):
                try:
                    page = int(page)
                except:
                    page = 0
                    
            # Encontra o chunk atual e os adjacentes
            current_chunks = chunks_by_page.get(page, [])
            prev_chunks = chunks_by_page.get(page - 1, [])
            next_chunks = chunks_by_page.get(page + 1, [])
            
            # Encontra o índice do chunk atual
            current_index = -1
            for i, chunk in enumerate(current_chunks):
                if content in chunk:
                    current_index = i
                    break
                    
            if current_index == -1:
                return content
            
            # Define quanto contexto incluir
            if full_content:
                # Inclui todo o conteúdo da página atual
                expanded_content = "\n\n".join(current_chunks)
            else:
                # Inclui apenas chunks adjacentes na mesma página
                context_chunks = []
                
                # Adiciona chunk anterior da mesma página
                if current_index > 0:
                    context_chunks.append(current_chunks[current_index - 1])
                    
                # Adiciona chunk atual
                context_chunks.append(current_chunks[current_index])
                
                # Adiciona chunk seguinte da mesma página
                if current_index < len(current_chunks) - 1:
                    context_chunks.append(current_chunks[current_index + 1])
                    
                # Se não tem contexto na mesma página, tenta páginas adjacentes
                if len(context_chunks) == 1:
                    if prev_chunks and current_index == 0:
                        context_chunks.insert(0, prev_chunks[-1])
                    if next_chunks and current_index == len(current_chunks) - 1:
                        context_chunks.append(next_chunks[0])
                        
                expanded_content = "\n\n".join(context_chunks)
        
            return expanded_content
        
        except Exception as e:
            pdf_logger.warning(f"Erro ao expandir contexto: {e}")
            return content
