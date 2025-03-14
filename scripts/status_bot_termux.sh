#!/bin/bash
# Script para verificar o status do bot Cerebro (versão para Termux)

# Diretório do projeto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# Função para formatar tamanho
format_size() {
    local size=$1
    local units=("B" "K" "M" "G")
    local unit=0
    
    while [ $size -ge 1024 ] && [ $unit -lt 3 ]; do
        size=$(($size / 1024))
        unit=$(($unit + 1))
    done
    
    echo "$size${units[$unit]}"
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
            echo "PID: $pid - $(ps -p $pid -o cmd= | head -c 50)..."
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
echo "Tempo de execução: $(ps -o etime= -p $PID | tail -1 | xargs)"

# Verifica uso de CPU e memória (versão Termux)
if command -v ps >/dev/null 2>&1; then
    # No Termux, usamos ps para obter informações de CPU e memória
    CPU=$(ps -p $PID -o %cpu | tail -1 | xargs)
    MEM=$(ps -p $PID -o %mem | tail -1 | xargs)
    echo "Uso de CPU: $CPU%"
    echo "Uso de memória: $MEM%"
fi

# Verifica informações sobre o arquivo de log
if [ -f "$LOG_FILE" ]; then
    LOG_SIZE=$(stat -c "%s" "$LOG_FILE" 2>/dev/null || stat "$LOG_FILE" | grep Size | awk '{print $2}')
    LOG_SIZE_FORMATTED=$(format_size $LOG_SIZE)
    LOG_LINES=$(wc -l < "$LOG_FILE")
    LOG_MODIFIED=$(date -r "$LOG_FILE" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || ls -l --time-style="+%Y-%m-%d %H:%M:%S" "$LOG_FILE" | awk '{print $6, $7}')
    echo -e "\nArquivo de log:"
    echo "Caminho: $LOG_FILE"
    echo "Tamanho: $LOG_SIZE_FORMATTED"
    echo "Linhas: $LOG_LINES"
    echo "Modificado: $LOG_MODIFIED"
    echo -e "\nÚltimas 5 linhas do log:"
    tail -n 5 "$LOG_FILE"
else
    echo -e "\nArquivo de log não encontrado: $LOG_FILE"
fi

# Verifica se há arquivos de banco de dados
DB_PATH="$PROJECT_DIR/var/db/cerebro.db"
if [ -f "$DB_PATH" ]; then
    DB_SIZE=$(stat -c "%s" "$DB_PATH" 2>/dev/null || stat "$DB_PATH" | grep Size | awk '{print $2}')
    DB_SIZE_FORMATTED=$(format_size $DB_SIZE)
    DB_MODIFIED=$(date -r "$DB_PATH" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || ls -l --time-style="+%Y-%m-%d %H:%M:%S" "$DB_PATH" | awk '{print $6, $7}')
    echo -e "\nBanco de dados:"
    echo "Caminho: $DB_PATH"
    echo "Tamanho: $DB_SIZE_FORMATTED"
    echo "Modificado: $DB_MODIFIED"
else
    echo -e "\nBanco de dados não encontrado: $DB_PATH"
fi

echo -e "\nUse scripts/stop_bot.sh para parar o bot"
echo "Use scripts/restart_bot.sh para reiniciar o bot"
