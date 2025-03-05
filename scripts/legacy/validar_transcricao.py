#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import io
import sys
import tempfile
import logging
import requests
import subprocess
from secrets_cerebro import OPENAI_API_KEY
import openai

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Verifica a versão da API OpenAI
logger.info(f"Usando OpenAI API versão: {openai.__version__}")
logger.info(f"OPENAI_API_KEY configurada: {bool(OPENAI_API_KEY)} (comprimento: {len(OPENAI_API_KEY)})")

def converter_para_wav(audio_path):
    """Converte o arquivo de áudio para WAV com parâmetros específicos."""
    temp_wav_path = None
    try:
        # Cria um arquivo temporário para o WAV
        temp_wav_fd, temp_wav_path = tempfile.mkstemp(suffix='.wav')
        os.close(temp_wav_fd)
        
        # Certifica-se de que pydub está instalado
        try:
            from pydub import AudioSegment
        except ImportError:
            logger.info("Instalando pydub...")
            subprocess.run(["python3", "-m", "pip", "install", "pydub"], check=True)
            from pydub import AudioSegment
        
        # Carrega o áudio
        logger.info(f"Carregando arquivo de áudio: {audio_path}")
        try:
            # Tenta determinar o formato do arquivo
            result = subprocess.run(['file', audio_path], capture_output=True, text=True)
            logger.info(f"Informações do arquivo: {result.stdout}")
            
            # Tenta carregar com formato específico primeiro
            if 'ogg' in result.stdout.lower():
                logger.info("Detectado formato OGG")
                sound = AudioSegment.from_file(audio_path, format="ogg")
            elif 'mp3' in result.stdout.lower():
                logger.info("Detectado formato MP3")
                sound = AudioSegment.from_file(audio_path, format="mp3")
            elif 'wav' in result.stdout.lower():
                logger.info("Detectado formato WAV")
                sound = AudioSegment.from_file(audio_path, format="wav")
            else:
                # Tenta formato genérico
                logger.info("Formato não reconhecido, tentando formato genérico")
                sound = AudioSegment.from_file(audio_path)
        except Exception as e:
            logger.error(f"Erro ao carregar áudio: {e}")
            raise
        
        # Configura o áudio para formato compatível com Whisper
        logger.info("Configurando áudio para formato compatível com Whisper")
        sound = sound.set_channels(1)  # Mono
        sound = sound.set_frame_rate(16000)  # 16kHz
        
        # Exporta para WAV
        logger.info(f"Exportando para WAV: {temp_wav_path}")
        sound.export(temp_wav_path, format="wav")
        
        # Verifica o arquivo WAV
        if os.path.exists(temp_wav_path) and os.path.getsize(temp_wav_path) > 0:
            logger.info(f"Arquivo WAV criado com sucesso: {os.path.getsize(temp_wav_path)} bytes")
            return temp_wav_path
        else:
            logger.error("Arquivo WAV não foi criado corretamente")
            return None
    except Exception as e:
        logger.error(f"Erro na conversão para WAV: {e}")
        if temp_wav_path and os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)
        return None

def testar_transcricao(audio_path):
    """Testa a transcrição de áudio usando o método direto da API REST.
    
    Returns:
        tuple: (success, transcription) onde success é um booleano indicando se a transcrição foi bem-sucedida
               e transcription é o texto transcrito (ou string vazia se falhar)
    """
    
    if not os.path.exists(audio_path):
        logger.error(f"Arquivo de áudio não encontrado: {audio_path}")
        return False, ""
    
    logger.info(f"Testando transcrição do arquivo: {audio_path}")
    logger.info(f"Tamanho do arquivo: {os.path.getsize(audio_path)} bytes")
    
    # Converte o arquivo para WAV se necessário
    temp_wav_path = None
    try:
        # Converte para WAV com parâmetros específicos
        temp_wav_path = converter_para_wav(audio_path)
        if not temp_wav_path:
            logger.error("Falha na conversão para WAV")
            return False, ""
        
        # Usa o arquivo WAV para transcrição
        logger.info("Iniciando transcrição com o arquivo WAV convertido")
        
        # Tenta transcrever usando o método direto da API REST
        transcription_success = False
        user_message = ""
        
        try:
            logger.info("Transcrevendo áudio usando chamada direta à API REST...")
            
            # Lê o arquivo de áudio
            with open(temp_wav_path, "rb") as audio_file:
                audio_data = audio_file.read()
            
            logger.info(f"Arquivo de áudio lido: {len(audio_data)} bytes")
            
            # Configura os cabeçalhos para a solicitação
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            }
            
            # Prepara os dados para upload
            files = {
                "file": ("audio.wav", audio_data, "audio/wav")
            }
            data = {
                "model": "whisper-1",
                "language": "pt",  # Especifica o idioma português
                "response_format": "json"  # Garante resposta em JSON
            }
            
            # Faz a solicitação para a API
            logger.info("Enviando solicitação para a API OpenAI...")
            response = requests.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers=headers,
                files=files,
                data=data
            )
            
            # Verifica a resposta
            logger.info(f"Código de status da resposta: {response.status_code}")
            logger.info(f"Cabeçalhos da resposta: {response.headers}")
            
            if response.status_code == 200:
                # Processa a resposta bem-sucedida
                result = response.json()
                logger.info(f"Resposta completa da API: {result}")
                
                user_message = result.get("text", "")
                logger.info(f"Texto transcrito: '{user_message}'")
                
                if user_message and user_message.strip():
                    logger.info("Transcrição bem-sucedida!")
                    transcription_success = True
                else:
                    logger.error("A transcrição retornou texto vazio")
            else:
                # Registra detalhes do erro
                logger.error(f"Erro na API: {response.status_code}")
                logger.error(f"Detalhes do erro: {response.text}")
        except Exception as e:
            logger.error(f"Erro na transcrição: {e}")
        # Retorna o resultado da transcrição
        return transcription_success, user_message
    finally:
        # Limpa os arquivos temporários
        if temp_wav_path and os.path.exists(temp_wav_path):
            try:
                os.remove(temp_wav_path)
                logger.info(f"Arquivo temporário removido: {temp_wav_path}")
            except Exception as e:
                logger.error(f"Erro ao remover arquivo temporário: {e}")

def main():
    """Função principal para testar a transcrição de áudio."""
    
    if len(sys.argv) > 1:
        audio_path = sys.argv[1]
    else:
        # Verifica se existe um arquivo de áudio de exemplo
        audio_path = "sample.wav"
        if not os.path.exists(audio_path):
            logger.error(f"Arquivo de exemplo {audio_path} não encontrado. Especifique um arquivo de áudio como argumento.")
            print(f"Uso: python3 {sys.argv[0]} <caminho_para_arquivo_audio>")
            return 1
    
    logger.info(f"Testando transcrição do arquivo: {audio_path}")
    resultado = testar_transcricao(audio_path)
    
    # Verifica se o resultado é uma tupla (success, transcription) ou apenas um booleano
    if isinstance(resultado, tuple) and len(resultado) == 2:
        success, transcription = resultado
    else:
        success = resultado
        transcription = ""
    
    if success:
        logger.info("Transcrição bem-sucedida!")
        print(f"\nTranscrição:\n{transcription}\n")
        return 0
    else:
        logger.error("Falha na transcrição")
        print("\nFalha na transcrição. Verifique os logs para mais detalhes.\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
