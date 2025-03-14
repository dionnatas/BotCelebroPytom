"""
Processador de áudio para transcrição.
"""
import logging
import os
import subprocess
import tempfile
from typing import Tuple, Optional

from src.config.settings import WHISPER_SAMPLE_RATE

logger = logging.getLogger(__name__)

class AudioProcessor:
    """
    Processador de áudio para preparação antes da transcrição.
    """
    
    @staticmethod
    def converter_para_wav(audio_path: str) -> Tuple[bool, Optional[str]]:
        """
        Converte o arquivo de áudio para WAV com parâmetros específicos para Whisper.
        
        Args:
            audio_path: Caminho para o arquivo de áudio original
            
        Returns:
            Tuple[bool, Optional[str]]: Sucesso da conversão e caminho do arquivo WAV
        """
        temp_wav_path = None
        try:
            # Verifica se o arquivo de entrada existe
            if not os.path.exists(audio_path):
                logger.error(f"Arquivo de áudio não encontrado: {audio_path}")
                return False, None
                
            # Verifica o tamanho do arquivo
            if os.path.getsize(audio_path) == 0:
                logger.error(f"Arquivo de áudio está vazio: {audio_path}")
                return False, None
                
            logger.info(f"Arquivo de áudio existe e tem tamanho: {os.path.getsize(audio_path)} bytes")
            
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
            
            # Tenta determinar o formato do arquivo
            result = subprocess.run(['file', audio_path], capture_output=True, text=True)
            logger.info(f"Informações do arquivo: {result.stdout}")
            
            # Carrega o áudio com o formato apropriado
            if 'ogg' in result.stdout.lower():
                logger.info("Detectado formato OGG")
                sound = AudioSegment.from_file(audio_path, format="ogg")
            elif 'mp3' in result.stdout.lower():
                logger.info("Detectado formato MP3")
                sound = AudioSegment.from_file(audio_path, format="mp3")
            elif 'wav' in result.stdout.lower():
                logger.info("Detectado formato WAV")
                sound = AudioSegment.from_file(audio_path, format="wav")
            elif 'm4a' in result.stdout.lower() or 'mp4' in result.stdout.lower():
                logger.info("Detectado formato M4A/MP4")
                sound = AudioSegment.from_file(audio_path, format="mp4")
            else:
                # Tenta formato genérico
                logger.info("Formato não reconhecido, tentando formato genérico")
                sound = AudioSegment.from_file(audio_path)
            
            # Configura para mono e 16kHz (requisitos do Whisper)
            logger.info("Configurando áudio para mono e 16kHz...")
            sound = sound.set_channels(1)  # Mono
            sound = sound.set_frame_rate(WHISPER_SAMPLE_RATE)  # 16kHz
            
            # Exporta para WAV
            logger.info(f"Exportando para WAV: {temp_wav_path}")
            sound.export(temp_wav_path, format="wav")
            
            # Verifica se o arquivo WAV foi criado corretamente
            if os.path.exists(temp_wav_path) and os.path.getsize(temp_wav_path) > 0:
                logger.info(f"Arquivo WAV criado com sucesso: {os.path.getsize(temp_wav_path)} bytes")
                return True, temp_wav_path
            else:
                logger.error("Arquivo WAV não foi criado corretamente")
                return False, None
                
        except Exception as e:
            logger.error(f"Erro na conversão para WAV: {e}")
            return False, None


# Instância global do processador de áudio
audio_processor = AudioProcessor()
