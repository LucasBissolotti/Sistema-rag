# Guia de Instalação para Windows

Este documento fornece instruções específicas para instalar e executar o Sistema RAG em ambientes Windows.

## Pré-requisitos

1. **Python 3.8 ou superior**
   - Baixe e instale a partir do [site oficial do Python](https://www.python.org/downloads/windows/)
   - **IMPORTANTE:** Durante a instalação, marque a opção "Add Python to PATH"

2. **Git (opcional)**
   - Baixe e instale a partir do [site oficial do Git](https://git-scm.com/download/win)

3. **Visual C++ Redistributable (recomendado)**
   - Algumas bibliotecas podem exigir o Visual C++ Redistributable
   - Baixe a versão mais recente em [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)

## Instalação Passo-a-Passo

1. **Clone ou baixe o repositório**
   - Via Git:
     ```
     git clone https://github.com/seu-usuario/sistema-rag.git
     cd sistema-rag
     ```
   - Ou baixe o ZIP e extraia para uma pasta

2. **Crie um ambiente virtual Python**
   Abra o PowerShell ou o Prompt de Comando e navegue até a pasta do projeto:
   ```
   cd caminho\para\sistema-rag
   python -m venv venv
   ```

3. **Ative o ambiente virtual**
   ```
   .\venv\Scripts\activate
   ```
   
   Se você receber um erro sobre políticas de execução no PowerShell, execute:
   ```
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
   ```
   E então tente ativar o ambiente novamente.

4. **Instale as dependências**
   ```
   pip install -r config\requirements.txt
   ```

5. **Instale o Ollama (para LLM local)**
   - Baixe o instalador do Windows em [Ollama Releases](https://github.com/ollama/ollama/releases)
   - Execute o instalador e siga as instruções
   - Após a instalação, abra um terminal e baixe um modelo:
     ```
     ollama pull llama3:8b
     ```

## Executando o Sistema

1. **Iniciando o sistema**
   Com o ambiente virtual ativado:
   ```
   python start.py
   ```
   Escolha a opção desejada:
   - 1: Interface de linha de comando
   - 2: Interface web

2. **Linha de comando direta**
   ```
   # Para CLI
   python start.py --cli
   
   # Para web
   python start.py --web
   ```

3. **Acesso à interface web**
   - Abra seu navegador e acesse: http://localhost:5000

## Solução de Problemas

### Erro de importação de módulos
Se você receber erros de importação de módulos, verifique:
- Se o ambiente virtual está ativado
- Se todas as dependências foram instaladas corretamente

### Erro ao carregar modelos de embedding
Os modelos de embedding são baixados na primeira execução. Verifique:
- Se você tem conexão com a internet
- Se há espaço suficiente em disco
- Se o caminho do diretório não contém caracteres especiais

### Ollama não responde
- Verifique se o serviço Ollama está em execução
- Reinicie o serviço do Ollama se necessário
- Verifique logs em: `C:\Users\SEU_USUARIO\AppData\Local\ollama`

## Atualização

Para atualizar o sistema:
1. Faça backup dos seus documentos em `data/documents`
2. Baixe a versão mais recente
3. Reinstale as dependências se necessário:
   ```
   pip install -r config\requirements.txt
   ```

## Desinstalação

1. Desative o ambiente virtual:
   ```
   deactivate
   ```

2. Exclua a pasta do projeto
3. Desinstale o Ollama pelo Painel de Controle se não for mais necessário
