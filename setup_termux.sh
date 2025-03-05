#!/bin/bash
# Script para configurar o ambiente no Termux

echo "Atualizando pacotes..."
pkg update -y && pkg upgrade -y

echo "Instalando dependências necessárias..."
pkg install -y python clang libffi openssl

echo "Instalando pip e atualizando..."
pip install --upgrade pip

echo "Instalando dependências do projeto..."
pip install -r requirements.txt

echo "Verificando a versão da biblioteca python-telegram-bot..."
python check_telegram_bot.py

echo "Verificando a versão da API OpenAI..."
python check_openai.py

echo "Aplicando correções para o ambiente Termux..."
python fix_termux.py

echo "Verificando a configuração do arquivo secrets_cerebro.py..."
if [ ! -f "secrets_cerebro.py" ]; then
    echo "Arquivo secrets_cerebro.py não encontrado. Criando modelo..."
    cat > secrets_cerebro.py << EOL
# Substitua os valores abaixo pelas suas chaves de API
TELEGRAM_API_KEY = "sua_chave_telegram_aqui"
OPENAI_API_KEY = "sua_chave_openai_aqui"
MY_CHAT_ID = "seu_chat_id_aqui"  # ou ["id1", "id2"] para múltiplos IDs
EOL
    echo "Arquivo secrets_cerebro.py criado. Por favor, edite-o com suas chaves de API."
fi

echo "Configuração concluída!"
echo "Para executar o bot, use o comando: python cerebro.py"
echo "Para manter o bot rodando em segundo plano, use: nohup python cerebro.py > cerebro.log 2>&1 &"
