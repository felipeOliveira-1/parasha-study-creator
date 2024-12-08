import os
import json
import logging
from typing import List, Dict
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv
from pdf_processor import PDFProcessor
import requests
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import html2text

# Configuração inicial apenas do logging básico
logging.basicConfig(level=logging.INFO)

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Verifica se as variáveis do Supabase estão definidas
if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_SERVICE_KEY"):
    print("\nERRO: As variáveis SUPABASE_URL e SUPABASE_SERVICE_KEY precisam estar definidas no arquivo .env")
    print("Por favor, configure estas variáveis e tente novamente.")
    exit()

# Constantes e configurações
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ORG = os.getenv("OPENAI_ORG", None)
PDF_FOLDER = os.getenv("PDF_FOLDER", "livros")
CACHE_FILE = os.getenv("CACHE_FILE", "parasha_cache.json")
STUDY_FOLDER = os.getenv("STUDY_FOLDER", "estudos")
CHAT_HISTORY_FOLDER = os.getenv("CHAT_HISTORY_FOLDER", "conversas")

# Mapeamento de parashiot para suas referências no Sefaria
PARASHA_REFERENCES = {
    "Bereshit": "Genesis 1:1-6:8",
    "Noach": "Genesis 6:9-11:32",
    "Lech Lecha": "Genesis 12:1-17:27",
    "Vayera": "Genesis 18:1-22:24",
    "Chayei Sarah": "Genesis 23:1-25:18",
    "Toldot": "Genesis 25:19-28:9",
    "Vayetzei": "Genesis 28:10-32:3",
    "Vayishlach": "Genesis 32:4-36:43",
    "Vayeshev": "Genesis 37:1-40:23",
    "Miketz": "Genesis 41:1-44:17",
    "Vayigash": "Genesis 44:18-47:27",
    "Vayechi": "Genesis 47:28-50:26",
    "Shemot": "Exodus 1:1-6:1",
    "Vaera": "Exodus 6:2-9:35",
    "Bo": "Exodus 10:1-13:16",
    "Beshalach": "Exodus 13:17-17:16",
    "Yitro": "Exodus 18:1-20:23",
    "Mishpatim": "Exodus 21:1-24:18",
    "Terumah": "Exodus 25:1-27:19",
    "Tetzaveh": "Exodus 27:20-30:10",
    "Ki Tisa": "Exodus 30:11-34:35",
    "Vayakhel": "Exodus 35:1-38:20",
    "Pekudei": "Exodus 38:21-40:38",
    "Vayikra": "Leviticus 1:1-5:26",
    "Tzav": "Leviticus 6:1-8:36",
    "Shemini": "Leviticus 9:1-11:47",
    "Tazria": "Leviticus 12:1-13:59",
    "Metzora": "Leviticus 14:1-15:33",
    "Achrei Mot": "Leviticus 16:1-18:30",
    "Kedoshim": "Leviticus 19:1-20:27",
    "Emor": "Leviticus 21:1-24:23",
    "Behar": "Leviticus 25:1-26:2",
    "Bechukotai": "Leviticus 26:3-27:34",
    "Bamidbar": "Numbers 1:1-4:20",
    "Naso": "Numbers 4:21-7:89",
    "Beha'alotekha": "Numbers 8:1-12:16",
    "Shelach": "Numbers 13:1-15:41",
    "Korach": "Numbers 16:1-18:32",
    "Chukat": "Numbers 19:1-22:1",
    "Balak": "Numbers 22:2-25:9",
    "Pinchas": "Numbers 25:10-30:1",
    "Matot": "Numbers 30:2-32:42",
    "Masei": "Numbers 33:1-36:13",
    "Devarim": "Deuteronomy 1:1-3:22",
    "Vaetchanan": "Deuteronomy 3:23-7:11",
    "Eikev": "Deuteronomy 7:12-11:25",
    "Re'eh": "Deuteronomy 11:26-16:17",
    "Shoftim": "Deuteronomy 16:18-21:9",
    "Ki Teitzei": "Deuteronomy 21:10-25:19",
    "Ki Tavo": "Deuteronomy 26:1-29:8",
    "Nitzavim": "Deuteronomy 29:9-30:20",
    "Vayeilech": "Deuteronomy 31:1-31:30",
    "Ha'azinu": "Deuteronomy 32:1-32:52",
    "VeZot HaBerakhah": "Deuteronomy 33:1-34:12"
}

