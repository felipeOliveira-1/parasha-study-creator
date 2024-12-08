# Parasha Study Creator

Uma ferramenta avançada para geração de estudos da Torá, combinando tecnologia moderna com sabedoria tradicional judaica. O sistema integra processamento de linguagem natural, busca semântica e IA para criar estudos profundos e significativos das parashiot (porções semanais da Torá).

## Visão Geral do Sistema

O Parasha Study Creator é composto por vários módulos especializados que trabalham em conjunto:

### Componentes Principais

1. **main.py**
   - Ponto de entrada do sistema
   - Gerencia o fluxo principal de execução
   - Implementa interface de chat com "Rabino Virtual"
   - Gerencia histórico de conversas e cache
   - Coordena integração entre módulos

2. **parasha.py**
   - Gerencia textos das 54 parashiot do ciclo anual
   - Integra com API do Sefaria para obtenção de textos
   - Mapeia referências bíblicas precisas
   - Organiza textos por livro da Torá

3. **study_generator.py**
   - Gera estudos estruturados usando IA
   - Cria resumos e tópicos de estudo
   - Integra análise Mussar (ética judaica)
   - Incorpora comentários rabínicos

4. **prompt_library.py**
   - Biblioteca de templates XML para IA
   - Define estrutura precisa para cada componente
   - Garante consistência na geração de conteúdo
   - Implementa limites e regras específicas

5. **pdf_processor.py**
   - Processa PDFs e EPUBs de fontes judaicas
   - Cria embeddings usando OpenAI
   - Implementa busca semântica híbrida
   - Gerencia armazenamento no Supabase

## Funcionalidades Detalhadas

### Processamento de Textos
- Processamento automático de PDFs e EPUBs
- Divisão inteligente em chunks com sobreposição
- Sistema de cache para otimização
- Controle de versão de documentos

### Busca Semântica Avançada
- Busca híbrida (85% semântica, 15% keywords)
- Análise sofisticada de relevância
- Expansão automática de contexto
- Integração com Supabase Vector Store

### Geração de Estudos
- Resumos concisos e significativos
- Tópicos de estudo estruturados
- Análise ética (Mussar)
- Aplicações práticas modernas
- Integração de comentários clássicos

### Interface Interativa
- Chat com "Rabino Virtual"
- Comandos especiais:
  - `/help`: Guia completo
  - `/refs`: Busca referências
  - `/save`: Salva conversas
- Sistema de histórico de conversas

## Requisitos Técnicos

### Dependências
- Python 3.8+
- OpenAI API
- Supabase
- Langchain
- BeautifulSoup4
- PyPDF2
- EbookLib

### Variáveis de Ambiente (.env)
```
OPENAI_API_KEY=sua_chave_aqui
OPENAI_MODEL=gpt-4o
OPENAI_ORG=sua_org_aqui
SUPABASE_URL=sua_url_aqui
SUPABASE_SERVICE_KEY=sua_chave_aqui
PDF_FOLDER=livros
CACHE_FILE=parasha_cache.json
STUDY_FOLDER=estudos
CHAT_HISTORY_FOLDER=conversas
```

## Configuração e Instalação

1. Clone o repositório:
   ```bash
   git clone [url-do-repositorio]
   cd parasha-study-creator
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure o ambiente:
   - Crie arquivo `.env` com as variáveis necessárias
   - Crie as pastas necessárias:
     - `livros/` para PDFs e EPUBs
     - `estudos/` para output
     - `conversas/` para histórico

4. Configure o Supabase:
   - Execute `supabase_setup.sql`
   - Verifique configuração da tabela `documents`

## Uso do Sistema

### Processamento Inicial
1. Adicione documentos na pasta `livros/`
2. Execute processamento inicial:
   ```bash
   python main.py --process-docs
   ```

### Geração de Estudos
1. Execute o programa:
   ```bash
   python main.py
   ```
2. Use comandos disponíveis:
   - Digite nome da parashá para gerar estudo
   - Use `/refs` para buscar referências
   - Use `/save` para salvar conversas

## Estrutura de Arquivos
```
parasha-study-creator/
├── main.py              # Ponto de entrada
├── parasha.py           # Gerenciador de parashiot
├── study_generator.py   # Gerador de estudos
├── prompt_library.py    # Templates de IA
├── pdf_processor.py     # Processador de documentos
├── requirements.txt     # Dependências
├── .env                 # Configurações
├── livros/             # PDFs e EPUBs
├── estudos/            # Estudos gerados
└── conversas/          # Histórico de chat
```

## Notas Técnicas

### Sistema de Cache
- Controle de arquivos processados
- Hash de verificação de mudanças
- Otimização de reprocessamento

### Busca Semântica
- Embeddings via OpenAI
- Vector store no Supabase
- Sistema de scoring sofisticado
- Expansão contextual inteligente

### Geração de Conteúdo
- Templates XML estruturados
- Limites específicos por seção
- Sistema de retry em falhas
- Validação de output

## Contribuição

Para contribuir com o projeto:
1. Fork o repositório
2. Crie uma branch para sua feature
3. Faça commit das mudanças
4. Push para a branch
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
