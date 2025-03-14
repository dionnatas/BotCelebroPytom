#!/bin/bash
# Script para executar o bot Cerebro em segundo plano

# Diretório do projeto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# Cria diretórios de logs e PID se não existirem
mkdir -p "$PROJECT_DIR/var/logs" "$PROJECT_DIR/var/run"

# Verifica se o bot já está em execução
PID_FILE="$PROJECT_DIR/var/run/cerebro.pid"
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null; then
        echo "O bot já está em execução com PID $PID"
        echo "Use scripts/stop_bot.sh para parar o bot antes de iniciar novamente."
        exit 1
    else
        echo "Arquivo PID encontrado, mas o processo não está em execução. Removendo arquivo PID antigo."
        rm "$PID_FILE"
    fi
fi

echo "Iniciando o bot Cerebro em segundo plano..."

# Define os caminhos para logs e PID
LOG_FILE="$PROJECT_DIR/var/logs/cerebro.log"

# Verifica se o ambiente virtual existe
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo "Ambiente virtual não encontrado. Criando..."
    python3 -m venv venv
    echo "Ambiente virtual criado. Instalando dependências..."
    source "$PROJECT_DIR/venv/bin/activate"
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "Dependências instaladas com sucesso."
fi

# Ativa o ambiente virtual e executa o bot em segundo plano
source "$PROJECT_DIR/venv/bin/activate" && nohup "$PROJECT_DIR/venv/bin/python" main.py > "$LOG_FILE" 2>&1 &

# Salva o PID
echo $! > "$PID_FILE"
echo "Bot iniciado com PID $(cat "$PID_FILE")"
echo "Logs sendo salvos em $LOG_FILE"
echo "Use scripts/status_bot.sh para verificar o status do bot"
echo "Use scripts/stop_bot.sh para parar o bot"
