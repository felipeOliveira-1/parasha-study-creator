import streamlit as st
import os
from datetime import datetime
from main import (
    PDFProcessor,
    get_references_for_query,
    save_chat_history,
    load_chat_history,
    list_chat_histories,
    RABBI_SYSTEM_PROMPT,
    PDF_FOLDER,
    CHAT_HISTORY_FOLDER,
    get_parasha_text,
    generate_study_topics,
    load_cache,
    save_cache,
    PARASHA_REFERENCES,
    STUDY_FOLDER
)
from openai import OpenAI
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Inicializa o cliente OpenAI
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORG", None)
)

# Configuração da página
st.set_page_config(
    page_title="Parasha Study Creator",
    page_icon="✡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para estilizar a interface
def local_css():
    st.markdown("""
        <style>
        .chat-message {
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            display: flex;
            flex-direction: column;
            color: #000000;  /* Garante texto preto */
        }
        .user-message {
            background-color: #e6f3ff;
            border-left: 5px solid #2778c4;
            color: #000000;  /* Texto preto para mensagens do usuário */
        }
        .assistant-message {
            background-color: #f0f2f6;
            border-left: 5px solid #464b54;
            color: #000000;  /* Texto preto para mensagens do rabino */
        }
        .refs-message {
            background-color: #fff3e6;
            border-left: 5px solid #ff9d00;
            font-size: 0.9em;
            color: #000000;  /* Texto preto para referências */
        }
        .hebrew-text {
            font-family: 'Times New Roman', serif;
            font-size: 1.2em;
            color: #000000;  /* Texto preto para hebraico */
        }
        /* Garante que todos os textos dentro das mensagens sejam pretos */
        .chat-message p, .chat-message span, .chat-message div {
            color: #000000 !important;
        }
        </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Inicializa variáveis da sessão se não existirem"""
    if 'messages' not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": RABBI_SYSTEM_PROMPT}]
    if 'pdf_processor' not in st.session_state:
        st.session_state.pdf_processor = PDFProcessor(PDF_FOLDER)
    if 'conversation_name' not in st.session_state:
        st.session_state.conversation_name = None

def display_chat_history():
    """Exibe o histórico do chat com estilo personalizado"""
    for message in st.session_state.messages[1:]:  # Pula o system prompt
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message user-message"><strong style="color: #000000;">🙋‍♂️ Você:</strong> <span style="color: #000000;">{message["content"]}</span></div>', unsafe_allow_html=True)
        elif message["role"] == "assistant":
            st.markdown(f'<div class="chat-message assistant-message"><strong style="color: #000000;">👨‍🏫 Rabino:</strong> <span style="color: #000000;">{message["content"]}</span></div>', unsafe_allow_html=True)

def gerar_estudo():
    st.title("Gerador de Estudo da Parashá")
    
    # Garante que o diretório de estudos existe
    os.makedirs(STUDY_FOLDER, exist_ok=True)
    
    # Carrega o cache
    cache = load_cache()
    
    # Adiciona uma caixa de seleção com os nomes das parashiot
    parasha_name = st.selectbox(
        "Selecione a Parashá",
        options=sorted(PARASHA_REFERENCES.keys()),
        help="Escolha a parashá que você deseja estudar"
    )
    
    if st.button("Gerar Estudo"):
        try:
            with st.spinner(f"Obtendo texto para {parasha_name}..."):
                # Verifica cache
                if parasha_name in cache:
                    st.info(f"Usando texto em cache para {parasha_name}")
                    parasha_text = cache[parasha_name]
                else:
                    st.info(f"Obtendo texto para {parasha_name}")
                    parasha_text = get_parasha_text(parasha_name)
                    cache[parasha_name] = parasha_text
                    save_cache(cache)
            
            with st.spinner("Gerando estudo..."):
                study = generate_study_topics(parasha_text, client)
                
                # Salva o estudo no diretório de estudos
                now = datetime.now().strftime("%Y%m%d")
                safe_name = parasha_name.lower().replace(' ', '_')
                filename = f"estudo_{safe_name}_{now}.md"
                filepath = os.path.join(STUDY_FOLDER, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(study)
                
                st.success(f"Estudo salvo em: {filename}")
                
                # Formata e exibe o conteúdo
                st.markdown("""
                <style>
                .study-content {
                    background-color: #f8f9fa;
                    padding: 2rem;
                    border-radius: 0.5rem;
                    border-left: 5px solid #2778c4;
                    margin: 1rem 0;
                    color: #000000;
                }
                .study-content h1, .study-content h2, .study-content h3 {
                    color: #1f2937;
                    margin-top: 1.5rem;
                }
                .study-content ul {
                    margin-left: 1.5rem;
                }
                </style>
                """, unsafe_allow_html=True)
                
                st.markdown(f'<div class="study-content">{study}</div>', unsafe_allow_html=True)
                
                # Adiciona botão de download
                st.download_button(
                    label="📥 Download do Estudo",
                    data=study,
                    file_name=filename,
                    mime="text/markdown",
                )
                
        except Exception as e:
            st.error(f"Erro ao gerar estudo: {str(e)}\n\nVerifique se o nome da parashá está correto e tente novamente.")

def main():
    local_css()
    initialize_session_state()
    
    # Sidebar
    with st.sidebar:
        st.title("✡️ Parasha Study Creator")
        st.markdown('<p class="hebrew-text">ברוכים הבאים</p>', unsafe_allow_html=True)
        
        # Opções do modo
        mode = st.radio(
            "Escolha o modo:",
            ["Chat com Rabino", "Gerar Estudo da Parashá"]
        )
        
        if mode == "Chat com Rabino":
            st.markdown("### Histórico de Conversas")
            
            # Botão para nova conversa
            if st.button("Nova Conversa"):
                st.session_state.messages = [{"role": "system", "content": RABBI_SYSTEM_PROMPT}]
                st.session_state.conversation_name = None
                st.rerun()
            
            # Lista de conversas salvas
            histories = list_chat_histories()
            if histories:
                selected_history = st.selectbox(
                    "Carregar conversa:",
                    [""] + histories,
                    format_func=lambda x: "Selecione uma conversa..." if x == "" else x[:-5]
                )
                
                if selected_history and selected_history != st.session_state.conversation_name:
                    loaded_messages = load_chat_history(selected_history)
                    if loaded_messages:
                        st.session_state.messages = loaded_messages
                        st.session_state.conversation_name = selected_history
                        st.rerun()
            
            # Opção para salvar conversa
            if len(st.session_state.messages) > 1:  # Se há mensagens além do system prompt
                save_name = st.text_input("Nome para salvar:", 
                    value=st.session_state.conversation_name[:-5] if st.session_state.conversation_name else "")
                if st.button("Salvar Conversa"):
                    if save_name:
                        saved_name = save_chat_history(st.session_state.messages, save_name)
                        if saved_name:
                            st.session_state.conversation_name = saved_name
                            st.success(f"Conversa salva como: {saved_name}")
        
        st.markdown("### Ajuda")
        with st.expander("Ver comandos disponíveis"):
            st.markdown("""
            🔍 **Comandos:**
            - `/refs` - Busca referências nos textos
            - Exemplo: `/refs qual a importância do shabat?`
            
            📚 **Tópicos sugeridos:**
            - Torah e comentários
            - Halakhá (lei judaica)
            - Parashat Hashavua
            - Filosofia judaica
            - Kabbalah
            """)
    
    # Área principal
    if mode == "Chat com Rabino":
        st.header("💬 Chat com Rabino Virtual")
        
        # Exibe histórico do chat
        display_chat_history()
        
        # Campo de entrada
        user_input = st.chat_input("Digite sua pergunta aqui...")
        
        if user_input:
            # Verifica se é um comando de referência
            include_refs = user_input.startswith('/refs')
            if include_refs:
                query = user_input[5:].strip()
                
                with st.spinner("Buscando referências..."):
                    references = get_references_for_query(st.session_state.pdf_processor, query)
                
                if references:
                    st.markdown(f'<div class="chat-message refs-message"><strong style="color: #000000;">📚 Referências encontradas:</strong><br><span style="color: #000000;">{references}</span></div>', 
                              unsafe_allow_html=True)
                    
                    context_prompt = f"""Pergunta do usuário: {query}

Referências encontradas nos textos:
{references}

Por favor, responda à pergunta incorporando o conhecimento das referências fornecidas, citando-as quando apropriado."""
                    
                    st.session_state.messages.append({"role": "user", "content": context_prompt})
                else:
                    st.warning("Nenhuma referência relevante encontrada. Respondendo com conhecimento geral...")
                    st.session_state.messages.append({"role": "user", "content": query})
            else:
                st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Gera resposta
            with st.spinner("O Rabino está pensando..."):
                try:
                    response = client.chat.completions.create(
                        model=os.getenv("OPENAI_MODEL", "gpt-4"),
                        messages=st.session_state.messages,
                        temperature=0.13,
                    )
                    
                    rabbi_response = response.choices[0].message.content
                    st.session_state.messages.append({"role": "assistant", "content": rabbi_response})
                    
                    # Força atualização para mostrar nova mensagem
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Erro ao processar sua pergunta: {str(e)}")
    
    else:
        gerar_estudo()

if __name__ == "__main__":
    main()
