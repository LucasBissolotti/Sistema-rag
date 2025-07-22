#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de inicialização rápida para o Sistema RAG
Este script ajuda a iniciar o sistema com facilidade
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def check_environment():
    """Verifica se o ambiente está configurado corretamente"""
    # Verifica se estamos em um ambiente virtual
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if not in_venv:
        print("\n⚠️ AVISO: Você não está em um ambiente virtual Python.")
        print("É recomendável criar e ativar um ambiente virtual antes de executar este script.")
        print("Veja o README.md para instruções.\n")
    
    # Verifica se as dependências estão instaladas
    try:
        import yaml
        import flask
        import transformers
        import chromadb
    except ImportError as e:
        print(f"\n❌ ERRO: Dependência não encontrada: {e}")
        print("Execute 'pip install -r config/requirements.txt' para instalar as dependências necessárias.")
        return False
    
    # Verifica se o Ollama está instalado (opcional)
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print("✅ Ollama detectado e funcionando.")
        else:
            print("⚠️ Ollama pode não estar funcionando corretamente.")
    except:
        print("\n⚠️ AVISO: Ollama não detectado ou não está em execução.")
        print("O Ollama é necessário para o funcionamento do LLM local.")
        print("Visite https://github.com/ollama/ollama para instruções de instalação.")
    
    # Verifica pastas necessárias
    data_dir = Path("data")
    if not data_dir.exists():
        print("\n⚠️ AVISO: Pasta 'data' não encontrada. Criando estrutura de diretórios...")
        os.makedirs("data/documents", exist_ok=True)
        os.makedirs("data/cache", exist_ok=True)
        os.makedirs("data/vectordb", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
    
    return True

def start_cli():
    """Inicia a interface de linha de comando"""
    print("🚀 Iniciando interface de linha de comando...")
    try:
        subprocess.run([sys.executable, "src/main.py"])
    except KeyboardInterrupt:
        print("\n👋 Sistema encerrado pelo usuário.")
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")

def start_web():
    """Inicia a interface web"""
    print("🌐 Iniciando servidor web...")
    try:
        subprocess.run([sys.executable, "src/web/app.py"])
    except KeyboardInterrupt:
        print("\n👋 Servidor web encerrado pelo usuário.")
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sistema RAG - Busca Inteligente em Documentos")
    parser.add_argument("--web", action="store_true", help="Iniciar interface web")
    parser.add_argument("--cli", action="store_true", help="Iniciar interface de linha de comando")
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("🔍 Sistema RAG - Busca Inteligente em Documentos")
    print("=" * 50)
    
    if check_environment():
        if args.web:
            start_web()
        elif args.cli:
            start_cli()
        else:
            # Se nenhum argumento for fornecido, pergunta ao usuário
            print("\n🔧 Escolha a interface:")
            print("1. Interface de linha de comando (CLI)")
            print("2. Interface web")
            choice = input("\nEscolha uma opção (1-2): ").strip()
            
            if choice == "1":
                start_cli()
            elif choice == "2":
                start_web()
            else:
                print("❌ Opção inválida.")
