#!/bin/bash
# Script para configurar o ambiente no Termux (Android)

echo "Configurando ambiente para o bot Cerebro no Termux..."

# Verifica se está no Termux
if [ -d "/data/data/com.termux" ]; then
    echo "Ambiente Termux detectado."
else
    echo "Este script é específico para o Termux no Android."
    echo "Se você está em outro ambiente, use pip install -r requirements.txt."
    exit 1
fi

# Atualiza os pacotes
echo "Atualizando pacotes..."
pkg update -y && pkg upgrade -y

# Instala dependências necessárias
echo "Instalando dependências..."
pkg install -y python ffmpeg libffi openssl file coreutils

# Instala as dependências Python
echo "Instalando dependências Python..."
pip install -r requirements.txt

# Verifica a instalação do OpenAI
echo "Verificando versão da API OpenAI..."
if pip show openai | grep -q "Version: 0.28.0"; then
    echo "OpenAI API versão 0.28.0 instalada corretamente."
else
    echo "Instalando versão específica da API OpenAI..."
    pip uninstall -y openai
    pip install openai==0.28.0
fi

# Verifica se o arquivo de segredos existe
if [ ! -f "secrets_cerebro.py" ]; then
    if [ -f "secrets_cerebro.py.example" ]; then
        echo "Arquivo secrets_cerebro.py não encontrado."
        echo "Criando a partir do exemplo..."
        cp secrets_cerebro.py.example secrets_cerebro.py
        echo "Por favor, edite o arquivo secrets_cerebro.py e adicione suas chaves de API."
    else
        echo "ERRO: Arquivo secrets_cerebro.py.example não encontrado."
        echo "Por favor, crie o arquivo secrets_cerebro.py manualmente com suas chaves de API."
        exit 1
    fi
fi

# Aplica correções específicas para o Termux
echo "Aplicando correções para o Termux..."

# Verifica se o ffmpeg está instalado corretamente
if command -v ffmpeg >/dev/null 2>&1; then
    echo "FFmpeg está instalado."
    ffmpeg -version | head -n 1
else
    echo "AVISO: FFmpeg não encontrado. Tentando instalar novamente..."
    pkg install -y ffmpeg
    if command -v ffmpeg >/dev/null 2>&1; then
        echo "FFmpeg instalado com sucesso."
    else
        echo "ERRO: Falha ao instalar FFmpeg. A conversão de áudio pode não funcionar."
    fi
fi

# Verifica se o comando file está instalado corretamente
if command -v file >/dev/null 2>&1; then
    echo "Comando 'file' está instalado."
    file --version | head -n 1
else
    echo "AVISO: Comando 'file' não encontrado. Tentando instalar novamente..."
    pkg install -y file
    if command -v file >/dev/null 2>&1; then
        echo "Comando 'file' instalado com sucesso."
    else
        echo "ERRO: Falha ao instalar o comando 'file'. A verificação de formato de arquivos pode não funcionar."
    fi
fi

# Cria diretório temporário se não existir
if [ ! -d "$HOME/tmp" ]; then
    echo "Criando diretório temporário em $HOME/tmp"
    mkdir -p "$HOME/tmp"
    echo "export TMPDIR=$HOME/tmp" >> "$HOME/.bashrc"
    export TMPDIR=$HOME/tmp
fi

# Executa o script de correção de áudio para o Termux
python3 scripts/fix_termux_audio.py

echo "Configuração concluída!"
echo "Para iniciar o bot, execute: ./scripts/run_background.sh"
echo "Para verificar o status, execute: ./scripts/status_bot_termux.sh"
