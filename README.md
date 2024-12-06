# Parasha Study Creator

Uma ferramenta para criar estudos bíblicos baseados em parashas (porções semanais da Torá), utilizando processamento de linguagem natural e busca semântica em referências.

## Funcionalidades

- Processamento de PDFs com referências e comentários
- Busca semântica usando embeddings OpenAI
- Armazenamento vetorial com Supabase
- Geração de estudos em formato Markdown
- Sistema de cache para otimização de processamento

## Requisitos

- Python 3.8+
- OpenAI API Key
- Supabase Account

## Configuração

1. Clone o repositório
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure as variáveis de ambiente em um arquivo `.env`:
   ```
   OPENAI_API_KEY=sua_chave_aqui
   SUPABASE_URL=sua_url_aqui
   SUPABASE_SERVICE_KEY=sua_chave_aqui
   ```
4. Execute o script de setup do Supabase (`supabase_setup.sql`)

## Uso

1. Coloque seus PDFs de referência na pasta `pdfs/`
2. Execute o script principal:
   ```bash
   python main.py
   ```

## Estrutura do Projeto

- `main.py`: Script principal que gerencia a criação dos estudos
- `pdf_processor.py`: Processamento de PDFs e busca semântica
- `supabase_setup.sql`: Script de configuração do Supabase
- `requirements.txt`: Dependências do projeto
- `clear_and_reprocess.py`: Utilitário para limpar cache e reprocessar PDFs
