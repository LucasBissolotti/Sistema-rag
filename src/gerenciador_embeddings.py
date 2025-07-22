from sentence_transformers import SentenceTransformer
import chromadb
from typing import List, Dict, Optional
import uuid
import logging
import torch

class EmbeddingManager:
	"""
	Gerencia embeddings usando sentence-transformers
	Modelo otimizado para português: all-MiniLM-L6-v2
	"""

	def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
		self.model_name = model_name
		self.model = None
		self.logger = logging.getLogger(__name__)
		self._load_model()

	def _load_model(self):
		"""Carrega o modelo de embeddings, utilizando GPU se disponível"""
		try:
			# Especificando o uso de GPU, caso ela esteja disponível
			self.model = SentenceTransformer(self.model_name, device='cuda' if torch.cuda.is_available() else 'cpu')
			self.logger.info(f"Modelo carregado: {self.model_name}")
		except Exception as e:
			self.logger.error(f"Erro ao carregar modelo: {str(e)}")
			raise

	def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
		"""Gera embeddings para uma lista de textos"""
		if not self.model:
			raise ValueError("Modelo não carregado")

		try:
			embeddings = self.model.encode(texts, show_progress_bar=True)
			return embeddings.tolist()
		except Exception as e:
			self.logger.error(f"Erro ao gerar embeddings: {str(e)}")
			return []

	# ...existing code...
class ChromaVectorStore:
	"""
	Gerencia o armazenamento vetorial usando ChromaDB
	"""

	def __init__(
		self,
		collection_name: str = "rag_documents",
		persist_directory: str = "./data/chromadb"
	):
		self.collection_name = collection_name
		self.persist_directory = persist_directory
		self.client = None
		self.collection = None
		self.logger = logging.getLogger(__name__)
		self._initialize_client()

	def reset_collection(self):
		"""Reseta a coleção, deletando todos os documentos"""
		try:
			# Tenta deletar a coleção existente
			self.client.delete_collection(name=self.collection_name)
			self.logger.info(f"Coleção '{self.collection_name}' deletada")
		except Exception as e:
			# Se a coleção não existir, continua normalmente
			self.logger.warning(f"Coleção pode não existir: {str(e)}")
		
		try:
			# Reinicializa a coleção
			self._initialize_client()
			self.logger.info("Coleção recriada com sucesso")
		except Exception as e:
			self.logger.error(f"Falha ao recriar coleção: {str(e)}")
			raise

	def _initialize_client(self):
		"""Inicializa o cliente ChromaDB"""
		try:
			self.client = chromadb.PersistentClient(path=self.persist_directory)
			self.collection = self.client.get_or_create_collection(
				name=self.collection_name,
				metadata={"hnsw:space": "cosine"}
			)
			self.logger.info(f"ChromaDB inicializado: {self.collection_name}")
		except Exception as e:
			self.logger.error(f"Erro ao inicializar ChromaDB: {str(e)}")
			raise

	def add_documents(self, documents: List[Dict[str, str]], embeddings: List[List[float]]):
		"""Adiciona documentos e embeddings ao ChromaDB em lotes menores"""
		try:
			# Prepara os dados para inserção
			batch_size = 100  # Ajuste o tamanho do lote para 100 (ou o valor máximo suportado)

			ids = [str(uuid.uuid4()) for _ in documents]
			texts = [doc['text'] for doc in documents]
			metadatas = [
				{
					'filename': doc['filename'],
					'filepath': doc['filepath'],
					'format': doc['format'],
					'size': doc['size']
				}
				for doc in documents
			]

			self.logger.info(f"Adicionando {len(documents)} documentos ao ChromaDB: {[doc['filename'] for doc in documents]}")

			# Adiciona os documentos em lotes
			for i in range(0, len(documents), batch_size):
				batch_ids = ids[i:i + batch_size]
				batch_texts = texts[i:i + batch_size]
				batch_metadatas = metadatas[i:i + batch_size]
				batch_embeddings = embeddings[i:i + batch_size]

				# Adiciona o lote ao ChromaDB
				self.collection.add(
					ids=batch_ids,
					embeddings=batch_embeddings,
					documents=batch_texts,
					metadatas=batch_metadatas
				)

				self.logger.info(f"Adicionados {len(batch_ids)} documentos ao ChromaDB")

			return ids

		except Exception as e:
			self.logger.error(f"Erro ao adicionar documentos: {str(e)}")
			return []

	def search_similar(self, query_embedding: List[float], n_results: int = 5) -> Dict:
		"""Busca documentos similares baseado no embedding da query"""
		try:
			results = self.collection.query(
				query_embeddings=[query_embedding],
				n_results=n_results
			)
			
			self.logger.info(f"Documentos encontrados: {len(results.get('documents', []))}")

			# Aqui, estamos pegando os 'documents' retornados pela consulta, que devem ser múltiplos
			if 'documents' in results and len(results['documents'][0]) > 0:
				self.logger.info(f"Documentos encontrados: {len(results['documents'])}")
				return results
			else:
				self.logger.warning("Nenhum documento encontrado na busca.")
				return {}
		except Exception as e:
			self.logger.error(f"Erro na busca: {str(e)}")
			return {}

	def get_collection_stats(self) -> Dict[str, int]:
		"""Obtém estatísticas da coleção"""
		try:
			stats = self.collection.count()
			return {"total_documents": stats}
		except Exception as e:
			self.logger.error(f"Erro ao obter estatísticas da coleção: {str(e)}")
			return {}
