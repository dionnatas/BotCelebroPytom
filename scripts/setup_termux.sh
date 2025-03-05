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
pkg install -y python ffmpeg libffi openssl

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
python3 scripts/fix_audio.py

echo "Configuração concluída!"
echo "Para iniciar o bot, execute: ./scripts/run_background.sh"
echo "Para verificar o status, execute: ./scripts/status_bot.sh"
