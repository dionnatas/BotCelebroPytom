#!/bin/bash
# Script para verificar o status do bot Cerebro

BOT_RUNNING=0
BOT_PID=""

# Verifica se o arquivo PID existe
if [ -f "cerebro.pid" ]; then
    # Lê o PID do arquivo
    STORED_PID=$(cat cerebro.pid)
    
    # Verifica se o PID existe e se o processo está rodando
    if [ ! -z "$STORED_PID" ]; then
        if ps -p "$STORED_PID" > /dev/null; then
            BOT_RUNNING=1
            BOT_PID="$STORED_PID"
            echo "O bot Cerebro está rodando com PID: $BOT_PID"
            
            # Mostra há quanto tempo o processo está rodando
            if command -v ps > /dev/null; then
                PROCESS_START=$(ps -p "$BOT_PID" -o lstart= 2>/dev/null)
                if [ ! -z "$PROCESS_START" ]; then
                    echo "Iniciado em: $PROCESS_START"
                fi
                
                # Mostra o uso de CPU e memória
                echo "Uso de recursos:"
                ps -p "$BOT_PID" -o %cpu,%mem 2>/dev/null
            fi
            
            # Verifica se o arquivo de log existe e mostra as últimas linhas
            if [ -f "cerebro.log" ]; then
                echo -e "\nÚltimas 5 linhas do log:"
                tail -n 5 cerebro.log
            else
                echo "Arquivo de log não encontrado."
            fi
        else
            echo "O bot não está rodando com o PID $STORED_PID (PID inválido)."
            BOT_RUNNING=0
        fi
    else
        echo "Arquivo PID está vazio."
    fi
else
    echo "Arquivo cerebro.pid não encontrado."
fi

# Se não encontrou pelo arquivo PID, procura por processos python rodando cerebro.py
if [ "$BOT_RUNNING" -eq 0 ]; then
    PYTHON_PIDS=$(ps -ef | grep "python.*cerebro\.py" | grep -v grep | awk '{print $2}')
    if [ ! -z "$PYTHON_PIDS" ]; then
        echo "Encontrados processos do bot rodando:"
        for pid in $PYTHON_PIDS; do
            echo "PID: $pid"
            BOT_RUNNING=1
            BOT_PID="$pid"
            
            # Mostra há quanto tempo o processo está rodando
            if command -v ps > /dev/null; then
                PROCESS_START=$(ps -p "$pid" -o lstart= 2>/dev/null)
                if [ ! -z "$PROCESS_START" ]; then
                    echo "Iniciado em: $PROCESS_START"
                fi
                
                # Mostra o uso de CPU e memória
                echo "Uso de recursos:"
                ps -p "$pid" -o %cpu,%mem 2>/dev/null
            fi
        done
        
        # Atualiza o arquivo PID com o primeiro PID encontrado
        echo "$BOT_PID" > cerebro.pid
        echo "Arquivo cerebro.pid atualizado com o PID: $BOT_PID"
        
        # Verifica se o arquivo de log existe e mostra as últimas linhas
        if [ -f "cerebro.log" ]; then
            echo -e "\nÚltimas 5 linhas do log:"
            tail -n 5 cerebro.log
        else
            echo "Arquivo de log não encontrado."
        fi
    else
        echo "O bot Cerebro não está rodando."
    fi
fi

# Exibe comandos úteis
if [ "$BOT_RUNNING" -eq 1 ]; then
    echo -e "\nComandos úteis:"
    echo "- Para ver o log completo: cat cerebro.log"
    echo "- Para monitorar o log em tempo real: tail -f cerebro.log"
    echo "- Para parar o bot: ./stop_bot.sh"
else
    echo -e "\nPara iniciar o bot, use: ./run_background.sh"
fi
