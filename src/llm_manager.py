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
                 model_name: str = "llama3:latest"):
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
                         retries: int = 1,  # Reduzido para 1 (não fazer retries automáticos)
                         backoff_factor: float = 1.5) -> str:
        """
        Gera resposta usando o modelo local com Ollama
        """
        # Limita o tamanho do contexto para evitar envio de dados excessivos
        context = context[:5000]
        
        # Monta um prompt mais simples para acelerar o processamento
        if context:
            full_prompt = f"""
Usando apenas as informações do contexto abaixo, responda à pergunta do usuário de forma objetiva.

Contexto:
{context}

Pergunta: {prompt}

Resposta:
"""
        else:
            full_prompt = f"Pergunta: {prompt}\n\nResposta:"

        try:
            self.logger.info(f"Enviando consulta para o Ollama (modelo: {self.model_name})")
            
            payload = {
                "model": self.model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            # Aumenta o timeout
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=1000  # 16 minutos
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get('response', '').strip()
                self.logger.info(f"Resposta gerada com sucesso ({len(answer)} caracteres)")
                return answer
            else:
                self.logger.error(f"Erro na geração: código {response.status_code}")
                return "Erro ao gerar resposta do modelo: o servidor Ollama retornou um erro."
                
        except requests.exceptions.Timeout:
            self.logger.error("Timeout na comunicação com o Ollama")
            return "Tempo de resposta excedido. O modelo está demorando muito para processar a consulta."
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar resposta: {str(e)}")
            return f"Erro ao gerar resposta: {str(e)}"
