#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir problemas de transcrição de áudio no Termux
"""

import os
import sys
import subprocess
import shutil
import logging
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_termux():
    """Verifica se estamos rodando no Termux"""
    return os.path.exists("/data/data/com.termux")

def install_package(package):
    """Instala um pacote no Termux usando pkg"""
    try:
        logger.info(f"Instalando {package}...")
        subprocess.run(["pkg", "install", "-y", package], check=True)
        return True
    except subprocess.CalledProcessError:
        logger.error(f"Falha ao instalar {package}")
        return False

def check_and_install_ffmpeg():
    """Verifica se o ffmpeg está instalado e funcionando"""
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        logger.info("FFmpeg está instalado e funcionando corretamente")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.warning("FFmpeg não encontrado ou não está funcionando corretamente")
        return install_package("ffmpeg")

def check_and_install_file_command():
    """Verifica se o comando file está instalado e funcionando"""
    try:
        subprocess.run(["file", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        logger.info("Comando 'file' está instalado e funcionando corretamente")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.warning("Comando 'file' não encontrado ou não está funcionando corretamente")
        return install_package("file")

def setup_tmp_directory():
    """Configura um diretório temporário no Termux"""
    home = os.path.expanduser("~")
    tmp_dir = os.path.join(home, "tmp")
    
    if not os.path.exists(tmp_dir):
        logger.info(f"Criando diretório temporário em {tmp_dir}")
        os.makedirs(tmp_dir, exist_ok=True)
    
    # Define a variável de ambiente TMPDIR
    os.environ["TMPDIR"] = tmp_dir
    
    # Adiciona ao .bashrc se ainda não estiver lá
    bashrc = os.path.join(home, ".bashrc")
    export_line = f"export TMPDIR={tmp_dir}"
    
    if os.path.exists(bashrc):
        with open(bashrc, "r") as f:
            if export_line not in f.read():
                with open(bashrc, "a") as f:
                    f.write(f"\n{export_line}\n")
                    logger.info(f"Adicionado {export_line} ao .bashrc")
    else:
        with open(bashrc, "w") as f:
            f.write(f"{export_line}\n")
            logger.info(f"Criado .bashrc com {export_line}")
    
    return tmp_dir

def patch_audio_processor():
    """Modifica o processador de áudio para funcionar no Termux"""
    audio_processor_path = os.path.join("src", "transcription", "audio_processor.py")
    
    if not os.path.exists(audio_processor_path):
        logger.error(f"Arquivo {audio_processor_path} não encontrado")
        return False
    
    # Faz backup do arquivo original
    backup_path = f"{audio_processor_path}.bak"
    if not os.path.exists(backup_path):
        shutil.copy2(audio_processor_path, backup_path)
        logger.info(f"Backup criado em {backup_path}")
    
    # Lê o conteúdo do arquivo
    with open(audio_processor_path, "r") as f:
        content = f.read()
    
    # Modifica o conteúdo para usar subprocess em vez de comandos diretos
    if "subprocess.run([\"file\"" not in content:
        # Substitui o uso do comando 'file'
        content = content.replace(
            "os.system(f\"file {audio_file}\")",
            "subprocess.run([\"file\", audio_file], check=False)"
        )
        
        # Adiciona import subprocess se necessário
        if "import subprocess" not in content:
            content = content.replace(
                "import os",
                "import os\nimport subprocess"
            )
        
        # Modifica a conversão de áudio para usar pydub diretamente
        if "from pydub import AudioSegment" not in content:
            content = content.replace(
                "import os",
                "import os\nfrom pydub import AudioSegment"
            )
        
        # Substitui a função converter_para_wav
        old_function = """def converter_para_wav(audio_file: str) -> str:
    \"\"\"Converte um arquivo de áudio para o formato WAV.\"\"\"
    try:
        logger.info(f"Verificando formato do arquivo: {audio_file}")
        os.system(f"file {audio_file}")
        
        # Verifica se o arquivo existe e tem tamanho
        if not os.path.exists(audio_file):
            logger.error(f"Arquivo não encontrado: {audio_file}")
            return None
            
        file_size = os.path.getsize(audio_file)
        logger.info(f"Arquivo de áudio existe e tem tamanho: {file_size} bytes")
        
        # Instala pydub se necessário
        try:
            import pydub
        except ImportError:
            logger.info("Instalando pydub...")
            os.system("pip install pydub")
            import pydub
        
        # Define o caminho para o arquivo WAV de saída
        wav_file = audio_file.rsplit('.', 1)[0] + '.wav'
        
        # Converte para WAV usando pydub
        logger.info(f"Convertendo {audio_file} para {wav_file}")
        os.system(f"ffmpeg -i {audio_file} -acodec pcm_s16le -ar 16000 -ac 1 {wav_file}")
        
        # Verifica se a conversão foi bem-sucedida
        if os.path.exists(wav_file) and os.path.getsize(wav_file) > 0:
            logger.info(f"Conversão bem-sucedida. Tamanho do arquivo WAV: {os.path.getsize(wav_file)} bytes")
            return wav_file
        else:
            logger.error(f"Falha na conversão. Arquivo WAV não encontrado ou vazio.")
            return None
    except Exception as e:
        logger.error(f"Erro na conversão para WAV: {e}")
        return None"""
        
        new_function = """def converter_para_wav(audio_file: str) -> str:
    \"\"\"Converte um arquivo de áudio para o formato WAV usando pydub diretamente.\"\"\"
    try:
        logger.info(f"Verificando formato do arquivo: {audio_file}")
        subprocess.run(["file", audio_file], check=False)
        
        # Verifica se o arquivo existe e tem tamanho
        if not os.path.exists(audio_file):
            logger.error(f"Arquivo não encontrado: {audio_file}")
            return None
            
        file_size = os.path.getsize(audio_file)
        logger.info(f"Arquivo de áudio existe e tem tamanho: {file_size} bytes")
        
        # Instala pydub se necessário
        try:
            from pydub import AudioSegment
        except ImportError:
            logger.info("Instalando pydub...")
            subprocess.run(["pip", "install", "pydub"], check=True)
            from pydub import AudioSegment
        
        # Define o caminho para o arquivo WAV de saída
        wav_file = audio_file.rsplit('.', 1)[0] + '.wav'
        
        # Converte para WAV usando pydub diretamente
        logger.info(f"Convertendo {audio_file} para {wav_file} usando pydub")
        try:
            # Tenta carregar o áudio com pydub
            audio = AudioSegment.from_file(audio_file)
            # Configura para 16kHz, mono, 16-bit PCM
            audio = audio.set_frame_rate(16000).set_channels(1)
            # Exporta como WAV
            audio.export(wav_file, format="wav")
            logger.info(f"Conversão bem-sucedida usando pydub. Tamanho do arquivo WAV: {os.path.getsize(wav_file)} bytes")
        except Exception as e:
            logger.warning(f"Falha ao converter com pydub: {e}. Tentando com ffmpeg...")
            # Tenta com ffmpeg como fallback
            try:
                subprocess.run([
                    "ffmpeg", "-i", audio_file, 
                    "-acodec", "pcm_s16le", 
                    "-ar", "16000", 
                    "-ac", "1", 
                    wav_file
                ], check=True)
                logger.info(f"Conversão bem-sucedida com ffmpeg. Tamanho do arquivo WAV: {os.path.getsize(wav_file)} bytes")
            except Exception as e2:
                logger.error(f"Falha também com ffmpeg: {e2}")
                return None
        
        # Verifica se a conversão foi bem-sucedida
        if os.path.exists(wav_file) and os.path.getsize(wav_file) > 0:
            return wav_file
        else:
            logger.error(f"Falha na conversão. Arquivo WAV não encontrado ou vazio.")
            return None
    except Exception as e:
        logger.error(f"Erro na conversão para WAV: {e}")
        return None"""
        
        content = content.replace(old_function, new_function)
        
        # Escreve o conteúdo modificado
        with open(audio_processor_path, "w") as f:
            f.write(content)
        
        logger.info(f"Arquivo {audio_processor_path} modificado com sucesso")
        return True
    else:
        logger.info(f"Arquivo {audio_processor_path} já foi modificado")
        return True

def main():
    """Função principal"""
    if not check_termux():
        logger.error("Este script é específico para o Termux no Android")
        sys.exit(1)
    
    logger.info("Iniciando correções para o Termux")
    
    # Verifica e instala dependências
    ffmpeg_ok = check_and_install_ffmpeg()
    file_ok = check_and_install_file_command()
    
    # Configura diretório temporário
    tmp_dir = setup_tmp_directory()
    logger.info(f"Diretório temporário configurado: {tmp_dir}")
    
    # Modifica o processador de áudio
    audio_processor_patched = patch_audio_processor()
    
    # Verifica se tudo foi bem-sucedido
    if ffmpeg_ok and file_ok and audio_processor_patched:
        logger.info("Todas as correções foram aplicadas com sucesso")
    else:
        logger.warning("Algumas correções não puderam ser aplicadas")
        if not ffmpeg_ok:
            logger.error("FFmpeg não está instalado corretamente")
        if not file_ok:
            logger.error("Comando 'file' não está instalado corretamente")
        if not audio_processor_patched:
            logger.error("Não foi possível modificar o processador de áudio")
    
    logger.info("Correções para o Termux concluídas")

if __name__ == "__main__":
    main()
