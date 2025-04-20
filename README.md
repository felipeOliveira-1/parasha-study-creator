# Parasha Study Creator

Ferramenta automatizada para geração de estudos aprofundados de parashot (porções semanais da Torá), integrando inteligência artificial, tradição judaica e customização total do formato do estudo.

---

## ✨ Principais Funcionalidades

- **Geração automática de estudos completos** a partir do nome da porção
- **Prompt avançado** com contexto de Halachá, Cabalá, Mussar, Chassidut e referências autênticas
- **Personalização total do formato**: basta editar o arquivo `studies/EXEMPLO_FORMATO.md` para mudar o modelo de saída
- **Salva os estudos em Markdown** no diretório `studies/`
- **Fluxo 100% automatizado**: o usuário só digita o nome da porção e recebe o estudo pronto
- **Utiliza OpenAI GPT-4.1 e Sefaria API** para geração e enriquecimento do conteúdo

---

## 🚀 Como Usar

### 1. Pré-requisitos
- Python 3.10+
- Chave de API do OpenAI (`OPENAI_API_KEY`)

### 2. Instalação
```bash
pip install -r requirements.txt
```

### 3. Configuração
- Copie `.env.example` para `.env` e coloque sua chave OpenAI:
  ```env
  OPENAI_API_KEY=sua_chave_aqui
  ```

### 4. Personalize o formato do estudo (opcional)
- Edite o arquivo `studies/EXEMPLO_FORMATO.md` para definir o modelo, tópicos, citações e sugestões práticas que deseja em todos os estudos gerados.

### 5. Gerando um estudo
```bash
python criar_estudo.py
```
Digite o nome da porção (ex: Shemini) quando solicitado. O estudo será salvo automaticamente em `studies/NOME_DA_PORCAO.md`.

---

## 🗂️ Estrutura do Projeto
```
parasha-study-creator/
├── criar_estudo.py           # Script principal para gerar estudos
├── mcp_server.py             # Servidor MCP (Model Context Protocol)
├── requirements.txt          # Dependências Python
├── .env                      # Variáveis sensíveis (OpenAI API Key)
├── studies/
│   ├── EXEMPLO_FORMATO.md    # Modelo de formatação do estudo
│   └── <Parasha>.md          # Estudos gerados
└── README.md
```

---

## 🧠 Como funciona?
- O usuário executa `criar_estudo.py` e informa o nome da porção.
- O script garante que o servidor MCP está rodando e faz a requisição.
- O servidor lê o arquivo de exemplo (`EXEMPLO_FORMATO.md`) e instrui a IA a seguir exatamente aquele modelo, trazendo sempre referências, estrutura e sugestões práticas.
- O estudo é salvo automaticamente em Markdown.

---

## 🛠️ Personalização Avançada
- **Quer mudar o formato dos estudos?** Basta editar `studies/EXEMPLO_FORMATO.md`.
- **Quer mudar o prompt/contexto?** Edite o bloco de prompt em `mcp_server.py`.
- **Quer gerar estudos para todas as parashiot de uma vez?** Peça por um script de automação!

---

## 📚 Tecnologias Utilizadas
- Python 3.10+
- OpenAI API (GPT-4)
- Sefaria API (textos judaicos)
- python-dotenv
- requests

---

## 🤝 Contribuição
1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)

---

## 📄 Licença
MIT

