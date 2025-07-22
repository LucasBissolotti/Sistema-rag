#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema RAG - Interface Web
"""

import os
import sys
import time
import logging
from flask import Flask, render_template, request, jsonify
import threading
from pathlib import Path

# Adiciona o diretório pai ao sys.path para permitir importações do pacote
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline_rag import RAGPipeline

app = Flask(__name__)

# Configuração de logs
log_dir = Path(__file__).resolve().parent.parent.parent / 'logs'
log_dir.mkdir(exist_ok=True)  # Cria o diretório de logs se não existir

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'web_app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Status compartilhado
indexing_status = {
    "running": False,
    "progress": 0,
    "total": 0,
    "status": "idle",
    "message": "",
    "logs": []
}

# Inicializa o pipeline
pipeline = None
try:
    pipeline = RAGPipeline()
    logger.info("Pipeline inicializado com sucesso")
except Exception as e:
    logger.error(f"Erro ao inicializar pipeline: {e}")

@app.route('/')
def index():
    """Página inicial"""
    return render_template('index.html')

@app.route('/api/status')
def status():
    """Status do sistema"""
    if not pipeline:
        return jsonify({"error": "Pipeline não inicializado"}), 500

    try:
        db_stats = pipeline.vector_store.get_collection_stats()
        return jsonify({
            "status": "ok",
            "db_stats": db_stats,
            "indexing": indexing_status
        })
    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/query', methods=['POST'])
@app.route('/consulta', methods=['POST'])  # Endpoint adicional para compatibilidade
def query():
    """Processa consulta do usuário"""
    if not pipeline:
        return jsonify({"error": "Pipeline não inicializado"}), 500

    try:
        data = request.json
        
        # Compatibilidade com ambos formatos de requisição
        question = data.get('question', '')
        if not question:
            question = data.get('pergunta', '')
        
        question = question.strip()
        
        if not question:
            logger.warning("Requisição recebida com pergunta vazia")
            return jsonify({"error": "Pergunta vazia"}), 400
        
        logger.info(f"Processando consulta: {question}")
        
        # Abordagem direta - apenas defina um timeout maior para o Flask
        # (o timeout padrão é 1 minuto no Werkzeug/Flask)
        start_time = time.time()
        
        try:
            # Gera a resposta diretamente
            result = pipeline.generate_answer(question)
            processing_time = time.time() - start_time
            logger.info(f"Resposta gerada com sucesso em {processing_time:.2f} segundos")
            
            # Formato compatível com ambas versões do frontend
            return jsonify({
                "answer": result.get("answer", "Erro ao processar consulta"),
                "sources": result.get("sources", []),
                "resposta": result.get("answer", "Erro ao processar consulta"),
                "fontes": result.get("sources", []),
                "processing_time": f"{processing_time:.2f} segundos"
            })
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            return jsonify({
                "error": f"Erro ao processar consulta: {str(e)}",
                "resposta": f"Ocorreu um erro ao processar sua pergunta: {str(e)}",
                "fontes": []
            }), 500
            
    except Exception as e:
        logger.error(f"Erro ao processar requisição: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Erro ao processar consulta: {e}")
        return jsonify({"error": str(e)}), 500

def index_worker(status_dict):
    """Função para indexar documentos em segundo plano"""
    global pipeline
    if not pipeline:
        status_dict["status"] = "error"
        status_dict["message"] = "Pipeline não inicializado"
        status_dict["running"] = False
        return
    
    try:
        status_dict["running"] = True
        status_dict["status"] = "running"
        status_dict["message"] = "Iniciando indexação..."
        status_dict["logs"] = ["Iniciando processo de indexação..."]
        
        # Chama o método de indexação com progresso
        result = pipeline.index_documents_with_progress(status_dict)
        
        if "error" in result:
            status_dict["status"] = "error"
            status_dict["message"] = f"Erro: {result['error']}"
        else:
            status_dict["status"] = "completed"
            status_dict["message"] = "Indexação concluída com sucesso"
            status_dict["logs"].append(f"Total de documentos indexados: {result['total_documents']}")
            status_dict["logs"].append(f"Total de chunks gerados: {result['chunks']}")
            status_dict["logs"].append(f"Total de embeddings: {result['embeddings_generated']}")
    
    except Exception as e:
        logger.error(f"Erro no processo de indexação: {e}")
        status_dict["status"] = "error"
        status_dict["message"] = f"Erro: {str(e)}"
        status_dict["logs"].append(f"ERRO: {str(e)}")
    finally:
        status_dict["running"] = False

@app.route('/api/index', methods=['POST'])
def index_documents():
    """Inicia processo de indexação em segundo plano"""
    global indexing_status
    
    if indexing_status["running"]:
        return jsonify({"error": "Indexação já em andamento"}), 400
    
    # Reset do status
    indexing_status = {
        "running": False,
        "progress": 0,
        "total": 0,
        "status": "starting",
        "message": "Preparando indexação...",
        "logs": []
    }
    
    # Inicia thread para indexação
    thread = threading.Thread(
        target=index_worker,
        args=(indexing_status,),
        daemon=True
    )
    thread.start()
    
    return jsonify({"status": "started", "message": "Indexação iniciada"})

@app.route('/api/docs')
def list_documents():
    """Lista documentos disponíveis (endpoint API)"""
    # Usa um caminho relativo baseado no arquivo atual
    docs_path = Path(__file__).resolve().parent.parent.parent / "data" / "documents"
    
    try:
        if not docs_path.exists():
            return jsonify({"documents": [], "error": "Pasta não encontrada"}), 404
        
        docs = []
        for ext in [".pdf", ".docx", ".txt"]:
            for file_path in docs_path.glob(f"**/*{ext}"):
                docs.append({
                    "name": file_path.name,
                    "path": str(file_path.relative_to(docs_path)),
                    "type": ext[1:],  # Remove o ponto do início
                    "size_kb": round(file_path.stat().st_size / 1024, 1)
                })
        return jsonify({"documents": docs})
    except Exception as e:
        logger.error(f"Erro ao listar documentos: {e}")
        return jsonify({"error": str(e)}), 500
                
@app.route('/documentos')
def get_documents():
    """Lista documentos disponíveis (endpoint para interface web)"""
    docs_path = Path(__file__).resolve().parent.parent.parent / "data" / "documents"
    
    try:
        if not docs_path.exists():
            return jsonify([])
        
        docs = []
        for ext in [".pdf", ".docx", ".txt"]:
            for file_path in docs_path.glob(f"**/*{ext}"):
                docs.append(file_path.name)
                
        return jsonify(docs)
    except Exception as e:
        logger.error(f"Erro ao listar documentos: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/documentos/<filename>', methods=['DELETE'])
def delete_document(filename):
    """Remove um documento"""
    docs_path = Path(__file__).resolve().parent.parent.parent / "data" / "documents"
    
    try:
        # Sanitiza o nome do arquivo para evitar path traversal
        safe_filename = Path(filename).name
        file_path = docs_path / safe_filename
        
        if not file_path.exists():
            return jsonify({"error": "Arquivo não encontrado"}), 404
            
        # Remove o arquivo
        file_path.unlink()
        logger.info(f"Arquivo removido: {file_path}")
        
        return jsonify({
            "success": True,
            "message": f"Arquivo {safe_filename} removido com sucesso"
        })
    except Exception as e:
        logger.error(f"Erro ao remover documento: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/documentos', methods=['POST'])
def upload_document():
    """Upload de documentos"""
    try:
        # Verifica se há arquivo na requisição
        if 'file' not in request.files:
            return jsonify({"error": "Nenhum arquivo enviado"}), 400
            
        file = request.files['file']
        
        # Verifica se o arquivo tem nome
        if file.filename == '':
            return jsonify({"error": "Nenhum arquivo selecionado"}), 400
            
        # Verifica extensão do arquivo
        allowed_extensions = ['.pdf', '.docx', '.txt']
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            return jsonify({
                "error": f"Formato não suportado: {file_ext}. Use: {', '.join(allowed_extensions)}"
            }), 400
            
        # Define o caminho para salvar o arquivo
        docs_path = Path(__file__).resolve().parent.parent.parent / "data" / "documents"
        docs_path.mkdir(exist_ok=True)
        
        # Garante nome de arquivo único para evitar sobrescrever arquivos
        filename = Path(file.filename).stem
        filepath = docs_path / f"{filename}{file_ext}"
        
        # Se o arquivo já existir, adiciona um número ao nome
        counter = 1
        while filepath.exists():
            filepath = docs_path / f"{filename}_{counter}{file_ext}"
            counter += 1
        
        # Salva o arquivo
        file.save(filepath)
        logger.info(f"Arquivo salvo: {filepath}")
        
        return jsonify({
            "success": True,
            "message": f"Arquivo {filepath.name} enviado com sucesso",
            "filename": filepath.name
        })
        
    except Exception as e:
        logger.error(f"Erro ao fazer upload: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
