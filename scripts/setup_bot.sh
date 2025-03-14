#!/bin/bash

# Script de configuração para o Bot Cerebro
# Este script instala todas as dependências necessárias e configura o ambiente

echo "Iniciando configuração do Bot Cerebro..."

# Atualizar pacotes do sistema
echo "Atualizando pacotes do sistema..."
sudo apt-get update
sudo apt-get upgrade -y

# Instalar dependências do sistema
echo "Instalando dependências do sistema..."
sudo apt-get install -y python3-pip python3-venv ffmpeg

# Criar ambiente virtual
echo "Criando ambiente virtual Python..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependências Python com versões específicas para evitar conflitos
echo "Instalando dependências Python..."
pip install urllib3==1.26.15
pip install python-telegram-bot==13.12
pip install six
pip install supabase
pip install -r requirements.txt

# Verificar se o arquivo de segredos existe
if [ ! -f "secrets_cerebro.py" ]; then
    echo "AVISO: O arquivo secrets_cerebro.py não foi encontrado."
    echo "Criando arquivo de exemplo. Por favor, edite-o com suas chaves de API."
    
    cat > secrets_cerebro.py << EOF
# Arquivo de configuração de chaves de API
# Substitua os valores abaixo pelas suas chaves reais

TELEGRAM_API_KEY = "sua_chave_api_telegram"
OPENAI_API_KEY = "sua_chave_api_openai"

# Configuração do Supabase (opcional, se USE_SUPABASE=True em settings.py)
SUPABASE_URL = "sua_url_supabase"
SUPABASE_KEY = "sua_chave_supabase"
EOF

    echo "Arquivo secrets_cerebro.py criado. Por favor, edite-o antes de executar o bot."
fi

# Criar diretórios necessários
echo "Criando diretórios para logs e banco de dados..."
mkdir -p var/logs
mkdir -p var/db

# Configurar permissões para scripts
echo "Configurando permissões para scripts..."
chmod +x scripts/*.sh

echo "Configuração concluída com sucesso!"
echo "Para iniciar o bot, execute: ./scripts/run_background.sh"
echo "Para verificar o status do bot, execute: ./scripts/status_bot.sh"
echo "Para parar o bot, execute: ./scripts/stop_bot.sh"
