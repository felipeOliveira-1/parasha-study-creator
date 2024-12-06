import os
import json
import logging
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv
from pdf_processor import PDFProcessor
import requests

# Configuração inicial apenas do logging básico
logging.basicConfig(level=logging.INFO)

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Constantes e configurações
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "o1-preview")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PDF_FOLDER = os.getenv("PDF_FOLDER", "livros")
CACHE_FILE = os.getenv("CACHE_FILE", "parasha_cache.json")

# Configurações iniciais
client = OpenAI()


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


def get_parasha_text(parasha_name):
    """Obtém o texto da parashá da API do Sefaria."""
    # URL base da API do Sefaria
    base_url = "https://www.sefaria.org/api/texts/"
    
    try:
        # Faz a requisição para a API
        response = requests.get(
            f"{base_url}{parasha_name}?context=0&pad=0&commentary=0&version=The Koren Jerusalem Bible"
        )
        response.raise_for_status()  # Levanta exceção para erros HTTP
        
        data = response.json()
        
        # Verifica se o texto está em formato de lista ou string
        text = data.get('text', '')
        if isinstance(text, list):
            # Se for lista, junta os elementos
            text = ' '.join(text)
        elif not isinstance(text, str):
            # Se não for string nem lista, converte para string
            text = str(text)
        
        # Verifica se o texto está vazio
        if not text.strip():
            raise ValueError("Texto da parashá está vazio")
            
        return text
        
    except Exception as e:
        logging.error(f"Erro ao obter texto da parashá: {e}")
        raise


def generate_study_topics(parasha_text, retries=3):
    """Gera tópicos de estudo baseados no texto da parashá."""
    try:
        # Gera um resumo do texto da parashá
        print("\nPressione Enter para usar o resumo sugerido ou digite seu próprio resumo:")
        user_summary = input("> ")
        
        if not user_summary.strip():
            # Se o usuário não forneceu um resumo, gera um
            completion = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Você é um especialista em Torá."},
                    {
                        "role": "user",
                        "content": f"Resuma o seguinte texto da Torá em português, destacando os principais acontecimentos e ensinamentos (máximo 300 caracteres):\n\n{parasha_text}"
                    }
                ]
            )
            summary = completion.choices[0].message.content
        else:
            summary = user_summary
            
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
                "content": """You are a Rabbi specializing in Jewish studies, with deep knowledge of Torah, Talmud, Mishnah, Midrash, Halakha, Kabbalah, and Jewish thought. Your task is to create study topics in PT-BR that help deepen the understanding of the Torah portion. Always keep the scope within Orthodox Judaism."""
            },
            {
                "role": "user",
                "content": f"""Based on this summary of the parasha: {summary}

                Develop 3 study topics, each containing:
                - Topic title
                - Related Bible verse (reference and text)
                - A deep reflection on the topic
                - A question for discussion
                - 3 practical tips for applying the learning

                Format each topic like this:
                ### [Topic Title]
                **Bible Verse:** [Reference]
                **The Verse:** "[Verse Text]"

                **Reflection:** [Your Reflection]

                **Discussion Question:** [Your Question]

                **Practical Tips:**
                - [Tip 1]
                - [Tip 2]
                - [Tip 3]"""
            }
        ]

        study_completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=study_messages
        )
        topics_content = study_completion.choices[0].message.content

        # Adiciona os tópicos ao template
        template = f"# Estudo da Parashá\n\n## Resumo\n{summary}\n\n## Tópicos de Estudo\n{topics_content}\n"

        # Gera o Mussar com as referências expandidas e dicas práticas
        mussar_messages = [
            {
                "role": "system",
                "content": """As a Rabbi, your task is to create a comprehensive Mussar analysis with practical tips for each topic. The Mussar analysis should include citations from available references, formatted as: "In [Book Name], we find: '[QUOTE]'. This teaching shows us that..." You should provide detailed explanations after each citation and demonstrate how it applies to modern life. Avoid repeating the same source twice, and ensure that your response is in pt-br.

                Additionally, for each topic, include a "Practical Tips" section with three suggestions.

                Please ensure that your Mussar analysis and practical tips are insightful, relevant, and applicable to the topic at hand. Your response should be flexible enough to allow for various relevant and creative analyses and practical tips, while maintaining a clear and structured format for each topic."""
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

        # Cria o diretório de estudos se não existir
        os.makedirs("estudos", exist_ok=True)

        # Gera um nome de arquivo com a data
        today = datetime.now().strftime("%Y-%m-%d")
        safe_parasha_name = ''.join(c for c in "Genesis.1" if c.isalnum() or c in (' ', '-', '_'))
        output_file = os.path.join("estudos", f"estudo_{safe_parasha_name}_{today}.md")

        # Salva o estudo em um arquivo .md
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(template)
            
        print(f"\nEstudo salvo em: {output_file}")
        return template

    except Exception as e:
        logging.error(f"Erro ao gerar estudo: {str(e)}")
        if retries > 0:
            logging.info(f"Tentando novamente... ({retries} tentativas restantes)")
            return generate_study_topics(parasha_text, retries - 1)
        else:
            raise e


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


def main():
    """Função principal do programa."""
    try:
        # Limpa arquivos antigos
        clean_files()
        
        # Configura o logging
        setup_logging()
        
        # Verifica se a API key está configurada
        if not OPENAI_API_KEY:
            raise ValueError("API key não encontrada. Configure a variável OPENAI_API_KEY no arquivo .env")
            
        # Carrega o cache
        cache = load_cache()
        
        # Nome da parashá a ser estudada
        parasha_name = "Genesis.1"
        
        # Verifica se a parashá já está no cache
        if parasha_name in cache:
            print(f"Usando texto em cache para {parasha_name}")
            parasha_text = cache[parasha_name]
        else:
            print(f"Obtendo texto para {parasha_name}")
            parasha_text = get_parasha_text(parasha_name)
            cache[parasha_name] = parasha_text
            save_cache(cache)
        
        # Gera o estudo
        generate_study_topics(parasha_text)
        
    except Exception as e:
        logging.error(f"Erro na execução principal: {str(e)}")
        raise


if __name__ == "__main__":
    main()