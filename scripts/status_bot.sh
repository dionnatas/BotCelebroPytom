#!/bin/bash
# Script para verificar o status do bot Cerebro

# Diretório do projeto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# Função para formatar tamanho
format_size() {
    local size=$1
    local units=("B" "KB" "MB" "GB")
    local unit=0
    
    while [ $size -ge 1024 ] && [ $unit -lt 3 ]; do
        size=$(($size / 1024))
        unit=$(($unit + 1))
    done
    
    echo "$size ${units[$unit]}"
}

# Define os caminhos para logs e PID
PID_FILE="$PROJECT_DIR/var/run/cerebro.pid"
LOG_FILE="$PROJECT_DIR/var/logs/cerebro.log"

# Verifica se o arquivo PID existe
if [ ! -f "$PID_FILE" ]; then
    echo "Arquivo PID não encontrado. O bot não parece estar em execução."
    
    # Verifica se há algum processo python executando main.py
    PIDS=$(pgrep -f "python.*main.py" || echo "")
    if [ -n "$PIDS" ]; then
        echo "No entanto, encontrei processos relacionados ao bot:"
        for pid in $PIDS; do
            echo "PID: $pid - $(ps -p $pid -o command= | head -c 50)..."
        done
        echo "Use 'kill $PIDS' para encerrar esses processos."
    fi
    
    exit 1
fi

# Lê o PID
PID=$(cat "$PID_FILE")

# Verifica se o processo está em execução
if ! ps -p $PID > /dev/null; then
    echo "O processo com PID $PID não está em execução, mas o arquivo PID existe."
    echo "O bot pode ter sido encerrado inesperadamente."
    echo "Removendo arquivo PID antigo..."
    rm "$PID_FILE"
    exit 1
fi

echo "Bot Cerebro está em execução"
echo "PID: $PID"
echo "Tempo de execução: $(ps -p $PID -o etime= | xargs)"

# Verifica uso de CPU e memória
if command -v top >/dev/null 2>&1; then
    CPU=$(top -l 1 -pid $PID -stats cpu | tail -1 | awk '{print $1}')
    MEM=$(top -l 1 -pid $PID -stats mem | tail -1 | awk '{print $1}')
    echo "Uso de CPU: $CPU%"
    echo "Uso de memória: $MEM%"
fi

# Verifica informações sobre o arquivo de log
if [ -f "$LOG_FILE" ]; then
    LOG_SIZE=$(du -h "$LOG_FILE" | cut -f1)
    LOG_LINES=$(wc -l < "$LOG_FILE")
    LOG_MODIFIED=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$LOG_FILE")
    echo "\nArquivo de log:"
    echo "Caminho: $LOG_FILE"
    echo "Tamanho: $LOG_SIZE"
    echo "Linhas: $LOG_LINES"
    echo "Modificado: $LOG_MODIFIED"
    echo "\nÚltimas 5 linhas do log:"
    tail -n 5 "$LOG_FILE"
else
    echo "\nArquivo de log não encontrado: $LOG_FILE"
fi

# Verifica se há arquivos de banco de dados
if [ -f "$PROJECT_DIR/var/db/cerebro.db" ]; then
    DB_SIZE=$(du -h "$PROJECT_DIR/var/db/cerebro.db" | cut -f1)
    DB_MODIFIED=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$PROJECT_DIR/var/db/cerebro.db")
    echo "\nBanco de dados:"
    echo "Caminho: $PROJECT_DIR/var/db/cerebro.db"
    echo "Tamanho: $DB_SIZE"
    echo "Modificado: $DB_MODIFIED"
else
    echo "\nBanco de dados não encontrado: $PROJECT_DIR/var/db/cerebro.db"
fi

echo -e "\nUse scripts/stop_bot.sh para parar o bot"
echo "Use scripts/restart_bot.sh para reiniciar o bot"
