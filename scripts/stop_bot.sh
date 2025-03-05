#!/bin/bash
# Script para parar o bot Cerebro

# Diretório do projeto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# Define o caminho para o arquivo PID
PID_FILE="$PROJECT_DIR/var/run/cerebro.pid"

# Verifica se o arquivo PID existe
if [ ! -f "$PID_FILE" ]; then
    echo "Arquivo PID não encontrado. O bot não parece estar em execução."
    exit 1
fi

# Lê o PID
PID=$(cat "$PID_FILE")

# Verifica se o processo está em execução
if ! ps -p $PID > /dev/null; then
    echo "O processo com PID $PID não está em execução. Removendo arquivo PID."
    rm "$PID_FILE"
    exit 0
fi

echo "Parando o bot Cerebro (PID: $PID)..."

# Envia sinal SIGTERM para o processo
kill $PID

# Aguarda o processo terminar
echo "Aguardando o processo terminar..."
for i in {1..10}; do
    if ! ps -p $PID > /dev/null; then
        echo "Bot parado com sucesso."
        rm "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# Se o processo ainda estiver em execução após 10 segundos, força o encerramento
if ps -p $PID > /dev/null; then
    echo "O processo não terminou normalmente. Forçando encerramento..."
    kill -9 $PID
    
    # Verifica novamente
    if ! ps -p $PID > /dev/null; then
        echo "Bot encerrado forçadamente."
        rm "$PID_FILE"
        exit 0
    else
        echo "Não foi possível encerrar o bot. Verifique manualmente."
        exit 1
    fi
fi