def get_parasha_reference(parasha_name: str) -> str:
    """
    Obtém a referência correta da parashá no formato do Sefaria.
    
    Args:
        parasha_name: Nome da parashá (ex: "Bereshit", "Noach")
        
    Returns:
        str: Referência no formato do Sefaria (ex: "Genesis 1:1-6:8")
    """
    if parasha_name not in PARASHA_REFERENCES:
        raise ValueError(f"Parashá '{parasha_name}' não encontrada. Verifique o nome e tente novamente.")
    return PARASHA_REFERENCES[parasha_name]

def get_parasha_text(parasha_name):
    """Obtém o texto da parashá da API do Sefaria."""
    try:
        # Obtém a referência correta para a parashá
        reference = get_parasha_reference(parasha_name)
        
        # Separa o livro e os versículos
        book, verses = reference.split(" ", 1)
        
        # URL base da API do Sefaria
        base_url = "https://www.sefaria.org/api/texts/"
        
        # Constrói a URL completa
        url = f"{base_url}{book}.{verses}?context=0&pad=0&commentary=0&language=en"
        
        # Faz a requisição
        response = requests.get(url)
        response.raise_for_status()
        
        # Processa a resposta
        data = response.json()
        
        def flatten_text(text_data):
            """Função auxiliar para achatar estruturas de texto aninhadas."""
            if isinstance(text_data, str):
                return text_data
            elif isinstance(text_data, list):
                return " ".join(flatten_text(item) for item in text_data if item)
            else:
                return ""

        # Extrai o texto em inglês
        if 'text' not in data:
            raise ValueError("Resposta da API não contém campo 'text'")
            
        # Processa o texto, que pode estar em diferentes formatos
        text = flatten_text(data['text'])
        
        if not text.strip():
            raise ValueError("Texto da parashá está vazio após processamento")
            
        return text
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao fazer requisição para a API do Sefaria: {e}")
        raise
    except Exception as e:
        logging.error(f"Erro ao obter texto da parashá: {e}")
        raise

# Garante que a pasta de histórico existe
os.makedirs(CHAT_HISTORY_FOLDER, exist_ok=True)

def save_chat_history(messages: list, conversation_name: str = None) -> str:
    """
    Salva o histórico da conversa em um arquivo JSON.
    
    Args:
        messages: Lista de mensagens da conversa
        conversation_name: Nome opcional para a conversa
        
    Returns:
        str: Nome do arquivo onde a conversa foi salva
    """
    # Se não foi fornecido um nome, usa a data/hora atual
    if not conversation_name:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        conversation_name = f"conversa_{timestamp}"
    
    # Garante que o nome do arquivo tem extensão .json
    if not conversation_name.endswith('.json'):
        conversation_name += '.json'
        
    filepath = os.path.join(CHAT_HISTORY_FOLDER, conversation_name)
    
    # Salva o histórico
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'messages': messages
            }, f, ensure_ascii=False, indent=2)
        return conversation_name
    except Exception as e:
        logging.error(f"Erro ao salvar histórico: {str(e)}")
        return None

def load_chat_history(conversation_name: str) -> list:
    """
    Carrega o histórico de uma conversa.
    
    Args:
        conversation_name: Nome do arquivo da conversa
        
    Returns:
        list: Lista de mensagens da conversa
    """
    # Garante que o nome do arquivo tem extensão .json
    if not conversation_name.endswith('.json'):
        conversation_name += '.json'
        
    filepath = os.path.join(CHAT_HISTORY_FOLDER, conversation_name)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['messages']
    except Exception as e:
        logging.error(f"Erro ao carregar histórico: {str(e)}")
        return []

def list_chat_histories() -> list:
    """Lista todas as conversas salvas."""
    try:
        histories = [f for f in os.listdir(CHAT_HISTORY_FOLDER) if f.endswith('.json')]
        return sorted(histories, reverse=True)  # Mais recentes primeiro
    except Exception as e:
        logging.error(f"Erro ao listar históricos: {str(e)}")
        return []

def print_help():
    """Exibe o guia de ajuda do programa."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                   Guia do Parasha Study Creator                    ║
╚════════════════════════════════════════════════════════════════════╝

📚 Comandos Disponíveis:
  /help    - Exibe este guia de ajuda
  /refs    - Busca referências nos textos sagrados
  /save    - Salva a conversa atual
  sair     - Encerra a conversa

🔍 Como Usar as Referências:
  /refs [sua pergunta]
  Exemplo: /refs qual a importância do shabat?
  
💾 Como Salvar Conversas:
  /save [nome_opcional]
  Exemplo: /save minha_conversa
  • Se não especificar um nome, será usado data/hora atual
  
📖 Tópicos para Perguntas:
  • Torah e comentários rabínicos
  • Halakhá (lei judaica)
  • Parashat Hashavua
  • Filosofia e pensamento judaico
  • Kabbalah e misticismo judaico

💡 Dicas:
  • Use perguntas específicas para respostas mais precisas
  • Ao usar /refs, aguarde a busca nas referências
  • Salve conversas importantes para continuar depois
  • Você pode carregar conversas antigas ao iniciar

❓ Exemplos de Perguntas:
  • Qual o significado do Shemá Israel?
  • /refs como observar corretamente o Shabat?
  • Qual a importância da Teshuva?
  • /refs explique o conceito de Tikkun Olam
""")

