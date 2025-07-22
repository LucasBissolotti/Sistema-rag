#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para iniciar a interface web do Sistema RAG
"""

import os
import sys
from pathlib import Path

# Ajusta o caminho Python para incluir o diretório raiz do projeto
project_root = Path(__file__).resolve().parent
src_dir = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_dir))

# Verifica e cria diretórios necessários
os.makedirs(project_root / "data" / "documents", exist_ok=True)
os.makedirs(project_root / "data" / "cache", exist_ok=True)
os.makedirs(project_root / "data" / "vectordb", exist_ok=True)
os.makedirs(project_root / "logs", exist_ok=True)

# Importa e executa a aplicação web
if __name__ == "__main__":
    from src.web.app import app
    port = int(os.environ.get("PORT", 5000))
    
    print("=" * 50)
    print("🌐 Sistema RAG - Interface Web")
    print("=" * 50)
    print(f"📁 Documentos: {project_root / 'data' / 'documents'}")
    print(f"🔗 URL: http://localhost:{port}")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=port)
