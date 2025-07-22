import os
import PyPDF2
from docx import Document
from typing import List, Dict
from pathlib import Path
import logging
import re

class DocumentProcessor:
    """
    Classe para processar documentos da pasta local
    Suporta: PDF, DOCX, TXT
    """

    def __init__(self, documents_path: str):
        self.documents_path = Path(documents_path)
        self.supported_formats = ['.pdf', '.docx', '.txt']
        self.logger = logging.getLogger(__name__)

    def extract_text_from_pdf(self, file_path: Path) -> str:
        """Extrai texto de arquivo PDF"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            self.logger.error(f"Erro ao processar PDF {file_path}: {str(e)}")
            return ""

    def extract_text_from_pdf_chunked(self, file_path: Path, chunk_size: int = 2000) -> str:
        """Extrai texto de arquivo PDF em partes"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                for i in range(0, total_pages, chunk_size):
                    chunk_text = ""
                    for j in range(i, min(i + chunk_size, total_pages)):
                        page = pdf_reader.pages[j]
                        chunk_text += page.extract_text() + "\n"
                    text += chunk_text
            return text.strip()
        except Exception as e:
            self.logger.error(f"Erro ao processar PDF {file_path}: {str(e)}")
            return ""

    def extract_text_from_docx(self, file_path: Path) -> str:
        """Extrai texto de arquivo DOCX"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            self.logger.error(f"Erro ao processar DOCX {file_path}: {str(e)}")
            return ""

    def extract_text_from_txt(self, file_path: Path) -> str:
        """Extrai texto de arquivo TXT"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            self.logger.error(f"Erro ao processar TXT {file_path}: {str(e)}")
            return ""

    def process_document(self, file_path: Path) -> Dict[str, str]:
        """Processa um documento e retorna texto e metadados"""
        file_extension = file_path.suffix.lower()

        if file_extension == '.pdf':
            text = self.extract_text_from_pdf(file_path)
        elif file_extension == '.docx':
            text = self.extract_text_from_docx(file_path)
        elif file_extension == '.txt':
            text = self.extract_text_from_txt(file_path)
        else:
            self.logger.warning(f"Formato não suportado: {file_extension}")
            return None

        return {
            'filename': file_path.name,
            'filepath': str(file_path),
            'text': text,
            'size': len(text),
            'format': file_extension[1:].upper()
        }

    def scan_documents_folder(self) -> List[Dict[str, str]]:
        """Escaneia a pasta de documentos e processa todos os arquivos"""
        documents = []

        if not self.documents_path.exists():
            self.logger.error(f"Pasta não encontrada: {self.documents_path}")
            return documents

        for file_path in self.documents_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                doc_data = self.process_document(file_path)
                if doc_data and doc_data['text']:
                    documents.append(doc_data)
                    self.logger.info(f"Documento processado: {file_path.name}")

        return documents

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Divide o texto em chunks, ajustando de acordo com o tamanho do conteúdo extraído"""
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        sentences = re.split(r'(?<=[.!?]) +', text)
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "

        if current_chunk:
            chunks.append(current_chunk.strip())

        if overlap > 0:
            chunks = self.apply_overlap(chunks, overlap)

        return chunks

    def apply_overlap(self, chunks: List[str], overlap: int) -> List[str]:
        """Aplica a sobreposição entre chunks"""
        if overlap <= 0:
            return chunks

        overlapping_chunks = []
        for i in range(len(chunks) - 1):
            overlapping_chunks.append(chunks[i])
            overlap_chunk = chunks[i] + " " + chunks[i + 1][:overlap]
            overlapping_chunks.append(overlap_chunk)

        overlapping_chunks.append(chunks[-1])
        return overlapping_chunks
