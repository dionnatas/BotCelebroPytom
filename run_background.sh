#!/bin/bash
# Script para executar o bot em segundo plano no Termux

# Verifica se o arquivo cerebro.py existe
if [ ! -f "cerebro.py" ]; then
    echo "Erro: Arquivo cerebro.py não encontrado."
    exit 1
fi

# Verifica se o arquivo secrets_cerebro.py existe
if [ ! -f "secrets_cerebro.py" ]; then
    echo "Erro: Arquivo secrets_cerebro.py não encontrado."
    echo "Por favor, crie o arquivo com suas chaves de API."
    exit 1
fi

# Verifica se já existe uma instância do bot rodando
BOT_RUNNING=0
BOT_PID=""

# Cria arquivo PID se não existir
if [ ! -f "cerebro.pid" ]; then
    touch cerebro.pid
fi

# Lê o PID do arquivo
STORED_PID=$(cat cerebro.pid)

# Verifica se o PID existe e se o processo está rodando
if [ ! -z "$STORED_PID" ]; then
    if ps -p "$STORED_PID" > /dev/null; then
        BOT_RUNNING=1
        BOT_PID="$STORED_PID"
    fi
fi

# Verifica se há algum processo python rodando cerebro.py
PYTHON_PIDS=$(ps -ef | grep "python.*cerebro\.py" | grep -v grep | awk '{print $2}')
if [ ! -z "$PYTHON_PIDS" ]; then
    for pid in $PYTHON_PIDS; do
        if [ "$pid" != "$STORED_PID" ]; then
            BOT_RUNNING=1
            BOT_PID="$pid"
            # Atualiza o arquivo PID
            echo "$pid" > cerebro.pid
            break
        fi
    done
fi

# Se o bot já estiver rodando, exibe uma mensagem e sai
if [ "$BOT_RUNNING" -eq 1 ]; then
    echo "O bot Cerebro já está rodando com PID: $BOT_PID"
    echo "Para verificar os logs, use o comando: cat cerebro.log"
    echo "Para parar o bot, use o comando: ./stop_bot.sh ou kill $BOT_PID"
    exit 0
fi

# Aplica correções para o ambiente Termux
echo "Aplicando correções para o ambiente Termux..."
python fix_termux.py

# Executa o bot em segundo plano
echo "Iniciando o bot Cerebro em segundo plano..."
nohup python cerebro.py > cerebro.log 2>&1 &

# Salva o PID do processo
NEW_PID=$!
echo "$NEW_PID" > cerebro.pid

# Mostra o PID do processo
echo "Bot iniciado com PID: $NEW_PID"
echo "Para verificar os logs, use o comando: cat cerebro.log"
echo "Para parar o bot, use o comando: ./stop_bot.sh ou kill $NEW_PID"
