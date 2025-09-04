<h1 align="center">
    WhatsApp AI Chatbot
</h1>

<p align="center">
  <a href="#descrição">Descrição</a> •
  <a href="#funcionalidades">Funcionalidades</a> •
  <a href="#tecnologias-utilizadas">Tecnologias</a> •
  <a href="#instalação-e-execução">Instalação</a> •
  <a href="#personalização">Personalização</a> •
  <a href="#licença">Licença</a>
</p>

<p align="center">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python" alt="Python">
  </a>
  <a href="https://fastapi.tiangolo.com/">
    <img src="https://img.shields.io/badge/FastAPI-0.116.1+-green?style=flat-square&logo=fastapi" alt="FastAPI">
  </a>
  <a href="https://www.docker.com/">
    <img src="https://img.shields.io/badge/Docker-Compose-blue?style=flat-square&logo=docker" alt="Docker">
  </a>
  <a href="https://langchain.com/">
    <img src="https://img.shields.io/badge/LangChain-0.3.27+-orange?style=flat-square&logo=langchain" alt="LangChain">
  </a>
  <a href="https://www.whatsapp.com/">
    <img src="https://img.shields.io/badge/WhatsApp-Integration-green?style=flat-square&logo=whatsapp" alt="WhatsApp">
  </a>
</p>

Um bot de inteligência artificial integrado ao WhatsApp que utiliza técnicas de RAG (Retrieval-Augmented Generation) para responder perguntas baseadas em documentos carregados em sua memória. O sistema combina busca semântica com geração de respostas contextuais para fornecer informações precisas e relevantes.

## Descrição

O projeto **WhatsApp AI Chatbot** integra:
- Uma API desenvolvida em FastAPI para processar mensagens e comandos do WhatsApp;
- Um módulo de IA que utiliza LangChain e modelos OpenAI para fornecer respostas contextuais;
- Sistema RAG avançado para indexação e recuperação de informações a partir de múltiplos formatos de documento;
- Sistema de debounce inteligente para agrupar mensagens rápidas;
- Suporte a diversos tipos de arquivo (PDF, CSV, TXT, MD, DOC, DOCX);
- Orquestração via Docker e Docker Compose para facilitar a implantação e escalabilidade do sistema.

## Funcionalidades

- **Sistema RAG Inteligente:**
  - Busca semântica em documentos carregados
  - Respostas contextuais baseadas no conhecimento disponível
  - Suporte a múltiplos formatos de arquivo
  - Conversação natural e intuitiva
- **Integração WhatsApp:**
  - Respostas em tempo real via WhatsApp
  - Histórico de conversa mantido
  - Indicadores de digitação
- **API Moderna e Performática:**
  - Processamento assíncrono com FastAPI
  - Documentação automática em `/docs`
  - Health check em `/health`
- **Sistema de Debounce Inteligente:**
  - Agrupa mensagens rápidas para evitar spam
  - Configurável via variáveis de ambiente
  - Melhora a experiência do usuário


## Tecnologias Utilizadas

- **Python 3.11**
- **FastAPI:** Framework moderno e de alta performance para desenvolvimento da API web
- **Docker & Docker Compose:** Para containerização e orquestração dos serviços
- **Waha API:** Serviço utilizado para a comunicação e integração com o WhatsApp
- **LangChain:** Framework para integração com modelos de linguagem e recuperação de informações
- **OpenAI:** Modelos de linguagem para geração de respostas inteligentes (configurável)
- **ChromaDB:** Vector store para indexação e busca semântica dos dados
- **OpenAI Embeddings:** Geração de embeddings para processamento dos documentos
- **Redis:** Sistema de cache e debounce de mensagens
- **Múltiplos Loaders:** Suporte a PDF, CSV, TXT, MD, DOC, DOCX


## Instalação e Execução

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/devmoreir4/whatsapp-ai-chatbot.git
   cd whatsapp-ai-chatbot
   ```

2. **Configure as variáveis de ambiente:**<br>
    Crie um arquivo .env na raiz do projeto conforme o arquivo `.env.example` e defina as suas variáveis.

3. **Construa e inicie os containers:**
   ```bash
   docker-compose up --build
   ```

4. **Acesso aos Serviços:**
    - **API FastAPI**: Disponível na porta 5000
    - **Documentação automática**: [http://127.0.0.1:5000/docs](http://127.0.0.1:5000/docs)
    - **Serviço Waha (WhatsApp)**: Disponível na porta [3000](http://127.0.0.1:3000)
    - **Redis**: Disponível na porta 6379

    ### Endpoints da API

    - **POST** `/chatbot/webhook/` - Webhook para receber mensagens do WhatsApp
    - **GET** `/health` - Status de saúde da aplicação
    - **GET** `/buffer/status/{chat_id}` - Status do buffer de mensagens
    - **POST** `/buffer/cleanup` - Limpeza de tarefas expiradas

5. **Configuração do WhatsApp:**
    - Acesse o [Dashboard do WAHA](http://[::1]:3000/dashboard/).
    - Inicie uma nova sessão com um dispositivo.
    - No painel de configurações, adicione um Webhook com a URL:
    ```bash
    http://api:5000/chatbot/webhook/
    ```
    - Selecione somente o evento `message` para receber notificações de novas mensagens.
    - Após a sincronização do serviço, o bot estará ativo e pronto para operar.

6. **Configuração da Base de Conhecimento:**
    - Adicione seus documentos na pasta `rag/data/`
    - Formatos suportados: PDF, CSV, TXT, MD, DOC, DOCX
    - Execute o script de indexação:
    ```bash
    docker exec -it wpp_bot_api python /app/rag/rag.py
    ```
    - O bot estará pronto para responder perguntas baseadas nos documentos carregados.

## Personalização

### Adicionando Documentos

1. Copie seus arquivos para `rag/data/`
2. Execute a reindexação:
   ```bash
   docker exec -it wpp_bot_api python /app/rag/rag.py
   ```

### Formatos Suportados

- **PDF** - Documentos em PDF
- **CSV** - Planilhas e dados tabulares
- **TXT** - Arquivos de texto simples
- **MD** - Documentação em Markdown
- **DOC/DOCX** - Documentos do Microsoft Word

## Licença

Este projeto está licenciado sob a licença [MIT](LICENSE).
