"""
Script para corrigir problemas com a transcrição de áudio.
"""
import logging
import os
import subprocess
import sys
import tempfile
from typing import Tuple, Optional

# Adiciona o diretório raiz ao path para importações relativas
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.settings import OPENAI_API_KEY, OPENAI_WHISPER_MODEL, configure_logging

# Configura o logging
configure_logging()
logger = logging.getLogger(__name__)

def verificar_dependencias():
    """
    Verifica se todas as dependências necessárias estão instaladas.
    
    Returns:
        bool: True se todas as dependências estão instaladas, False caso contrário
    """
    try:
        # Verifica se o ffmpeg está instalado
        result = subprocess.run(['which', 'ffmpeg'], capture_output=True, text=True)
        if not result.stdout.strip():
            logger.warning("ffmpeg não encontrado. Tentando instalar...")
            
            # Tenta instalar o ffmpeg
            try:
                # Verifica o sistema operacional
                if sys.platform == 'darwin':  # macOS
                    subprocess.run(['brew', 'install', 'ffmpeg'], check=True)
                elif sys.platform == 'linux':
                    # Tenta diferentes gerenciadores de pacotes
                    try:
                        subprocess.run(['apt-get', 'update'], check=True)
                        subprocess.run(['apt-get', 'install', '-y', 'ffmpeg'], check=True)
                    except subprocess.CalledProcessError:
                        try:
                            subprocess.run(['yum', 'install', '-y', 'ffmpeg'], check=True)
                        except subprocess.CalledProcessError:
                            logger.error("Não foi possível instalar o ffmpeg automaticamente")
                            print("Por favor, instale o ffmpeg manualmente e tente novamente.")
                            return False
                else:
                    logger.error(f"Sistema operacional não suportado para instalação automática: {sys.platform}")
                    print("Por favor, instale o ffmpeg manualmente e tente novamente.")
                    return False
                
                logger.info("ffmpeg instalado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao instalar ffmpeg: {e}")
                print("Por favor, instale o ffmpeg manualmente e tente novamente.")
                return False
        
        # Verifica se o pydub está instalado
        try:
            import pydub
            # O pydub não tem um atributo __version__ consistente, então apenas verificamos se está instalado
            logger.info(f"pydub encontrado e instalado corretamente")
        except ImportError:
            logger.warning("pydub não encontrado. Tentando instalar...")
            
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'pydub'], check=True)
                import pydub
                logger.info(f"pydub instalado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao instalar pydub: {e}")
                print("Por favor, instale o pydub manualmente: pip install pydub")
                return False
        
        # Verifica a versão da API OpenAI
        try:
            import openai
            openai_version = getattr(openai, "__version__", "desconhecida")
            logger.info(f"OpenAI API versão: {openai_version}")
            
            if openai_version != "0.28.0":
                logger.warning(f"Versão da API OpenAI ({openai_version}) diferente da recomendada (0.28.0)")
                print(f"Aviso: Versão da API OpenAI ({openai_version}) diferente da recomendada (0.28.0)")
                print("Isso pode causar problemas com a transcrição de áudio.")
                print("Considere instalar a versão recomendada: pip install openai==0.28.0")
        except ImportError:
            logger.error("OpenAI API não encontrada")
            print("Por favor, instale a API OpenAI: pip install openai==0.28.0")
            return False
        
        logger.info("Todas as dependências verificadas com sucesso")
        return True
    
    except Exception as e:
        logger.error(f"Erro ao verificar dependências: {e}")
        return False

def diagnosticar_arquivo_audio(audio_path):
    """
    Realiza diagnóstico detalhado de um arquivo de áudio.
    
    Args:
        audio_path: Caminho para o arquivo de áudio
        
    Returns:
        str: Relatório de diagnóstico do arquivo
    """
    try:
        # Verifica se o arquivo existe
        if not os.path.exists(audio_path):
            return f"ERRO: Arquivo não existe: {audio_path}"
        
        # Verifica o tamanho do arquivo
        tamanho = os.path.getsize(audio_path)
        if tamanho == 0:
            return f"ERRO: Arquivo vazio (0 bytes): {audio_path}"
        
        # Verifica o formato usando o comando 'file'
        result = subprocess.run(['file', audio_path], capture_output=True, text=True, check=True)
        formato = result.stdout.strip()
        
        # Exibe os primeiros bytes do arquivo para diagnóstico
        with open(audio_path, 'rb') as f:
            primeiros_bytes = f.read(32)
            bytes_hex = ' '.join([f'{b:02x}' for b in primeiros_bytes])
        
        # Tenta obter informações usando ffmpeg com timeout
        ffmpeg_info = "Não disponível"
        try:
            # Usa timeout para evitar travamento
            ffmpeg_result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_format', '-show_streams', audio_path],
                capture_output=True, text=True, check=False, timeout=5
            )
            if ffmpeg_result.returncode == 0:
                ffmpeg_info = ffmpeg_result.stdout.strip()
            else:
                ffmpeg_info = f"Erro ffprobe: {ffmpeg_result.stderr.strip()}"
        except subprocess.TimeoutExpired:
            ffmpeg_info = "Timeout ao executar ffprobe (comando demorou mais de 5 segundos)"
        except Exception as e:
            ffmpeg_info = f"Erro ao executar ffprobe: {e}"
        
        return f"Arquivo: {audio_path}\nTamanho: {tamanho} bytes\nFormato: {formato}\nPrimeiros bytes: {bytes_hex}\n\nInformações FFmpeg:\n{ffmpeg_info}"
    
    except Exception as e:
        logger.error(f"Erro ao diagnosticar arquivo de áudio: {e}")
        return f"Erro ao diagnosticar arquivo: {e}"

