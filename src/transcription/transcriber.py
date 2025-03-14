"""
Transcritor de áudio usando a API da OpenAI.
"""
import logging
import os
import subprocess
import tempfile
from typing import Tuple, Optional

import openai
import requests

from src.config.settings import OPENAI_API_KEY, OPENAI_WHISPER_MODEL
from src.transcription.audio_processor import audio_processor

logger = logging.getLogger(__name__)

class AudioTranscriber:
    """
    Transcritor de áudio usando a API da OpenAI.
    """
    
    def __init__(self):
        """
        Inicializa o transcritor de áudio.
        """
        self.api_key = OPENAI_API_KEY
        self.model = OPENAI_WHISPER_MODEL
    
    def transcrever_audio(self, audio_path: str) -> Tuple[bool, str]:
        """
        Transcreve um arquivo de áudio.
        
        Args:
            audio_path: Caminho para o arquivo de áudio
            
        Returns:
            Tuple[bool, str]: Sucesso da transcrição e texto transcrito
        """
        temp_wav_path = None
        upload_path = None
        
        try:
            # Verifica se o arquivo existe
            if not os.path.exists(audio_path):
                logger.error(f"Arquivo de áudio não encontrado: {audio_path}")
                return False, "Arquivo de áudio não encontrado"
            
            # Converte o áudio para WAV
            logger.info("Convertendo áudio para WAV...")
            success, temp_wav_path = audio_processor.converter_para_wav(audio_path)
            
            if not success or not temp_wav_path:
                logger.error("Falha na conversão do áudio para WAV")
                return False, "Falha na conversão do áudio"
            
            # Transcreve o áudio usando a API REST direta
            logger.info("Transcrevendo áudio usando API REST...")
            
            # Configura os cabeçalhos para a solicitação
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Método 1: Usando arquivo diretamente
            try:
                logger.info("Método 1: Usando arquivo diretamente")
                
                with open(temp_wav_path, "rb") as audio_file:
                    files = {
                        "file": ("audio.wav", audio_file, "audio/wav")
                    }
                    
                    data = {
                        "model": self.model,
                        "language": "pt",
                        "response_format": "json",
                        "temperature": 0.0
                    }
                    
                    response = requests.post(
                        "https://api.openai.com/v1/audio/transcriptions",
                        headers=headers,
                        files=files,
                        data=data
                    )
                    
                    logger.info(f"Código de status da resposta: {response.status_code}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        transcription = result.get("text", "")
                        logger.info(f"Texto transcrito: '{transcription}'")
                        
                        if transcription and transcription.strip():
                            logger.info("Transcrição bem-sucedida com Método 1!")
                            return True, transcription
                    else:
                        logger.warning(f"Método 1 falhou: {response.status_code} - {response.text}")
            except Exception as e:
                logger.warning(f"Erro no Método 1: {e}")
            
            # Método 2: Usando arquivo temporário
            try:
                logger.info("Método 2: Usando arquivo temporário")
                
                # Cria um arquivo temporário para o upload
                upload_fd, upload_path = tempfile.mkstemp(suffix='.wav')
                os.close(upload_fd)
                
                # Lê o arquivo de áudio
                with open(temp_wav_path, "rb") as src_file:
                    audio_data = src_file.read()
                
                # Escreve os dados no arquivo temporário
                with open(upload_path, 'wb') as dst_file:
                    dst_file.write(audio_data)
                
                logger.info(f"Arquivo temporário criado: {upload_path} ({os.path.getsize(upload_path)} bytes)")
                
                # Prepara o arquivo para upload
                with open(upload_path, 'rb') as f:
                    files = {
                        "file": ("audio.wav", f, "audio/wav")
                    }
                    
                    data = {
                        "model": self.model,
                        "language": "pt",
                        "response_format": "json",
                        "temperature": 0.0
                    }
                    
                    response = requests.post(
                        "https://api.openai.com/v1/audio/transcriptions",
                        headers=headers,
                        files=files,
                        data=data
                    )
                    
                    logger.info(f"Código de status da resposta: {response.status_code}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        transcription = result.get("text", "")
                        logger.info(f"Texto transcrito: '{transcription}'")
                        
                        if transcription and transcription.strip():
                            logger.info("Transcrição bem-sucedida com Método 2!")
                            return True, transcription
                    else:
                        logger.warning(f"Método 2 falhou: {response.status_code} - {response.text}")
            except Exception as e:
                logger.warning(f"Erro no Método 2: {e}")
            
            # Método 3: Usando requests_toolbelt
            try:
                logger.info("Método 3: Usando requests_toolbelt")
                
                try:
                    from requests_toolbelt.multipart.encoder import MultipartEncoder
                except ImportError:
                    logger.info("Instalando requests_toolbelt...")
                    subprocess.run(["python3", "-m", "pip", "install", "requests_toolbelt"], check=True)
                    from requests_toolbelt.multipart.encoder import MultipartEncoder
                
                with open(temp_wav_path, "rb") as audio_file:
                    audio_data = audio_file.read()
                
                # Cria um dicionário com os campos do formulário
                fields = {
                    'file': ('audio.wav', audio_data, 'audio/wav'),
                    'model': self.model,
                    'language': 'pt',
                    'response_format': 'json',
                    'temperature': '0.0'
                }
                
                # Cria o codificador multipart
                m = MultipartEncoder(fields=fields)
                
                # Atualiza os cabeçalhos com o tipo de conteúdo correto
                headers['Content-Type'] = m.content_type
                
                # Faz a solicitação
                response = requests.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers=headers,
                    data=m
                )
                
                logger.info(f"Código de status da resposta: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    transcription = result.get("text", "")
                    logger.info(f"Texto transcrito: '{transcription}'")
                    
                    if transcription and transcription.strip():
                        logger.info("Transcrição bem-sucedida com Método 3!")
                        return True, transcription
                else:
                    logger.warning(f"Método 3 falhou: {response.status_code} - {response.text}")
            except Exception as e:
                logger.warning(f"Erro no Método 3: {e}")
            
            # Se chegou até aqui, todos os métodos falharam
            logger.error("Todos os métodos de transcrição falharam")
            return False, "Não foi possível transcrever o áudio após várias tentativas"
        except Exception as e:
            logger.error(f"Erro na transcrição: {e}")
            return False, f"Erro na transcrição: {e}"
            
        finally:
            # Limpa os arquivos temporários
            if temp_wav_path and os.path.exists(temp_wav_path):
                try:
                    os.remove(temp_wav_path)
                    logger.info(f"Arquivo temporário removido: {temp_wav_path}")
                except Exception as e:
                    logger.error(f"Erro ao remover arquivo temporário: {e}")
                    
            if upload_path and os.path.exists(upload_path):
                try:
                    os.remove(upload_path)
                    logger.info(f"Arquivo temporário de upload removido: {upload_path}")
                except Exception as e:
                    logger.error(f"Erro ao remover arquivo temporário de upload: {e}")


# Instância global do transcritor de áudio
audio_transcriber = AudioTranscriber()
