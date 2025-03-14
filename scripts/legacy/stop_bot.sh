#!/bin/bash
# Script para parar o bot Cerebro

# Verifica se o arquivo PID existe
if [ ! -f "cerebro.pid" ]; then
    echo "Arquivo cerebro.pid não encontrado. O bot não parece estar rodando."
    
    # Verifica se há algum processo python rodando cerebro.py
    PYTHON_PIDS=$(ps -ef | grep "python.*cerebro\.py" | grep -v grep | awk '{print $2}')
    if [ ! -z "$PYTHON_PIDS" ]; then
        echo "Encontrados processos do bot rodando sem arquivo PID:"
        for pid in $PYTHON_PIDS; do
            echo "PID: $pid"
        done
        
        read -p "Deseja encerrar esses processos? (s/n): " CHOICE
        if [ "$CHOICE" = "s" ] || [ "$CHOICE" = "S" ]; then
            for pid in $PYTHON_PIDS; do
                echo "Encerrando processo $pid..."
                kill "$pid"
            done
            echo "Processos encerrados."
        else
            echo "Operação cancelada."
        fi
    else
        echo "Nenhum processo do bot encontrado."
    fi
    
    exit 0
fi

# Lê o PID do arquivo
BOT_PID=$(cat cerebro.pid)

if [ -z "$BOT_PID" ]; then
    echo "PID não encontrado no arquivo cerebro.pid."
    exit 1
fi

# Verifica se o processo está rodando
if ps -p "$BOT_PID" > /dev/null; then
    echo "Encerrando o bot Cerebro (PID: $BOT_PID)..."
    kill "$BOT_PID"
    
    # Espera um pouco para verificar se o processo foi encerrado
    sleep 2
    
    if ps -p "$BOT_PID" > /dev/null; then
        echo "O processo não foi encerrado. Tentando encerrar forçadamente..."
        kill -9 "$BOT_PID"
        sleep 1
    fi
    
    if ! ps -p "$BOT_PID" > /dev/null; then
        echo "Bot encerrado com sucesso."
    else
        echo "Não foi possível encerrar o bot. Tente manualmente com: kill -9 $BOT_PID"
    fi
else
    echo "O bot não está rodando com o PID $BOT_PID."
    
    # Verifica se há algum processo python rodando cerebro.py
    PYTHON_PIDS=$(ps -ef | grep "python.*cerebro\.py" | grep -v grep | awk '{print $2}')
    if [ ! -z "$PYTHON_PIDS" ]; then
        echo "Encontrados outros processos do bot rodando:"
        for pid in $PYTHON_PIDS; do
            echo "PID: $pid"
        done
        
        read -p "Deseja encerrar esses processos? (s/n): " CHOICE
        if [ "$CHOICE" = "s" ] || [ "$CHOICE" = "S" ]; then
            for pid in $PYTHON_PIDS; do
                echo "Encerrando processo $pid..."
                kill "$pid"
            done
            echo "Processos encerrados."
        else
            echo "Operação cancelada."
        fi
    else
        echo "Nenhum outro processo do bot encontrado."
    fi
fi

# Limpa o arquivo PID
echo "" > cerebro.pid
