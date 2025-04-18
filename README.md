# Parasha Study Creator

Uma ferramenta avançada para geração de estudos da Torá, combinando tecnologia moderna com sabedoria tradicional judaica. O sistema utiliza a API do OpenAI e Sefaria para criar estudos profundos e significativos das parashiot (porções semanais da Torá), incluindo análises de Mussar (ética judaica).

## Funcionalidades Principais

- **Geração de Estudos Completos**:
  - Resumo da parashá
  - Temas principais
  - Tópicos de estudo aprofundados
  - Análise Mussar personalizada
  - Referências de obras clássicas de Mussar

- **Integração com Sefaria**:
  - Busca automática de textos relevantes
  - Referências precisas de obras clássicas
  - Textos originais em hebraico com tradução

- **Interface Moderna e Responsiva**:
  - Design limpo e intuitivo
  - Suporte a dispositivos móveis
  - Visualização otimizada de textos em hebraico

## Estrutura do Projeto

### Backend (Flask)

O backend é construído com Flask e oferece uma API RESTful para:
- Gerenciamento de parashiot
- Geração de estudos com OpenAI
- Integração com a API do Sefaria
- Tradução automática de textos

#### Estrutura de Diretórios
```
backend/
├── app/
│   ├── routes/          # Rotas da API
│   │   ├── parashot.py  # Endpoints de parashiot
│   │   └── studies.py   # Endpoints de estudos
│   ├── services/        # Lógica de negócio
│   │   ├── parasha_service.py    # Serviço de parashiot
│   │   ├── study_service.py      # Serviço de estudos
│   │   └── prompts.py            # Templates de prompts
│   └── __init__.py      # Configuração do Flask
├── requirements.txt    # Dependências Python
└── wsgi.py            # Ponto de entrada
```

### Frontend (React + TypeScript + Vite)

Interface moderna construída com React, TypeScript e Vite, oferecendo:
- Seleção intuitiva de parashiot
- Visualização clara dos estudos gerados
- Exibição de textos em hebraico e português
- Design responsivo com Tailwind CSS

#### Estrutura de Diretórios
```
frontend/
├── src/
│   ├── App.tsx         # Componente principal
│   ├── components/     # Componentes React
│   ├── assets/        # Recursos estáticos
│   └── styles/        # Estilos CSS
├── public/           # Arquivos públicos
└── package.json     # Dependências Node.js
```

## Configuração e Execução

### Pré-requisitos

- Python 3.10+
- Node.js 16+
- NPM ou Yarn
- Chave de API do OpenAI

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
FLASK_ENV=development
```

4. Execute o servidor:
```bash
python -m flask --app backend/wsgi.py run --debug
```

### Frontend

1. Instale as dependências:
```bash
cd frontend
npm install
```

2. Execute em modo desenvolvimento:
```bash
npm run dev
```

O frontend estará disponível em `http://localhost:5173` e se comunicará com o backend em `http://localhost:5000`.

## Tecnologias Utilizadas

### Backend
- Flask (Framework web)
- OpenAI API (Geração de texto)
- Sefaria API (Textos judaicos)
- Python-dotenv (Configuração)

### Frontend
- React 18
- TypeScript
- Vite
- Tailwind CSS
- Axios

## Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
