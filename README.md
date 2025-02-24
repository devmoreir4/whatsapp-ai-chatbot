# Itabapoana Alerta

Itabapoana Alerta é um bot de inteligência artificial integrado ao WhatsApp, desenvolvido para monitorar o Rio Itabapoana e as condições climáticas do município de Bom Jesus do Itabapoana. O sistema fornece informações em tempo real, como medições do nível do rio, cota de transbordamento, gráficos dinâmicos e acesso a câmeras de monitoramento, combinando dados históricos com previsões climáticas para apoiar a prevenção de desastres e a gestão de riscos ambientais.


## Descrição

O projeto **Itabapoana Alerta** integra:
- Uma API desenvolvida em Flask para processar mensagens e comandos do WhatsApp;
- Um módulo de IA que utiliza LangChain e o modelo ChatGroq (Llama-3.1-8b-instant) para fornecer respostas contextuais;
- Scripts para geração de gráficos dinâmicos com Matplotlib;
- Integração com a API do OpenWeatherMap para dados climáticos;
- Técnicas de Recuperação Aumentada de Geração (RAG) para indexação e recuperação de informações a partir de documentos;
- Orquestração via Docker e Docker Compose para facilitar a implantação e escalabilidade do sistema.


## Funcionalidades

- **Monitoramento do Rio:**
  - Consulta em tempo real do nível do rio e cota de transbordamento.
- **Gráficos Dinâmicos:**
  - Geração de gráficos do nível do rio nas últimas 24 horas.
  - Geração de gráficos de previsão de temperatura para os próximos 5 dias.
- **Câmera de Monitoramento:**
  - Disponibilização de link para acesso à câmera de monitoramento local.
- **Dados Climáticos:**
  - Consulta de temperatura, umidade do ar, velocidade do vento e condições meteorológicas atuais via API do OpenWeatherMap.
- **Integração com IA:**
  - Respostas inteligentes e contextualizadas utilizando técnicas de RAG, combinando dados históricos e diretrizes operacionais.


## Tecnologias Utilizadas

- **Python 3.11**
- **Flask:** Framework para desenvolvimento da API web.
- **Docker & Docker Compose:** Para containerização e orquestração dos serviços.
- **Waha API:** Serviço utilizado para a comunicação e integração com o WhatsApp.
- **LangChain:** Framework para integração com modelos de linguagem e recuperação de informações.
- **ChatGroq (Llama-3.1-8b-instant):** Modelo de linguagem utilizado para geração de respostas inteligentes.
- **Chroma:** Vector store para indexação e busca semântica dos dados.
- **HuggingFace Embeddings:** Geração de embeddings para processamento dos documentos.
- **Matplotlib:** Biblioteca para criação de gráficos dinâmicos.
- **BeautifulSoup:** Realiza o web scraping dos dados do site do INEA.
- **OpenWeatherMap API:** Para obtenção de informações climáticas em tempo real.


## Instalação e Execução

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/devmoreir4/whatsapp-ai-chatbot.git
   cd whatsapp-ai-chatbot
   ```

2. **Configure as variáveis de ambiente:**<br>
    Crie um arquivo .env na raiz do projeto baseado no arquivo `.env.example` e defina suas variáveis de ambiente.

3. **Construa e inicie os containers:**
   ```bash
   docker-compose up --build
   ```

4. **Acesso aos Serviços:** 
    - API Flask: Disponível na porta [5000](http://127.0.0.1:5000).
    - Serviço Waha (WhatsApp): Disponível na porta [3000](http://127.0.0.1:3000).

5. **Configuração do WhatsApp:**
    - Acesse o [Dashboard do WAHA](http://[::1]:3000/dashboard/).
    - Inicie uma nova sessão com um dispositivo.
    - No painel de configurações, adicione um Webhook com a URL:
    ```bash
    http://api:5000/chatbot/webhook/
    ```
    - Selecione somente o evento `message` para receber notificações de novas mensagens.
    - Após a sincronização do serviço, o bot estará ativo e pronto para operar.

    OBS: Caso deseje adaptar o bot para o seu contexto, basta alterar os arquivos no diretório `rag/data` e executar o arquivo rag.py dentro do container da api.
    ```bash
    docker exec -it <nome_do_container> /bin/bash
    python /app/rag/rag.py
    ```


## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir *issues* ou enviar *pull requests* para contribuir com o projeto.

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
