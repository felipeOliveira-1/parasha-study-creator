# Parasha Study Creator

Ferramenta automatizada para geração de estudos aprofundados de parashot (porções semanais da Torá), integrando inteligência artificial, tradição judaica e customização total do formato do estudo.

---

## ✨ Principais Funcionalidades

- **Geração automática de estudos completos** a partir do nome da porção semanal da Torá
- **Resumo detalhado do Daf Yomi** (uma página diária do Talmud), estruturado em tópicos, com introdução e conclusão, seguindo modelo didático
- **Prompt avançado** com contexto de Halachá, Cabalá, Mussar, Chassidut e referências autênticas
- **Personalização total do formato**: basta editar o arquivo `studies/EXEMPLO_FORMATO.md` (para Parashá) ou `EXEMPLO_DAF_YOMI.md` (para Daf Yomi) para mudar o modelo de saída
- **Salva os estudos em Markdown** no diretório `studies/`
- **Fluxo 100% automatizado**: o usuário só escolhe o tipo de estudo e recebe o arquivo pronto
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
- Edite o arquivo `studies/modelos/EXEMPLO_FORMATO.md` para definir o modelo, tópicos, citações e sugestões práticas que deseja em todos os estudos gerados.

### 5. Inicie o servidor MCP antes de gerar estudos
Antes de rodar o script principal, é necessário iniciar o servidor MCP manualmente em um terminal separado:
```bash
python src/mcp_server.py
```
Mantenha esse terminal aberto enquanto utiliza o sistema.

### 6. Gerando um estudo ou resumo do Daf Yomi
```bash
python src/criar_estudo.py
```
Você verá o seguinte menu:

```
=== Gerador de Estudos ===
Escolha o tipo de estudo:
[1] Parashá da semana
[2] Resumo em tópicos do Daf Yomi
Digite 1 ou 2: 
```

- Para Parashá: digite `1` e siga como antes (nome da porção, ex: Shemini). O estudo será salvo em `studies/NOME_DA_PORCAO.md`.
- Para Daf Yomi: digite `2` e informe o Daf (ex: `Makkot 7`). O resumo será salvo em `studies/Makkot_7.md`.

O resumo do Daf Yomi seguirá o modelo de `studies/modelos/EXEMPLO_DAF_YOMI.md` (totalmente editável).

---

## 🗂️ Estrutura do Projeto
```
parasha-study-creator/
├── src/
│   ├── criar_estudo.py           # Script principal para gerar estudos
│   └── mcp_server.py             # Servidor MCP (Model Context Protocol)
├── requirements.txt          # Dependências Python
├── .env                      # Variáveis sensíveis (OpenAI API Key)
├── config/
│   └── mcp_config.json           # Configurações do MCP
├── docs/
│   └── sefaria.md                # Documentação extra
├── studies/
│   ├── modelos/
│   │   ├── EXEMPLO_FORMATO.md    # Modelo de formatação do estudo da Parashá
│   │   └── EXEMPLO_DAF_YOMI.md   # Modelo de resumo do Daf Yomi (editável)
│   └── <Estudo>.md               # Estudos gerados (Parashá ou Daf Yomi)
└── README.md
```

---

## 🧠 Como funciona?
- O usuário executa `criar_estudo.py` e escolhe:
  - **[1] Parashá da semana**: informa o nome da porção e recebe um estudo aprofundado, seguindo o modelo de `EXEMPLO_FORMATO.md`.
  - **[2] Daf Yomi**: informa o Daf (ex: Makkot 7) e recebe um resumo detalhado, estruturado em tópicos, conforme `EXEMPLO_DAF_YOMI.md`.
- O usuário deve garantir que o servidor MCP (`mcp_server.py`) está rodando manualmente antes de executar o `criar_estudo.py`. O script principal faz a requisição ao MCP já em execução.
- O servidor lê o arquivo de exemplo correspondente e instrui a IA a seguir exatamente aquele modelo, trazendo sempre referências, estrutura e sugestões práticas.
- O estudo/resumo é salvo automaticamente em Markdown.

---

## 🛠️ Personalização Avançada
- **Quer mudar o formato dos estudos da Parashá?** Basta editar `studies/modelos/EXEMPLO_FORMATO.md`.
- **Quer mudar o formato do resumo do Daf Yomi?** Edite `studies/modelos/EXEMPLO_DAF_YOMI.md`.
- **Quer mudar o prompt/contexto?** Edite o bloco de prompt em `src/mcp_server.py`.
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

