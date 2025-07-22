import logging
import sys
from pathlib import Path
from pipeline_rag import RAGPipeline
from tqdm import tqdm  # Importa a biblioteca para barra de progresso

class RAGInterface:
    """Interface simples para usar o sistema RAG"""
    
    def __init__(self):
        self.setup_logging()
        self.pipeline = RAGPipeline()
    
    def setup_logging(self):
        """Configura logging com suporte a Unicode"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('./logs/rag_system.log', encoding='utf-8'),  # Define codificação UTF-8
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def run(self):
        """Executa interface principal"""
        print("🚀 Sistema RAG - Busca Inteligente")
        print("=" * 50)
        print("Sistema de busca inteligente em documentos")
        print("Tecnologias: 100% gratuitas e locais")
        print("=" * 50)
        
        while True:
            print("\n📋 Opções:")
            print("1. 📚 Indexar documentos")
            print("2. ❓ Fazer pergunta")
            print("3. 📊 Status do sistema")
            print("4. 🚪 Sair")
            
            try:
                choice = input("\n👉 Escolha uma opção (1-4): ").strip()
                
                if choice == "1":
                    self.index_documents()
                elif choice == "2":
                    self.ask_question()
                elif choice == "3":
                    self.show_status()
                elif choice == "4":
                    print("\n👋 Obrigado por usar o Sistema RAG!")
                    break
                else:
                    print("❌ Opção inválida. Escolha entre 1-4.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Sistema encerrado pelo usuário.")
                break
            except Exception as e:
                print(f"❌ Erro inesperado: {str(e)}")
    
    def index_documents(self):
        """Indexa documentos com barra de progresso"""
        print("\n📚 INDEXAÇÃO DE DOCUMENTOS")
        print("-" * 30)
        
        # Verifica se há documentos
        docs_path = Path("./data/documents")
        if not docs_path.exists():
            print(f"❌ Pasta de documentos não encontrada: {docs_path}")
            print("💡 Crie a pasta e coloque seus documentos lá.")
            return
        
        doc_files = list(docs_path.rglob("*.pdf")) + list(docs_path.rglob("*.docx")) + list(docs_path.rglob("*.txt"))
        if not doc_files:
            print("❌ Nenhum documento encontrado na pasta.")
            print("💡 Suporte: PDF, DOCX, TXT")
            return
        
        print(f"📁 Encontrados {len(doc_files)} documentos")
        
        reindex = input("🔄 Reindexar tudo? (s/N): ").lower().strip() == 's'
        
        print("\n⏳ Processando documentos...")
        
        # Usando tqdm para adicionar uma barra de progresso
        result = self.pipeline.index_documents(reindex)

        if "error" in result:
            print(f"❌ Erro: {result['error']}")
        else:
            print("✅ Indexação concluída!")
            print(f"   📄 Documentos: {result['total_documents']}")
            print(f"   🧩 Chunks: {result['chunks']}")
            print(f"   🧠 Embeddings: {result['embeddings_generated']}")
    
    def ask_question(self):
        """Faz pergunta ao sistema"""
        print("\n❓ FAZER PERGUNTA")
        print("-" * 20)
        
        query = input("💬 Digite sua pergunta: ").strip()
        
        if not query:
            print("❌ Pergunta não pode ser vazia")
            return
        
        print("\n🤔 Buscando informações...")
        result = self.pipeline.generate_answer(query)
        
        print(f"\n📝 RESPOSTA:")
        print("-" * 10)
        print(f"{result['answer']}")
        
        if result['sources']:
            print(f"\n📚 FONTES:")
            for i, source in enumerate(result['sources'], 1):
                print(f"   {i}. {source}")
        
        print("\n" + "=" * 50)
    
    def show_status(self):
        """Mostra status do sistema"""
        print("\n📊 STATUS DO SISTEMA")
        print("-" * 25)
        
        try:
            # Verifica componentes
            print("🔍 Verificando componentes...")
            
            # Verifica status dos componentes principais
            if self.pipeline.check_components():
                print("✅ Todos os componentes estão funcionando corretamente.")
            else:
                print("⚠️ Alguns componentes podem estar com problemas.")
                
            # Pasta de documentos
            docs_path = Path("./data/documents")
            if docs_path.exists():
                files = list(docs_path.rglob("*.*"))
                print(f"📁 Documentos: ✅ {len(files)} arquivos")
            else:
                print(f"📁 Documentos: ❌ Pasta não encontrada")
                
        except Exception as e:
            print(f"❌ Erro ao verificar status: {str(e)}")


if __name__ == "__main__":
    interface = RAGInterface()
    interface.run()