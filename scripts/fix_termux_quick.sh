#!/bin/bash
# Script para corrigir rapidamente os problemas de áudio no Termux

echo "Corrigindo problemas de áudio no Termux..."

# Instala pacotes necessários
echo "Instalando pacotes necessários..."
pkg install -y ffmpeg file python

# Cria diretório temporário
if [ ! -d "$HOME/tmp" ]; then
    echo "Criando diretório temporário em $HOME/tmp"
    mkdir -p "$HOME/tmp"
fi

# Configura variável de ambiente TMPDIR
export TMPDIR=$HOME/tmp
echo "export TMPDIR=$HOME/tmp" >> "$HOME/.bashrc"

# Instala pydub
echo "Instalando pydub..."
pip install pydub

# Verifica se o ffmpeg está instalado corretamente
if command -v ffmpeg >/dev/null 2>&1; then
    echo "FFmpeg está instalado:"
    ffmpeg -version | head -n 1
else
    echo "ERRO: FFmpeg não foi instalado corretamente."
    echo "Tente instalar manualmente com: pkg install ffmpeg"
fi

# Verifica se o comando file está instalado corretamente
if command -v file >/dev/null 2>&1; then
    echo "Comando 'file' está instalado:"
    file --version | head -n 1
else
    echo "ERRO: Comando 'file' não foi instalado corretamente."
    echo "Tente instalar manualmente com: pkg install file"
fi

# Cria um script Python para corrigir o processador de áudio
cat > fix_audio.py << 'EOL'
#!/usr/bin/env python3
import os
import shutil

# Caminho para o arquivo do processador de áudio
audio_processor_path = os.path.join("src", "transcription", "audio_processor.py")

# Verifica se o arquivo existe
if not os.path.exists(audio_processor_path):
    print(f"ERRO: Arquivo {audio_processor_path} não encontrado")
    exit(1)

# Faz backup do arquivo original
backup_path = f"{audio_processor_path}.bak"
if not os.path.exists(backup_path):
    shutil.copy2(audio_processor_path, backup_path)
    print(f"Backup criado em {backup_path}")

# Lê o conteúdo do arquivo
with open(audio_processor_path, "r") as f:
    content = f.read()

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
            os.system("pip install pydub")
            from pydub import AudioSegment
        
        # Define o caminho para o arquivo WAV de saída
        wav_file = audio_file.rsplit('.', 1)[0] + '.wav'
        
        # Tenta converter com pydub
        try:
            logger.info(f"Convertendo {audio_file} para {wav_file} usando pydub")
            # Carrega o áudio com pydub
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
                import subprocess
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
            logger.info(f"Conversão bem-sucedida. Tamanho do arquivo WAV: {os.path.getsize(wav_file)} bytes")
            return wav_file
        else:
            logger.error(f"Falha na conversão. Arquivo WAV não encontrado ou vazio.")
            return None
    except Exception as e:
        logger.error(f"Erro na conversão para WAV: {e}")
        return None"""

# Substitui a função
if old_function in content:
    content = content.replace(old_function, new_function)
    print("Função converter_para_wav substituída com sucesso")
else:
    print("AVISO: Não foi possível encontrar a função converter_para_wav para substituir")
    print("O arquivo pode já ter sido modificado ou a função foi alterada")

# Adiciona import subprocess se necessário
if "import subprocess" not in content:
    content = content.replace("import os", "import os\nimport subprocess")
    print("Import subprocess adicionado")

# Escreve o conteúdo modificado
with open(audio_processor_path, "w") as f:
    f.write(content)

print(f"Arquivo {audio_processor_path} modificado com sucesso")
EOL

# Executa o script Python
echo "Modificando o processador de áudio..."
python fix_audio.py

echo "Correções concluídas!"
echo "Reinicie o bot com: ./scripts/restart_bot.sh"
