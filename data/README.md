# Sistema RAG (Retrieval-Augmented Generation)

O sistema RAG permite que o bot responda perguntas baseadas em documentos específicos da sua empresa, combinando busca inteligente com geração de texto da IA.

## Arquivos de Exemplo Incluídos

- **`manual_empresa.txt`** - Manual de exemplo da empresa TechCorp com informações detalhadas
- **`perguntas_teste.txt`** - Lista de 50 perguntas para testar o funcionamento do RAG

## Como Utilizar

### 1. Adicionar Documentos
Coloque seus documentos na pasta `data/documents/` nos formatos suportados.

### 2. Indexar Documentos
```bash
docker exec -it wpp_bot_api python /app/bot/rag.py
```

### 3. Testar o Sistema
O bot automaticamente usará o RAG para responder perguntas baseadas nos documentos indexados.

## Formatos Suportados

- **PDF** (.pdf) - Documentos em PDF
- **CSV** (.csv) - Planilhas e dados tabulares
- **TXT** (.txt) - Arquivos de texto simples
- **Markdown** (.md) - Documentação em Markdown
- **Word** (.doc, .docx) - Documentos do Microsoft Word

## Dicas para Melhor Performance

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
```markdown
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

**Sempre reindexe após adicionar/remover arquivos:**

```bash
docker exec -it wpp_bot_api python /app/bot/rag.py
```
