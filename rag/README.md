# RAG do bot

A pasta `data` contém os documentos que serão indexados pelo sistema RAG do bot.

## Arquivos de Exemplo Incluídos

- **`manual_empresa.txt`** - Manual de exemplo da empresa TechCorp com informações detalhadas
- **`perguntas_teste.txt`** - Lista de 50 perguntas para testar o funcionamento do RAG

## Como Testar o RAG

### 1. Reindexe os documentos:
```bash
docker exec -it wpp_bot_api python /app/rag/rag.py
```

### 2. Teste com perguntas simples:
- "Qual é o nome da empresa?"
- "Qual o telefone da TechCorp?"
- "Quais são os horários de funcionamento?"

### 3. Teste com perguntas complexas:
- "Me explique todo o processo de desenvolvimento"
- "Quais são todas as certificações da empresa?"
- "Como funciona o atendimento ao cliente?"

### 4. Teste perguntas que devem falhar:
- "Qual o preço do iPhone?"
- "Como fazer um bolo?"
- "Qual a capital da França?"

## Formatos Suportados

- **PDF** (.pdf) - Documentos em PDF
- **CSV** (.csv) - Planilhas e dados tabulares
- **TXT** (.txt) - Arquivos de texto simples
- **Markdown** (.md) - Documentação em Markdown
- **Word** (.doc, .docx) - Documentos do Microsoft Word

## Dicas para Melhor Performance do RAG

### Estrutura de Documentos:
- **Use títulos claros** (# Título, ## Subtítulo)
- **Organize por seções** (Informações, Serviços, Contatos, etc.)
- **Inclua perguntas e respostas** (FAQ)
- **Use listas** para informações estruturadas

### Conteúdo Ideal:
- **Informações específicas** (nomes, números, datas)
- **Procedimentos passo a passo**
- **Perguntas frequentes**
- **Contatos e horários**
- **Políticas e regras**

### Exemplo de Estrutura:
```
# Manual da Empresa

## Informações Básicas
- Nome: Empresa XYZ
- Telefone: (11) 99999-9999
- Email: contato@empresa.com

## Serviços
1. Desenvolvimento de Software
2. Consultoria em TI
3. Suporte Técnico

## FAQ
**P: Qual o prazo de entrega?**
R: O prazo mínimo é de 30 dias úteis.
```

## Reindexação

Sempre reindexe após adicionar/remover arquivos. Para atualizar a base de conhecimento:

```bash
# Do host
docker exec -it wpp_bot_api python /app/rag/rag.py

# Dentro do container
python /app/rag/rag.py
```
