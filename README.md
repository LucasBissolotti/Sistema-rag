# Sistema RAG - Busca Inteligente em Documentos

Um sistema completo de RAG (Retrieval-Augmented Generation) para busca inteligente em documentos locais usando embeddings e LLMs locais.

## 📋 Visão Geral

Este sistema permite indexar documentos locais (PDF, DOCX, TXT), gerar embeddings para busca semântica e utilizar modelos de linguagem (LLMs) para responder perguntas com base no conteúdo dos documentos. Tudo funcionando de forma local e privada.

### ✨ Características

- ✅ Processamento de documentos em múltiplos formatos (PDF, DOCX, TXT)
- ✅ Geração e armazenamento de embeddings
- ✅ Busca semântica com banco de dados vetorial (ChromaDB)
- ✅ Integração com modelos LLM locais (Ollama, Llama.cpp, GPT4All)
- ✅ Interface de linha de comando amigável
- ✅ Interface web simples e elegante
- ✅ Sistema de log completo
- ✅ Cache de embeddings para melhor performance

## 🚀 Instalação

### Pré-requisitos
- Python 3.8 ou superior
- Pip (gerenciador de pacotes Python)
- Opcional: Ollama para LLMs locais ([Instalação do Ollama](https://github.com/ollama/ollama))

### Passos para instalação

1. **Clone o repositório**
   ```bash
   git clone https://github.com/[seu-username]/sistema-rag.git
   cd sistema-rag
   ```

2. **Crie e ative o ambiente virtual**
   ```bash
   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r config/requirements.txt
   ```

## ⚙️ Configuração

### Arquivo de configuração

Edite o arquivo [`config/config.yaml`](config/config.yaml) para ajustar as configurações do sistema:

```yaml
# Principais configurações disponíveis
documentos:
  pasta: "./data/documents"      # Pasta onde seus documentos serão armazenados
  formatos_suportados:           # Formatos de documento suportados
    - ".pdf"
    - ".docx"
    - ".txt"

processamento:
  tamanho_chunk: 500             # Tamanho dos chunks de texto
  sobreposicao_chunk: 100        # Sobreposição entre chunks

embeddings:
  modelo: "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"  # Modelo de embeddings
  cache_ativo: true              # Ativar cache de embeddings

llm:
  modelo: "ollama"               # Tipo de LLM a ser usado
  parametros:
    temperatura: 0.7             # Temperatura do modelo
```

### Documentos

Coloque seus documentos na pasta `data/documents`. O sistema suporta:
- Arquivos PDF (`.pdf`)
- Documentos Word (`.docx`)
- Arquivos de texto (`.txt`)

## 💻 Como Usar

### Interface de Linha de Comando (CLI)

Execute o sistema a partir da linha de comando:

```bash
python src/main.py
```

Você verá um menu com as seguintes opções:

1. **📚 Indexar documentos**  
   - Processa e indexa todos os documentos na pasta configurada
   - Gera embeddings e armazena no banco de dados vetorial
   - Permite reindexar todos os documentos

2. **❓ Fazer pergunta**  
   - Faça perguntas em linguagem natural sobre o conteúdo dos documentos
   - O sistema busca as informações relevantes e gera respostas baseadas nos documentos

3. **📊 Status do sistema**  
   - Visualize estatísticas sobre documentos indexados e status dos componentes

4. **🚪 Sair**  
   - Encerra o sistema

### Interface Web

Para iniciar a interface web:

```bash
python src/web/app.py
```

Acesse no navegador: http://localhost:5000

## 🧩 Arquitetura do Sistema

O sistema é composto pelos seguintes componentes:

- **Processador de Documentos**: Carrega e fragmenta documentos em chunks de texto
- **Gerenciador de Embeddings**: Gera e gerencia embeddings usando modelos de transformers
- **Banco de Dados Vetorial**: Armazena e recupera embeddings usando ChromaDB
- **Gerenciador LLM**: Integração com modelos de linguagem locais
- **Pipeline RAG**: Coordena o fluxo de indexação e consulta

## 📂 Estrutura do Projeto

```
config/              # Configurações do sistema
  ├── config.yaml    # Arquivo principal de configuração
  └── requirements.txt  # Dependências Python

data/                # Dados do sistema
  ├── cache/         # Cache de embeddings
  ├── documents/     # Documentos a serem indexados
  └── vectordb/      # Banco de dados vetorial

logs/                # Logs do sistema
  └── sistema.log    # Arquivo de log principal

src/                 # Código-fonte
  ├── processador_documentos.py  # Processamento de documentos
  ├── gerenciador_embeddings.py  # Gerenciamento de embeddings
  ├── gerenciador_llm.py         # Integração com LLMs
  ├── pipeline_rag.py            # Pipeline principal RAG
  ├── main.py                    # Interface de linha de comando
  └── web/                       # Interface web
      ├── app.py                 # Aplicação web
      ├── static/                # Arquivos estáticos
      └── templates/             # Templates HTML
```

## 📝 Desenvolvendo o Sistema

### Adicionando Novos Formatos de Documento

Para adicionar suporte a novos formatos de documentos, edite o arquivo `processador_documentos.py` e implemente um novo método para o formato desejado.

### Alterando o Modelo de Embeddings

Você pode alterar o modelo de embeddings no arquivo de configuração `config.yaml`. O sistema usa a biblioteca `sentence-transformers` para gerar embeddings.

### Integrando Outros LLMs

O sistema é projetado para trabalhar com diferentes LLMs locais. 

Por padrão, o sistema usa o Ollama com o modelo **llama3:latest**. Para baixar e usar este modelo:

```bash
# Baixar o modelo llama3
ollama pull llama3:latest
```

Você pode mudar o modelo usado alterando o parâmetro `model_name` no arquivo `llm_manager.py` ou o campo `modelo_nome` no arquivo `config.yaml`.

Para integrar outros modelos LLM, edite o arquivo `gerenciador_llm.py` ou `llm_manager.py`.

## 📄 Licença

Este projeto é licenciado sob a licença MIT - consulte o arquivo [LICENSE](LICENSE) para obter detalhes.

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir um issue ou enviar um pull request.

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Faça commit de suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Faça push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## ⭐ Agradecimentos

- [Sentence Transformers](https://github.com/UKPLab/sentence-transformers)
- [ChromaDB](https://github.com/chroma-core/chroma)
- [Ollama](https://github.com/ollama/ollama)