def chat_with_rabbi():
    """Função para interagir com o Rabino Virtual"""
    print("\nBruchim Haba'im - ברוכים הבאים!")
    print("Bem-vindo ao Rabino Virtual!")
    
    # Opção de carregar histórico
    histories = list_chat_histories()
    if histories:
        print("\nConversas anteriores disponíveis:")
        for i, history in enumerate(histories, 1):
            # Remove a extensão .json para exibição
            display_name = history[:-5] if history.endswith('.json') else history
            print(f"{i}. {display_name}")
        print("0. Iniciar nova conversa")
        
        while True:
            try:
                choice = input("\nEscolha uma opção (0 para nova conversa): ").strip()
                if choice == '0':
                    messages = [{"role": "system", "content": RABBI_SYSTEM_PROMPT}]
                    break
                elif choice.isdigit() and 1 <= int(choice) <= len(histories):
                    loaded_messages = load_chat_history(histories[int(choice)-1])
                    if loaded_messages:
                        messages = loaded_messages
                        print("\nConversa anterior carregada!")
                        # Exibe as últimas 3 mensagens do histórico
                        print("\nÚltimas mensagens:")
                        for msg in loaded_messages[-6:]:  # Últimas 3 interações (pergunta/resposta)
                            if msg['role'] == 'user':
                                print(f"\nVocê: {msg['content'][:100]}...")
                            elif msg['role'] == 'assistant':
                                print(f"Rabino: {msg['content'][:100]}...")
                        break
                    else:
                        print("Erro ao carregar conversa. Iniciando nova conversa.")
                        messages = [{"role": "system", "content": RABBI_SYSTEM_PROMPT}]
                        break
                else:
                    print("Opção inválida. Tente novamente.")
            except ValueError:
                print("Entrada inválida. Tente novamente.")
    else:
        messages = [{"role": "system", "content": RABBI_SYSTEM_PROMPT}]
    
    print("\nAqui você pode fazer perguntas sobre:")
    print("- Torah e comentários rabínicos")
    print("- Halakhá (lei judaica)")
    print("- Parashat Hashavua")
    print("- Filosofia e pensamento judaico")
    print("- Kabbalah e misticismo judaico")
    print("\nComandos especiais:")
    print("- Digite /help para ver o guia completo")
    print("- Use /refs para incluir referências dos livros")
    print("- Use /save para salvar a conversa atual")
    print("- Digite 'sair' para encerrar a conversa")
    
    # Inicializa o processador de PDF
    pdf_processor = PDFProcessor(PDF_FOLDER)
    
    while True:
        # Recebe a pergunta do usuário
        user_input = input("\nSua pergunta: ").strip()
        
        if user_input.lower() == 'sair':
            # Oferece salvar a conversa antes de sair
            save_option = input("\nDeseja salvar esta conversa? (s/n): ").strip().lower()
            if save_option == 's':
                name = input("Nome para a conversa (Enter para usar data/hora atual): ").strip()
                saved_name = save_chat_history(messages, name if name else None)
                if saved_name:
                    print(f"\nConversa salva como: {saved_name}")
            print("\nShalom! Tenha um excelente dia!")
            break
            
        # Comando de ajuda
        if user_input.lower() == '/help':
            print_help()
            continue
            
        # Comando para salvar a conversa
        if user_input.startswith('/save'):
            parts = user_input.split(maxsplit=1)
            name = parts[1] if len(parts) > 1 else None
            saved_name = save_chat_history(messages, name)
            if saved_name:
                print(f"\nConversa salva como: {saved_name}")
            continue
            
        # Verifica se o usuário quer incluir referências
        include_refs = user_input.startswith('/refs')
        if include_refs:
            user_input = user_input[5:].strip()  # Remove o comando /refs
            
            print("\nBuscando referências relevantes...")
            references = get_references_for_query(pdf_processor, user_input)
            
            if references:
                print("\nEncontramos algumas referências relevantes nos textos:")
                print(references)
                
                # Adiciona as referências ao contexto da pergunta
                context_prompt = f"""Pergunta do usuário: {user_input}

Referências encontradas nos textos:
{references}

Por favor, responda à pergunta incorporando o conhecimento das referências fornecidas, citando-as quando apropriado."""
                
                messages.append({"role": "user", "content": context_prompt})
            else:
                print("\nNenhuma referência relevante encontrada. Respondendo com conhecimento geral...")
                messages.append({"role": "user", "content": user_input})
        else:
            messages.append({"role": "user", "content": user_input})
        
        try:
            # Faz a chamada para a API
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                temperature=0.13,
            )
            
            # Obtém a resposta
            rabbi_response = response.choices[0].message.content
            
            # Adiciona a resposta ao histórico
            messages.append({"role": "assistant", "content": rabbi_response})
            
            # Exibe a resposta
            print("\nRabino:", rabbi_response)
            
        except Exception as e:
            print(f"\nErro ao processar sua pergunta: {str(e)}")
            print("Por favor, tente novamente.")

