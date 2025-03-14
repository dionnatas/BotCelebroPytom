"""
Serviço para interação com a API da OpenAI.
"""
import json
import logging
from typing import Tuple, Optional, Dict, Any

import openai
import requests

from src.config.settings import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE
from src.config.prompts import CLASSIFICADOR_PROMPT, BRAINSTORM_PROMPT, QUESTAO_PROMPT

# Configuração da API da OpenAI
openai.api_key = OPENAI_API_KEY

logger = logging.getLogger(__name__)

class OpenAIService:
    """
    Serviço para interação com a API da OpenAI.
    """
    
    @staticmethod
    def classificar_mensagem(texto: str) -> Tuple[str, str, str]:
        """
        Classifica a mensagem usando o modelo de IA.
        
        Args:
            texto: Texto a ser classificado
            
        Returns:
            Tuple[str, str, str]: Tipo, conteúdo e resumo da mensagem
        """
        try:
            logger.info("Classificando mensagem...")
            
            # Prepara o prompt completo
            prompt_completo = f"{CLASSIFICADOR_PROMPT}\n{texto}"
            
            # Faz a chamada para a API da OpenAI
            response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Você é um assistente que classifica mensagens."},
                    {"role": "user", "content": prompt_completo}
                ],
                temperature=OPENAI_TEMPERATURE
            )
            
            # Extrai a resposta
            resposta = response.choices[0].message.content.strip()
            logger.info(f"Resposta da classificação: {resposta}")
            
            # Tenta extrair os dados da resposta
            try:
                # Tenta interpretar como JSON
                dados = json.loads(resposta)
                if isinstance(dados, list) and len(dados) == 3:
                    tipo, conteudo, resumo = dados
                    return tipo, conteudo, resumo
            except json.JSONDecodeError:
                # Se não for JSON, tenta extrair manualmente
                pass
            
            # Tenta extrair usando regex ou parsing manual
            import re
            match = re.search(r'\["([^"]+)","([^"]+)","([^"]+)"\]', resposta)
            if match:
                tipo, conteudo, resumo = match.groups()
                return tipo, conteudo, resumo
            
            # Fallback: retorna a mensagem original como QUESTAO
            logger.warning("Não foi possível classificar a mensagem, usando fallback")
            return "QUESTAO", texto, texto[:30] + "..." if len(texto) > 30 else texto
            
        except Exception as e:
            logger.error(f"Erro ao classificar mensagem: {e}")
            return "QUESTAO", texto, texto[:30] + "..." if len(texto) > 30 else texto
    
    @staticmethod
    def gerar_brainstorm(ideia: str) -> str:
        """
        Gera um brainstorm para uma ideia usando o modelo de IA.
        
        Args:
            ideia: Texto da ideia
            
        Returns:
            str: Texto do brainstorm gerado
        """
        try:
            logger.info("Gerando brainstorm...")
            
            # Prepara o prompt completo
            prompt_completo = f"{BRAINSTORM_PROMPT}\n{ideia}"
            
            # Faz a chamada para a API da OpenAI
            response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Você é um especialista em inovação e brainstorming."},
                    {"role": "user", "content": prompt_completo}
                ],
                temperature=OPENAI_TEMPERATURE
            )
            
            # Extrai a resposta
            brainstorm = response.choices[0].message.content.strip()
            logger.info("Brainstorm gerado com sucesso")
            
            return brainstorm
            
        except Exception as e:
            logger.error(f"Erro ao gerar brainstorm: {e}")
            return f"Erro ao gerar brainstorm: {e}"
    
    @staticmethod
    def responder_questao(questao: str) -> str:
        """
        Responde a uma questão do usuário usando o modelo de IA.
        
        Args:
            questao: Texto da questão
            
        Returns:
            str: Texto da resposta gerada
        """
        try:
            logger.info("Respondendo questão...")
            
            # Prepara o prompt completo
            prompt_completo = f"{QUESTAO_PROMPT}\n{questao}"
            
            # Faz a chamada para a API da OpenAI
            response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Você é um assistente virtual útil e informativo."},
                    {"role": "user", "content": prompt_completo}
                ],
                temperature=OPENAI_TEMPERATURE
            )
            
            # Extrai a resposta
            resposta = response.choices[0].message.content.strip()
            logger.info("Resposta gerada com sucesso")
            
            return resposta
            
        except Exception as e:
            logger.error(f"Erro ao responder questão: {e}")
            return f"Desculpe, não consegui processar sua pergunta devido a um erro: {e}"


# Instância global do serviço OpenAI
openai_service = OpenAIService()
