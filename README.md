# Parasha Study Creator

Uma ferramenta avançada para geração de estudos da Torá, combinando tecnologia moderna com sabedoria tradicional judaica. O sistema integra processamento de linguagem natural, busca semântica e IA para criar estudos profundos e significativos das parashiot (porções semanais da Torá).

## Estrutura do Projeto

O projeto está organizado em duas partes principais:

### Backend (Flask)

O backend é construído com Flask e oferece uma API RESTful para:
- Gerenciamento de parashiot
- Geração de estudos
- Autenticação de usuários
- Busca semântica em textos judaicos

#### Estrutura de Diretórios
```
backend/
├── app/
│   ├── routes/          # Rotas da API
│   ├── services/        # Lógica de negócio
│   └── __init__.py      # Configuração do Flask
├── venv/               # Ambiente virtual Python
├── config.py          # Configurações
├── requirements.txt   # Dependências
├── schema.sql        # Esquema do banco
└── wsgi.py           # Ponto de entrada
```

### Frontend (React + TypeScript)

Interface moderna e responsiva construída com React e TypeScript, oferecendo:
- Interface intuitiva para estudos
- Chat com "Rabino Virtual"
- Visualização de parashiot e comentários
- Gerenciamento de estudos salvos

#### Estrutura de Diretórios
```
frontend/
├── src/
│   ├── components/     # Componentes React
│   ├── pages/         # Páginas da aplicação
│   ├── services/      # Chamadas à API
│   └── types/         # Tipos TypeScript
├── public/           # Arquivos estáticos
└── package.json     # Dependências
```

## Configuração e Execução

### Backend

1. Crie e ative o ambiente virtual:
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Linux/Mac
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente (.env):
```env
OPENAI_API_KEY=sua_chave_aqui
OPENAI_MODEL=gpt-4o
SUPABASE_URL=sua_url_aqui
SUPABASE_SERVICE_KEY=sua_chave_aqui
```

4. Execute o servidor:
```bash
python wsgi.py
```

### Frontend

1. Instale as dependências:
```bash
cd frontend
npm install
```

2. Configure as variáveis de ambiente (.env.local):
```env
VITE_API_URL=http://localhost:5000
```

3. Execute em modo desenvolvimento:
```bash
npm run dev
```

4. Para build de produção:
```bash
npm run build
```

## Funcionalidades

### API Backend
- `/api/parashot`: Gerenciamento de parashiot
- `/api/studies`: Geração e consulta de estudos
- `/api/auth`: Autenticação e autorização
- `/api/search`: Busca semântica em textos

### Interface Frontend
- Visualização de parashiot
- Geração de estudos personalizados
- Chat interativo com IA
- Busca em textos judaicos
- Gerenciamento de estudos salvos

## Tecnologias Principais

### Backend
- Flask (Framework Web)
- OpenAI API (GPT-4o)
- Supabase (Banco de dados e Autenticação)
- LangChain (Processamento de LLM)

### Frontend
- React 18
- TypeScript
- Vite
- TailwindCSS

## Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