RABBI_SYSTEM_PROMPT = """You are a Rabbi specializing in Jewish studies, with deep knowledge of Torah, Talmud, Mishnah, Midrash, Halakha, Kabbalah, and Jewish thought. When provided with reference materials, analyze them and incorporate their wisdom into your responses, always citing the source."""

def load_cache():
    """Carrega o cache de parashiot já processadas."""
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_cache(cache):
    """Salva o cache de parashiot processadas."""
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)

def generate_study_topics(parasha_text, client, retries=3):
    """Gera tópicos de estudo baseados no texto da parashá."""
    try:
        # Gera um resumo do texto da parashá
        completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Você é um especialista em Torá."},
                {
                    "role": "user",
                    "content": f"Resuma o seguinte texto da Torá em português, destacando os principais acontecimentos e ensinamentos (máximo 600 caracteres):\n\n{parasha_text}"
                }
            ]
        )
        summary = completion.choices[0].message.content
            
        logging.info(f"Resumo final tem {len(summary)} caracteres")
        
        # Inicializa o processador de PDF
        print("\nBuscando referências relevantes nos livros...")
        pdf_processor = PDFProcessor(PDF_FOLDER)
        
        # Busca referências relevantes nos PDFs para o resumo geral
        references = pdf_processor.query_similar_content(summary)
        
        # Gera os tópicos de estudo
        study_messages = [
            {
                "role": "system",
                "content": """You are a Rabbi specializing in Jewish studies, with deep knowledge of Torah, Talmud, Mishnah, Midrash, Halakha, Kabbalah, and Jewish thought. Your task is to create study topics in PT-BR that help deepen the understanding of the Torah portion. Always keep the scope within Orthodox Judaism.

When creating study topics, follow this structure for each topic:

1. Topic Title (### [Título])
   - Choose a title that captures the main theme or lesson
   - Be specific and engaging

2. Narrative Context (**Contexto Narrativo**)
   - Provide the historical and textual context
   - Explain what happened before and after
   - Help readers understand the setting

3. Bible Verse (**Versículo Bíblico**)
   - Reference and full text
   - Choose the most relevant verse for the topic

4. Classical Rabbinic Commentaries (**Comentários Rabínicos Clássicos**)
   - Present commentaries in chronological order
   - Show how interpretations complement each other
   - Connect commentaries to the main theme

5. Discussion Question (**Pergunta para Discussão**)
   - Create thought-provoking questions
   - Connect to both ancient and modern contexts
   - Encourage personal reflection

6. Practical Tips (**Dicas Práticas**)
   - Provide specific, actionable advice
   - Include spiritual and practical suggestions
   - Make tips relevant to modern life

Format each topic exactly like this:
### [Título do Tópico]

**Contexto Narrativo:**
[Explicação do contexto histórico e textual]

**Versículo Bíblico:** [Referência]
**O Versículo:** "[Texto do versículo]"

**Comentários Rabínicos Clássicos:**
[Será preenchido automaticamente com comentários do Sefaria]

**Pergunta para Discussão:**
[Pergunta reflexiva]

**Dicas Práticas:**
- [Dica 1]
- [Dica 2]
- [Dica 3]"""
            },
            {
                "role": "user",
                "content": f"""Based on this summary of the parasha: {summary}

                Develop 3 study topics following the exact structure provided. Focus on the most significant moral lessons and transformative moments in the parasha.

                Remember to:
                1. Keep the context clear and concise
                2. Choose verses that best represent each topic
                3. Create thought-provoking discussion questions
                4. Connect ancient wisdom to modern life
                5. Provide practical, actionable advice"""
            }
        ]

        # Gera os tópicos de estudo
        study_completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=study_messages,
            temperature=0.7  # Ajustado para mais criatividade nas análises
        )
        topics_content = study_completion.choices[0].message.content

        # Extrai as referências bíblicas para buscar comentários
        bible_refs = []
        current_ref = None
        for line in topics_content.split('\n'):
            if '**Versículo Bíblico:**' in line:
                # Extrai a referência (ex: Genesis 32:4)
                ref_line = line.split('**Versículo Bíblico:**')[1].strip()
                if ref_line:
                    current_ref = ref_line
            elif '**O Versículo:**' in line and current_ref:
                bible_refs.append(current_ref)
                current_ref = None

        # Busca e adiciona comentários rabínicos para cada referência
        for ref in bible_refs:
            logging.info(f"Referência original: {ref}")
            normalized_ref = normalize_bible_reference(ref)
            logging.info(f"Referência normalizada: {normalized_ref}")
            
            commentaries = get_commentaries(normalized_ref)
            translated_commentaries = translate_commentaries(commentaries, client)
            formatted_commentaries = format_commentaries(translated_commentaries)
            if formatted_commentaries:
                # Substitui o placeholder dos comentários pelo conteúdo real
                placeholder = "**Comentários Rabínicos Clássicos:**\n[Será preenchido automaticamente com comentários do Sefaria]"
                topics_content = topics_content.replace(
                    placeholder,
                    formatted_commentaries.strip(),
                    1  # Substitui apenas a primeira ocorrência para cada referência
                )
                logging.info(f"Comentários adicionados para {ref}")
            else:
                logging.warning(f"Nenhum comentário encontrado para {ref}")
        
        # Adiciona os tópicos ao template com uma introdução
        template = f"""# Estudo da Parashá

## Resumo
{summary}

## Introdução ao Estudo
Este estudo explora três aspectos fundamentais da parashá, cada um oferecendo uma perspectiva única sobre as lições morais e espirituais do texto. Cada tópico inclui contexto histórico, comentários rabínicos tradicionais, análise mussar e aplicações práticas para nossa vida moderna.

## Tópicos de Estudo
{topics_content}
"""
        
        # Gera o Mussar com as referências expandidas e dicas práticas
        mussar_messages = [
            {
                "role": "system",
                "content": """As a Rabbi, your task is to create a comprehensive Mussar analysis with practical tips for each topic. Follow these guidelines:

1. Citation Selection:
   - Only use citations that directly relate to the core theme of the specific moral lesson being discussed
   - The citation should naturally flow with your analysis, not feel forced
   - If a highly relevant citation isn't available, prefer to focus on Torah analysis

2. Citation Integration:
   - Before using a citation, explain the context of the situation or lesson
   - After the citation, clearly explain how it connects to the topic
   - Show how the wisdom applies both to the biblical story and modern life

3. Practical Application:
   - Ensure practical tips are specific and actionable
   - Connect tips directly to the lessons from both the Torah portion and the cited texts
   - Include a mix of spiritual, emotional, and practical advice

4. Context Awareness:
   - Consider the full context of both the Torah portion and the cited text
   - Avoid using citations out of their original context
   - Make connections that respect the depth of both sources

Remember to maintain Orthodox Jewish perspectives and ensure all interpretations align with traditional Jewish thought."""
            },
            {
                "role": "user",
                "content": f"""Crie uma análise Mussar com citações das referências e dicas práticas para cada tópico:

                Tópicos: {topics_content}

                Referências Disponíveis:
                {json.dumps([{
                    'content': ref['content'],
                    'source': ref['source']
                } for ref in references], indent=2, ensure_ascii=False)}"""
            }
        ]

        completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=mussar_messages
        )
        mussar_content = completion.choices[0].message.content

        # Adiciona o conteúdo Mussar ao template
        template += f"\n## Mussar\n{mussar_content}\n"

        return template

    except Exception as e:
        logging.error(f"Erro ao gerar estudo: {str(e)}")
        if retries > 0:
            logging.info(f"Tentando novamente... ({retries} tentativas restantes)")
            return generate_study_topics(parasha_text, client, retries - 1)
        raise

