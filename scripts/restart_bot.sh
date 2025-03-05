#!/bin/bash
# Script para reiniciar o bot Cerebro

# Diretório do projeto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "Reiniciando o bot Cerebro..."

# Define o caminho para o arquivo PID
PID_FILE="$PROJECT_DIR/var/run/cerebro.pid"

# Para o bot se estiver em execução
if [ -f "$PID_FILE" ]; then
    echo "Parando o bot atual..."
    ./scripts/stop_bot.sh
    
    # Aguarda um pouco para garantir que o processo foi encerrado
    sleep 2
fi

# Inicia o bot novamente
echo "Iniciando o bot novamente..."
./scripts/run_background.sh

echo "Bot reiniciado. Use scripts/status_bot.sh para verificar o status."
