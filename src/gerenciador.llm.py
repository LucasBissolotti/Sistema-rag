import time
import requests
import json
import logging
from typing import Dict, List, Optional

class OllamaLLMManager:
    """
    Gerencia interações com modelos LLM locais usando Ollama.
    Suporta modelos como Llama 3.1, Mistral, etc.
    """
    
    def __init__(self, 
                 base_url: str = "http://localhost:11434",
                 model_name: str = "llama3.1:8b"):
        self.base_url = base_url
        self.model_name = model_name
        self.logger = logging.getLogger(__name__)
        self._check_ollama_status()

    def _check_ollama_status(self) -> bool:
        """Verifica se o Ollama está rodando"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                self.logger.info("Ollama está rodando")
                return True
        except Exception as e:
            self.logger.error(f"Ollama não está rodando: {str(e)}")
            return False

    def generate_response(self, 
                         prompt: str, 
                         context: str = "",
                         max_tokens: int = 2048,  # aumente o limite se necessário
                         temperature: float = 0.1,
                         retries: int = 3,
                         backoff_factor: float = 1.5) -> str:
        """
        Gera resposta usando o modelo local com Retry em caso de falhas
        """
        # Limita o tamanho do contexto para evitar envio de dados excessivos
        context = context[:3000]

        # Monta o prompt com contexto se fornecido
        if context:
            full_prompt = f"""
Contexto dos documentos:
{context}

Pergunta do usuário:
{prompt}

Instruções:
- Responda de forma completa, detalhada e precisa, utilizando todas as informações relevantes do contexto acima.
- Se possível, cite os documentos ou fontes utilizadas.
- Se a resposta não estiver nos documentos, explique que não foi possível encontrar a informação.
- Use linguagem clara e objetiva, e organize a resposta em tópicos se necessário.

Resposta:
"""
        else:
            full_prompt = f"""
Pergunta do usuário:
{prompt}

Instruções:
- Responda de forma completa, detalhada e precisa.
- Se não houver contexto, explique que não há informações suficientes.

Resposta:
"""

        attempt = 0
        while attempt < retries:
            try:
                payload = {
                    "model": self.model_name,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                }
                
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=1000
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get('response', '').strip()
                else:
                    self.logger.error(f"Erro na geração: {response.status_code}")
                    return "Erro ao gerar resposta"
                    
            except Exception as e:
                attempt += 1
                if attempt < retries:
                    self.logger.warning(f"Tentativa {attempt} falhou, tentando novamente...")
                    time.sleep(backoff_factor ** attempt)  # Exponential backoff
                else:
                    self.logger.error(f"Erro ao gerar resposta: {str(e)}")
                    return "Erro ao gerar resposta"