def generate_study(parasha_text, client):
    """Função principal para gerar o estudo completo."""
    try:
        # Gera os tópicos de estudo
        study_content = generate_study_topics(parasha_text, client)
        return study_content
    except Exception as e:
        raise Exception(f"Erro ao gerar estudo: {str(e)}")

def clean_files():
    """Limpa arquivos de execuções anteriores."""
    files_to_delete = [
        'parasha_cache.json',
        'parasha_study.log',
        'pdf_processor.log'
    ]
    
    # Deleta arquivos na raiz
    for file in files_to_delete:
        try:
            if os.path.exists(file):
                os.remove(file)
                print(f"Arquivo deletado: {file}")
        except Exception as e:
            print(f"Erro ao deletar {file}: {e}")

def setup_logging():
    """Configura o sistema de logging."""
    # Configuração do logger principal
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Configuração do formato
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Handler para arquivo
    file_handler = logging.FileHandler('parasha_study.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

def get_references_for_query(pdf_processor, query: str, n_results: int = 3) -> str:
    """Busca referências relevantes nos PDFs para uma determinada pergunta."""
    try:
        results = pdf_processor.query_similar_content(query, n_results)
        if not results:
            return ""
            
        references = []
        for result in results:
            # Formata cada referência com o texto e a fonte
            reference = f"\nDe '{result['source']}':\n{result['content']}\n"
            references.append(reference)
            
        return "\n".join(references)
    except Exception as e:
        logging.error(f"Erro ao buscar referências: {str(e)}")
        return ""

def process_epub(epub_path: str, chunk_size: int = 1000) -> list:
    """
    Processa um arquivo EPUB e retorna uma lista de chunks de texto.
    
    Args:
        epub_path: Caminho para o arquivo EPUB
        chunk_size: Tamanho aproximado de cada chunk em caracteres
        
    Returns:
        List[Dict]: Lista de dicionários com o texto dividido em chunks e metadados
    """
    try:
        # Carrega o livro
        book = epub.read_epub(epub_path)
        
        # Extrai metadados básicos
        title = book.get_metadata('DC', 'title')[0][0] if book.get_metadata('DC', 'title') else "Unknown"
        author = book.get_metadata('DC', 'creator')[0][0] if book.get_metadata('DC', 'creator') else "Unknown"
        
        # Inicializa o conversor de HTML para texto
        h = html2text.HTML2Text()
        h.ignore_links = True
        h.ignore_images = True
        
        # Lista para armazenar todos os chunks
        chunks = []
        current_chunk = ""
        chapter_number = 0
        
        # Processa cada item do livro
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                # Converte HTML para texto
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                text = h.handle(str(soup))
                
                # Remove linhas em branco extras e espaços
                text = "\n".join(line.strip() for line in text.split("\n") if line.strip())
                
                # Divide o texto em chunks
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
        
        # Adiciona o último chunk se houver conteúdo
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
        logging.error(f"Erro ao processar EPUB: {str(e)}")
        raise

def add_epub_to_supabase(epub_path: str):
    """
    Processa um arquivo EPUB e adiciona seu conteúdo ao Supabase.
    
    Args:
        epub_path: Caminho para o arquivo EPUB
    """
    try:
        # Processa o EPUB
        chunks = process_epub(epub_path)
        
        # Inicializa o processador de PDF que contém a lógica do Supabase
        pdf_processor = PDFProcessor()
        
        # Adiciona cada chunk ao Supabase
        for chunk in chunks:
            pdf_processor.add_to_supabase(
                content=chunk["content"],
                source=chunk["source"],
                metadata=chunk["metadata"]
            )
            
        logging.info(f"EPUB processado com sucesso: {len(chunks)} chunks adicionados ao Supabase")
        
    except Exception as e:
        logging.error(f"Erro ao adicionar EPUB ao Supabase: {str(e)}")
        raise

def get_commentaries(reference: str) -> dict:
    """
    Busca comentários rabínicos clássicos do Sefaria para uma referência específica.
    
    Args:
        reference (str): Referência bíblica (ex: "Genesis 32:28")
        
    Returns:
        dict: Dicionário com comentários por comentarista
    """
    try:
        # Lista de comentaristas para buscar
        commentators = [
            "Rashi",
            "Ramban",
            "Sforno",
            "Or HaChaim",
            "Ibn Ezra",
            "Kli Yakar",
            "Ohr HaChaim"
        ]
        
        commentaries = {}
        base_url = "https://www.sefaria.org/api/texts/"
        
        for commentator in commentators:
            try:
                # Constrói a URL para o comentário específico
                commentary_ref = f"{commentator} on {reference}"
                url = f"{base_url}{commentary_ref}?context=0&pad=0&commentary=0&language=en"
                
                # Faz a requisição
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extrai o texto do comentário
                    if 'text' in data:
                        text = data['text']
                        if isinstance(text, list):
                            text = ' '.join([t for t in text if t])
                        if text:
                            commentaries[commentator] = text
                
            except Exception as e:
                logging.warning(f"Erro ao buscar comentário de {commentator}: {str(e)}")
                continue
        
        return commentaries
        
    except Exception as e:
        logging.error(f"Erro ao buscar comentários: {str(e)}")
        return {}

def translate_commentaries(commentaries: dict, client) -> dict:
    """
    Traduz e padroniza os comentários rabínicos do inglês para português usando a OpenAI.
    
    Args:
        commentaries (dict): Dicionário com comentários por comentarista
        client: Cliente OpenAI
        
    Returns:
        dict: Dicionário com comentários traduzidos e padronizados
    """
    if not commentaries:
        return {}
    
    translated = {}
    for commentator, text in commentaries.items():
        try:
            completion = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": """Você é um especialista em tradução e adaptação de textos rabínicos.
                        Sua tarefa é:
                        1. Traduzir o comentário para português brasileiro
                        2. Resumir o comentário em no máximo 3-4 linhas, focando nos pontos principais
                        3. Manter termos judaicos importantes em hebraico (transliterado) com breve explicação
                        4. Usar linguagem clara e acessível, mas mantendo o tom erudito
                        5. Seguir este formato:
                           "[Ponto principal do comentário]. [Explicação breve]. [Se relevante: termo em hebraico]. 
                           Para uma análise mais detalhada, consulte o texto original de [Nome do Comentarista]."
                        """
                    },
                    {
                        "role": "user",
                        "content": f"Adapte o seguinte comentário rabínico de {commentator}:\n\n{text}"
                    }
                ],
                temperature=0.3
            )
            translated[commentator] = completion.choices[0].message.content
            logging.info(f"Comentário de {commentator} traduzido e padronizado com sucesso")
        except Exception as e:
            logging.error(f"Erro ao traduzir comentário de {commentator}: {str(e)}")
            # Em caso de erro, cria uma versão simplificada do texto original
            translated[commentator] = f"Comentário original de {commentator} (em inglês): {text[:100]}... [texto completo disponível na fonte]"
    
    return translated

def format_commentaries(commentaries: dict) -> str:
    """
    Formata os comentários rabínicos para exibição.
    
    Args:
        commentaries (dict): Dicionário com comentários por comentarista
        
    Returns:
        str: Texto formatado dos comentários
    """
    if not commentaries:
        return "**Comentários Rabínicos Clássicos:**\n\nNenhum comentário encontrado para este versículo."
        
    formatted = "**Comentários Rabínicos Clássicos:**\n\n"
    
    # Ordem preferencial dos comentaristas
    preferred_order = [
        "Rashi",
        "Ramban",
        "Ibn Ezra",
        "Sforno",
        "Or HaChaim",
        "Kli Yakar",
        "Ohr HaChaim"
    ]
    
    # Adiciona comentários na ordem preferencial
    for commentator in preferred_order:
        if commentator in commentaries:
            formatted += f"**{commentator}**: {commentaries[commentator].strip()}\n\n"
    
    # Adiciona quaisquer outros comentários que não estejam na ordem preferencial
    for commentator, commentary in commentaries.items():
        if commentator not in preferred_order:
            formatted += f"**{commentator}**: {commentary.strip()}\n\n"
    
    return formatted.strip()

def normalize_bible_reference(ref: str) -> str:
    """
    Normaliza uma referência bíblica para o formato aceito pelo Sefaria.
    
    Args:
        ref (str): Referência bíblica (ex: "Gênesis 32:28")
        
    Returns:
        str: Referência normalizada (ex: "Genesis 32:28")
    """
    # Mapeamento de nomes em português para inglês
    book_names = {
        "Gênesis": "Genesis",
        "Êxodo": "Exodus",
        "Levítico": "Leviticus",
        "Números": "Numbers",
        "Deuteronômio": "Deuteronomy"
    }
    
    # Separa o nome do livro do capítulo e versículo
    parts = ref.split()
    if len(parts) >= 2:
        book = parts[0]
        rest = ' '.join(parts[1:])
        
        # Substitui o nome do livro se estiver no mapeamento
        normalized_book = book_names.get(book, book)
        return f"{normalized_book} {rest}"
    
    return ref

def get_mussar_texts(parasha_ref: str) -> List[Dict]:
    """
    Busca textos de Mussar relacionados à parashá no Sefaria.
    
    Args:
        parasha_ref: Referência da parashá no formato do Sefaria
        
    Returns:
        List[Dict]: Lista de textos de Mussar encontrados
    """
    mussar_sources = [
        "Orchot Tzadikim",
        "Mesilat Yesharim",
        "Chovot HaLevavot",
        "Shaarei Teshuvah",
        "Pele Yoetz"
    ]
    
    mussar_texts = []
    
    try:
        # Busca links relacionados
        url = f"https://www.sefaria.org/api/related/{parasha_ref}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            
            # Filtra links de fontes Mussar
            for link in data.get('links', []):
                for source in mussar_sources:
                    if source in link.get('ref', ''):
                        # Busca o texto completo do link
                        text_url = f"https://www.sefaria.org/api/texts/{link['ref']}"
                        text_response = requests.get(text_url)
                        if text_response.status_code == 200:
                            text_data = text_response.json()
                            if 'text' in text_data:
                                text = text_data['text']
                                if isinstance(text, list):
                                    text = ' '.join([t for t in text if t])
                                mussar_texts.append({
                                    'source': source,
                                    'ref': link['ref'],
                                    'text': text
                                })
        
        # Busca textos adicionais por palavras-chave
        for source in mussar_sources:
            url = f"https://www.sefaria.org/api/texts/search/{parasha_ref}?citing_only=1&citing_text={source}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                for hit in data.get('hits', {}).get('hits', []):
                    source_ref = hit['_source'].get('ref', '')
                    if source_ref:
                        text_url = f"https://www.sefaria.org/api/texts/{source_ref}"
                        text_response = requests.get(text_url)
                        if text_response.status_code == 200:
                            text_data = text_response.json()
                            if 'text' in text_data:
                                text = text_data['text']
                                if isinstance(text, list):
                                    text = ' '.join([t for t in text if t])
                                mussar_texts.append({
                                    'source': source,
                                    'ref': source_ref,
                                    'text': text
                                })
        
        return mussar_texts
        
    except Exception as e:
        logging.error(f"Erro ao buscar textos Mussar: {str(e)}")
        return []

def main():
    """Função principal do programa"""
    print("\nBem-vindo ao Parasha Study Creator!")
    
    # Inicializa o cliente OpenAI
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        organization=os.getenv("OPENAI_ORG", None)
    )
    
    while True:
        print("\nEscolha uma opção:")
        print("1. Conversar com o Rabino Virtual")
        print("2. Gerar estudo da Parasha")
        print("3. Listar documentos no Supabase")
        print("4. Reprocessar todos os documentos")
        
        choice = input("\nSua escolha (1, 2, 3 ou 4): ")
        
        if choice == "1":
            chat_with_rabbi()
            break
        elif choice == "2":
            # Limpa arquivos antigos
            clean_files()
            
            # Lista todas as parashiot disponíveis
            print("\nParashiot disponíveis:")
            for i, parasha in enumerate(sorted(PARASHA_REFERENCES.keys()), 1):
                print(f"{i}. {parasha}")
            
            # Solicita o nome da parashá
            while True:
                parasha_name = input("\nDigite o nome da parashá (ou 'lista' para ver novamente): ")
                
                if parasha_name.lower() == 'lista':
                    print("\nParashiot disponíveis:")
                    for i, parasha in enumerate(sorted(PARASHA_REFERENCES.keys()), 1):
                        print(f"{i}. {parasha}")
                    continue
                
                if parasha_name in PARASHA_REFERENCES:
                    break
                else:
                    print(f"Parashá '{parasha_name}' não encontrada. Por favor, escolha uma da lista.")
            
            try:
                # Obtém o texto da parashá
                print(f"\nObtendo texto para {parasha_name}")
                parasha_text = get_parasha_text(parasha_name)
                
                # Gera o estudo
                print("\nGerando estudo...")
                study = generate_study(parasha_text, client)
                
                # Salva o estudo em um arquivo
                today = datetime.now().strftime("%Y-%m-%d")
                safe_parasha_name = ''.join(c for c in parasha_name if c.isalnum() or c in (' ', '-', '_'))
                output_file = os.path.join(STUDY_FOLDER, f"estudo_{safe_parasha_name}_{today}.md")
                
                # Cria o diretório se não existir
                os.makedirs(STUDY_FOLDER, exist_ok=True)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(study)
                
                print(f"\nEstudo salvo em: {output_file}")
                
            except Exception as e:
                logging.error(f"Erro na execução principal: {str(e)}")
                raise
            
            break
        elif choice == "3":
            # Lista os documentos no Supabase
            processor = PDFProcessor(PDF_FOLDER)
            processor.list_documents()
            input("\nPressione Enter para continuar...")
            break
        elif choice == "4":
            # Força o reprocessamento de todos os documentos
            print("\nForçando reprocessamento de todos os documentos...")
            processor = PDFProcessor(PDF_FOLDER)
            
            # Remove o arquivo de versão para forçar reprocessamento
            if os.path.exists("pdf_version.json"):
                os.remove("pdf_version.json")
                print("Cache de versão removido.")
            
            # Processa todos os documentos novamente
            processor.create_vector_store()
            print("\nReprocessamento concluído!")
            input("\nPressione Enter para continuar...")
            break
        else:
            print("\nOpção inválida. Por favor, escolha 1, 2, 3 ou 4.")

if __name__ == "__main__":
    main()