def testar_transcrição():
    """
    Testa a funcionalidade de transcrição de áudio usando arquivos existentes.
    
    Returns:
        bool: True se o teste foi bem-sucedido, False caso contrário
    """
    import requests
    import openai
    
    temp_wav_path = None
    
    try:
        # Verifica a chave da API OpenAI
        if not OPENAI_API_KEY:
            logger.error("OPENAI_API_KEY não está definida")
            print("Erro: OPENAI_API_KEY não está definida")
            return False
        
        logger.info(f"OPENAI_API_KEY está definida e tem {len(OPENAI_API_KEY)} caracteres")
        
        # Procura por arquivos de áudio existentes
        test_audio_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test_audio")
        
        # Cria o diretório de teste se não existir
        os.makedirs(test_audio_dir, exist_ok=True)
        
        # Verifica especificamente se o arquivo telegram_audio.ogg existe
        telegram_audio = "telegram_audio.ogg"
        telegram_audio_path = os.path.join(test_audio_dir, telegram_audio)
        
        if os.path.exists(telegram_audio_path):
            tamanho_arquivo = os.path.getsize(telegram_audio_path)
            print(f"\nArquivo de áudio do Telegram encontrado: {telegram_audio_path}")
            print(f"Tamanho: {tamanho_arquivo} bytes")
            
            # Verifica se o arquivo tem um tamanho mínimo (1KB)
            if tamanho_arquivo > 1024:
                audio_file = telegram_audio_path
                logger.info(f"Usando arquivo de áudio do Telegram: {audio_file} ({tamanho_arquivo} bytes)")
                print("Arquivo de áudio do Telegram é válido e será usado para teste.")
            else:
                print(f"ATENÇÃO: O arquivo de áudio do Telegram é muito pequeno ({tamanho_arquivo} bytes).")
                print("Isso pode indicar que o arquivo não foi salvo corretamente.")
                print("Envie uma nova mensagem de voz para o bot e tente novamente.")
                
                # Procura por arquivos alternativos
                audio_files = [f for f in os.listdir(test_audio_dir) if f.endswith(('.ogg', '.mp3', '.wav', '.m4a')) and f != telegram_audio]
                if audio_files:
                    audio_file = os.path.join(test_audio_dir, audio_files[0])
                    print(f"Usando arquivo de áudio alternativo: {audio_file}")
                else:
                    print("Nenhum arquivo de áudio alternativo encontrado.")
                    return False
        else:
            print(f"\nArquivo de áudio do Telegram não encontrado: {telegram_audio_path}")
            print("Para gerar este arquivo, envie uma mensagem de voz para o bot no Telegram.")
            
            # Verifica se há outros arquivos de áudio no diretório de teste
            audio_files = [f for f in os.listdir(test_audio_dir) if f.endswith(('.ogg', '.mp3', '.wav', '.m4a'))]
            
            if not audio_files:
                logger.warning("Nenhum arquivo de áudio encontrado no diretório de teste")
                print(f"Por favor, adicione arquivos de áudio em: {test_audio_dir}")
                print("Formatos suportados: .ogg, .mp3, .wav, .m4a")
                return False
            
            # Usa o primeiro arquivo de áudio encontrado
            audio_file = os.path.join(test_audio_dir, audio_files[0])
            print(f"Usando arquivo de áudio alternativo: {audio_file}")
        logger.info(f"Usando arquivo de áudio existente: {audio_file} ({os.path.getsize(audio_file)} bytes)")
        
        # Converte para WAV se não for WAV
        if not audio_file.endswith('.wav'):
            try:
                # Importa pydub para conversão de áudio
                from pydub import AudioSegment
                
                temp_fd, temp_wav_path = tempfile.mkstemp(suffix='.wav')
                os.close(temp_fd)
                
                logger.info(f"Convertendo {audio_file} para WAV usando pydub: {temp_wav_path}")
                
                # Tenta carregar o áudio com pydub
                try:
                    if audio_file.endswith('.ogg'):
                        # Para arquivos OGG do Telegram (que são na verdade Opus)
                        audio = AudioSegment.from_file(audio_file, format="ogg")
                    else:
                        # Para outros formatos
                        audio = AudioSegment.from_file(audio_file)
                    
                    # Converte para mono e 16kHz
                    audio = audio.set_channels(1).set_frame_rate(16000)
                    
                    # Exporta para WAV
                    audio.export(temp_wav_path, format="wav")
                    
                    logger.info(f"Conversão concluída: {os.path.getsize(temp_wav_path)} bytes")
                except Exception as e:
                    logger.error(f"Erro ao converter com pydub: {e}")
                    print(f"Erro na conversão com pydub: {e}")
                    
                    # Fallback para ffmpeg com timeout mais curto
                    logger.info("Tentando fallback para ffmpeg...")
                    try:
                        subprocess.run([
                            'ffmpeg', '-i', audio_file, '-ar', '16000', '-ac', '1', temp_wav_path
                        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
                    except Exception as e2:
                        logger.error(f"Erro no fallback para ffmpeg: {e2}")
                        print(f"Erro no fallback para ffmpeg: {e2}")
                        return False
                
                if not os.path.exists(temp_wav_path) or os.path.getsize(temp_wav_path) == 0:
                    logger.error("Falha ao converter arquivo de áudio para WAV")
                    return False
                
                audio_path = temp_wav_path
            except Exception as e:
                logger.error(f"Erro geral na conversão de áudio: {e}")
                print(f"Erro geral na conversão de áudio: {e}")
                return False
        else:
            audio_path = audio_file
        
        # Testa a transcrição usando a API REST direta
        logger.info("Testando transcrição com API REST...")
        
        # Configura a API key
        openai.api_key = OPENAI_API_KEY
        
        # Lê o arquivo de áudio
        with open(audio_path, "rb") as audio_file:
            audio_data = audio_file.read()
        
        # Configura os cabeçalhos para a solicitação
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        
        # Prepara os dados para upload
        files = {
            "file": ("audio.wav", audio_data, "audio/wav")
        }
        data = {
            "model": OPENAI_WHISPER_MODEL,
            "language": "pt",
            "response_format": "json",
            "temperature": 0.0
        }
        
        # Faz a solicitação para a API
        response = requests.post(
            "https://api.openai.com/v1/audio/transcriptions",
            headers=headers,
            files=files,
            data=data
        )
        
        # Verifica a resposta
        if response.status_code == 200:
            result = response.json()
            transcription = result.get("text", "")
            
            logger.info(f"Transcrição bem-sucedida: '{transcription}'")
            print(f"Teste de transcrição bem-sucedido!")
            print(f"Transcrição: '{transcription}'")
            return True
        else:
            logger.error(f"Erro na API: {response.status_code}")
            logger.error(f"Detalhes do erro: {response.text}")
            print(f"Erro na API: {response.status_code}")
            print(f"Detalhes do erro: {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"Erro ao testar transcrição: {e}")
        print(f"Erro ao testar transcrição: {e}")
        return False
        
    finally:
        # Limpa os arquivos temporários, mas não remove arquivos originais do diretório de teste
        if temp_wav_path and os.path.exists(temp_wav_path) and not temp_wav_path.startswith(test_audio_dir):
            try:
                os.remove(temp_wav_path)
                logger.info(f"Arquivo temporário removido: {temp_wav_path}")
            except Exception as e:
                logger.error(f"Erro ao remover arquivo temporário: {e}")

if __name__ == "__main__":
    logger.info("Iniciando verificação de áudio...")
    
    print("Verificando dependências para transcrição de áudio...")
    if verificar_dependencias():
        print("Todas as dependências estão instaladas corretamente.")
        
        # Verifica se o arquivo telegram_audio_empty.ogg existe para diagnóstico
        test_audio_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test_audio")
        telegram_audio_empty = os.path.join(test_audio_dir, "telegram_audio_empty.ogg")
        
        if os.path.exists(telegram_audio_empty):
            print("\nDiagnosticando arquivo vazio do Telegram...")
            diagnostico = diagnosticar_arquivo_audio(telegram_audio_empty)
            print(diagnostico)
            print("\n" + "-"*50 + "\n")
        
        # Verifica se o arquivo telegram_audio.ogg existe para diagnóstico
        telegram_audio = os.path.join(test_audio_dir, "telegram_audio.ogg")
        if os.path.exists(telegram_audio):
            print("\nDiagnosticando arquivo de áudio do Telegram...")
            diagnostico = diagnosticar_arquivo_audio(telegram_audio)
            print(diagnostico)
            print("\n" + "-"*50 + "\n")
        
        print("\nTestando funcionalidade de transcrição...")
        if testar_transcrição():
            print("\nTudo está funcionando corretamente!")
            print("A funcionalidade de transcrição de áudio está operacional.")
        else:
            print("\nProblemas detectados na funcionalidade de transcrição.")
            print("Verifique os logs para mais detalhes.")
    else:
        print("Problemas detectados nas dependências.")
        print("Verifique os logs para mais detalhes.")
