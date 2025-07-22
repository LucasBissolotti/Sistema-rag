import logging
import os
import json
import hashlib
from typing import List, Dict, Optional
from processador_documentos import DocumentProcessor
from gerenciador_embeddings import EmbeddingManager, ChromaVectorStore
from llm_manager import OllamaLLMManager

class RAGPipeline:
	"""
	Pipeline principal do sistema RAG
	"""

	def __init__(
		self,
		documents_path: str = "./data/documents",
		embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
		llm_model: str = "llama3:latest",
		collection_name: str = "rag_documents",
		cache_path: str = "./data/cache"
	):
		self.logger = logging.getLogger(__name__)
		self.cache_path = cache_path

		# Criar diretório de cache se não existir
		os.makedirs(self.cache_path, exist_ok=True)

		# Inicializa os componentes
		self.document_processor = DocumentProcessor(documents_path)
		self.embedding_manager = EmbeddingManager(embedding_model)
		self.vector_store = ChromaVectorStore(collection_name)
		self.llm_manager = OllamaLLMManager(model_name=llm_model)

		self.logger.info("Pipeline RAG inicializado com sucesso")

	def check_components(self):
		"""Verifica o status dos principais componentes"""
		try:
			# Verifica o status do banco de dados
			db_stats = self.vector_store.get_collection_stats()
			if db_stats:
				self.logger.info(f"Base de dados: ✅ Ativa")
				self.logger.info(f"   📄 Documentos indexados: {db_stats.get('total_documents', 0)}")
			else:
				self.logger.warning(f"Base de dados: ❌ Não encontrada ou erro na conexão")

			# Verifica o status do Ollama
			ollama_status = self.llm_manager._check_ollama_status()
			if ollama_status:
				self.logger.info(f"🤖 Ollama: ✅ Rodando")
				self.logger.info(f"   🧠 Modelo: {self.llm_manager.model_name}")
			else:
				self.logger.warning(f"🤖 Ollama: ❌ Não está rodando")

			# Verifica o status do modelo de embeddings
			if self.embedding_manager.model:
				self.logger.info(f"🔤 Embeddings: ✅ Carregado")
				self.logger.info(f"   📐 Modelo: {self.embedding_manager.model_name}")
			else:
				self.logger.warning(f"🔤 Embeddings: ❌ Não carregado")

			return True
		except Exception as e:
			self.logger.error(f"Erro ao verificar componentes: {str(e)}")
			return False

	def index_documents(self, reindex: bool = False) -> Dict[str, int]:
		"""Indexa todos os documentos da pasta"""
		try:
			if reindex:
				self.vector_store.reset_collection()
				self.logger.info("Coleção reindexada com sucesso")
			else:
				# Filtra apenas documentos que ainda não estão indexados
				docs = self.document_processor.scan_documents_folder()
				indexed = self.vector_store.list_indexed_filenames()
				docs = [doc for doc in docs if doc['filename'] not in indexed]

			# Verifica se há documentos novos
			self.logger.info("Iniciando processamento de documentos...")
			documents = self.document_processor.scan_documents_folder()

			if not documents:
				return {"total_documents": 0, "chunks": 0}

			# Divide documentos em chunks
			all_chunks = []
			for doc in documents:
				chunks = self.document_processor.chunk_text(doc['text'])
				for i, chunk in enumerate(chunks):
					chunk_doc = doc.copy()
					chunk_doc['text'] = chunk
					chunk_doc['chunk_id'] = i
					all_chunks.append(chunk_doc)

			# Gera embeddings
			texts = [chunk['text'] for chunk in all_chunks]
			embeddings = self.embedding_manager.generate_embeddings(texts)

			# Adiciona ao ChromaDB
			ids = self.vector_store.add_documents(all_chunks, embeddings)

			return {
				"total_documents": len(documents),
				"chunks": len(all_chunks),
				"embeddings_generated": len(embeddings)
			}

		except Exception as e:
			self.logger.error(f"Erro na indexação: {str(e)}")
			return {"error": str(e)}

	def index_documents_with_progress(self, status_dict):
		try:
			logs = []
			self.vector_store.reset_collection()
			logs.append("Coleção resetada.")
			documents = self.document_processor.scan_documents_folder()
			logs.append(f"Documentos encontrados: {len(documents)}")
			status_dict["total"] = len(documents)
			status_dict["progress"] = 0

			if not documents:
				status_dict["message"] = "Nenhum documento encontrado."
				status_dict["logs"] = logs
				return {"total_documents": 0, "chunks": 0}

			all_chunks = []
			for idx, doc in enumerate(documents):
				chunks = self.document_processor.chunk_text(doc['text'])
				for i, chunk in enumerate(chunks):
					chunk_doc = doc.copy()
					chunk_doc['text'] = chunk
					chunk_doc['chunk_id'] = i
					all_chunks.append(chunk_doc)
				status_dict["progress"] = idx + 1
				status_dict["message"] = f"Processando documento {idx+1}/{len(documents)}: {doc['filename']}"
				logs.append(f"Documento {doc['filename']} gerou {len(chunks)} chunks.")

			# Filtra chunks vazios
			all_chunks = [chunk for chunk in all_chunks if chunk['text'].strip()]
			logs.append(f"Total de chunks após filtro: {len(all_chunks)}")

			texts = [chunk['text'] for chunk in all_chunks]
			logs.append(f"Gerando embeddings para {len(texts)} chunks...")
			embeddings = self.embedding_manager.generate_embeddings(texts)
			logs.append(f"Embeddings gerados: {len(embeddings)}")

			# Verifica se o número de embeddings corresponde ao de chunks
			if len(embeddings) != len(all_chunks):
				logs.append(f"ERRO: Número de embeddings ({len(embeddings)}) diferente do número de chunks ({len(all_chunks)})!")

			self.vector_store.add_documents(all_chunks, embeddings)
			logs.append("Chunks e embeddings enviados ao ChromaDB.")

			stats = self.vector_store.get_collection_stats()
			logs.append(f"Documentos na coleção após indexação: {stats}")

			status_dict["logs"] = logs
			return {
				"total_documents": len(documents),
				"chunks": len(all_chunks),
				"embeddings_generated": len(embeddings),
				"collection_stats": stats,
				"logs": logs
			}
		except Exception as e:
			status_dict["status"] = "error"
			status_dict["message"] = str(e)
			status_dict["logs"] = status_dict.get("logs", []) + [f"ERRO: {str(e)}"]
			return {"error": str(e)}

	def _get_cache_key(self, query: str) -> str:
		"""Gera uma chave única para cada consulta"""
		return hashlib.md5(query.encode('utf-8')).hexdigest()

	def _load_cache(self, cache_key: str) -> Optional[Dict[str, str]]:
		"""Carrega o cache, se existir"""
		cache_file = os.path.join(self.cache_path, f"{cache_key}.json")
		if os.path.exists(cache_file):
			with open(cache_file, 'r', encoding='utf-8') as f:
				return json.load(f)
		return None

	def _save_cache(self, cache_key: str, result: Dict[str, str]):
		"""Salva a resposta no cache"""
		cache_file = os.path.join(self.cache_path, f"{cache_key}.json")
		with open(cache_file, 'w', encoding='utf-8') as f:
			json.dump(result, f, ensure_ascii=False, indent=4)
			
	def _find_similar_cached_query(self, query: str) -> Optional[str]:
		"""Tenta encontrar uma consulta similar no cache"""
		try:
			# Verificar apenas se já existe algum arquivo de cache
			if not os.path.exists(self.cache_path):
				return None
				
			# Lista todos os arquivos de cache
			cache_files = [f for f in os.listdir(self.cache_path) if f.endswith('.json')]
			if not cache_files:
				return None
				
			# Carrega as consultas anteriores
			previous_queries = []
			for cache_file in cache_files[:30]:  # Limita a 30 arquivos para não sobrecarregar
				try:
					with open(os.path.join(self.cache_path, cache_file), 'r', encoding='utf-8') as f:
						data = json.load(f)
						if "query" in data:
							previous_queries.append(data["query"])
				except:
					continue
					
			if not previous_queries:
				return None
				
			# Verifica similaridade com consultas anteriores (implementação simples)
			words = set(query.split())
			best_match = None
			best_score = 0.6  # Limiar mínimo de similaridade (60%)
			
			for prev_query in previous_queries:
				prev_words = set(prev_query.split())
				
				# Calcula o coeficiente de Jaccard
				intersection = len(words.intersection(prev_words))
				union = len(words.union(prev_words))
				
				if union == 0:  # Evitar divisão por zero
					continue
					
				similarity = intersection / union
				
				if similarity > best_score:
					best_score = similarity
					best_match = prev_query
					
			return best_match
		except Exception as e:
			self.logger.error(f"Erro ao buscar consultas similares: {e}")
			return None

	def generate_answer(self, query: str) -> Dict[str, str]:
		"""Gera resposta usando RAG, com cache de consulta"""
		# Normaliza a consulta para melhorar as chances de cache hit
		query = query.lower().strip()
		cache_key = self._get_cache_key(query)
		
		# Verifica se a resposta já está no cache
		cached_result = self._load_cache(cache_key)
		if cached_result:
			self.logger.info("Resposta obtida do cache")
			return cached_result
		
		# Tenta encontrar consultas similares no cache
		similar_query = self._find_similar_cached_query(query)
		if similar_query:
			self.logger.info(f"Encontrada consulta similar no cache: '{similar_query}'")
			cached_key = self._get_cache_key(similar_query)
			cached_result = self._load_cache(cached_key)
			if cached_result:
				return cached_result

		# Caso não esteja no cache, gera a resposta
		try:
			# Gera embedding da query
			query_embedding = self.embedding_manager.generate_embeddings([query])[0]

			# Busca documentos similares
			results = self.vector_store.search_similar(query_embedding, 5)

			if not results or not results.get('documents'):
				result = {
					"query": query,
					"answer": "Não encontrei informações relevantes nos documentos.",
					"sources": []
				}
			else:
				# Monta contexto
				context_parts = []
				sources = []

				for i, doc in enumerate(results['documents'][0]):
					context_parts.append(doc)
					if results.get('metadatas') and results['metadatas'][0][i]:
						filename = results['metadatas'][0][i].get('filename', 'Desconhecido')
						if filename not in sources:
							sources.append(filename)

				context = "\n\n".join(context_parts)  # Limita contexto

				# Gera resposta
				answer = self.llm_manager.generate_response(query, context)
				# Tratamento extra: se a resposta for muito curta ou genérica, adicione uma mensagem
				if not answer or len(answer.strip()) < 20:
					answer = "Não foi possível gerar uma resposta detalhada com base nos documentos indexados."
				# Opcional: formate para HTML se desejar
				answer = answer.replace('\n', '<br>')
				result = {
					"query": query,
					"answer": answer,
					"sources": sources
				}

			# Salva no cache
			self._save_cache(cache_key, result)
			return result

		except Exception as e:
			return {
				"query": query,
				"answer": f"Erro ao gerar resposta: {str(e)}",
				"sources": []
			}
