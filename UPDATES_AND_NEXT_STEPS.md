 # Atualizações e Próximas Tarefas

 ## Atualizações Realizadas

 - **Requisito de Python**: atualizado de 3.8+ para 3.10+ no README.md.
 - **Dependências**: limpezas em backend/requirements.txt:
   - Removidas: pypdf, ebooklib, beautifulsoup4, html2text, tiktoken, langchain, langchain-community, langchain-openai, tqdm.
   - Adicionadas: tenacity, pydantic.
 - **Variáveis de ambiente**:
   - Atualização da chave `OPENAI_API_KEY` em `.env`.
   - Criação recomendada de um arquivo modelo `.env.example` para documentar as variáveis (sem expor segredos).

 ## Próximas Tarefas

 1. **Histórico de Estudos**  
    Implementar ou remover o endpoint `/api/studies/history` (função `get_study_history`) em `backend/app/services/study_service.py`.
 2. **Testes e CI**  
    Criar suítes de testes com `pytest` para serviços (`parasha_service`, `study_service`, `commentaries_service`)  
    Configurar pipeline de CI para lint (Flake8), type-check (mypy) e execução de testes.
 3. **Licença**  
    Incluir ou atualizar arquivo `LICENSE.md` (licença MIT).
 4. **Configuração do Frontend**  
    Parametrizar a URL do backend no frontend via variável de ambiente (ex.: `VITE_API_BASE_URL`).
 5. **Containerização**  
    Adicionar suporte a Docker e `docker-compose` para facilitar o setup local e deploy.