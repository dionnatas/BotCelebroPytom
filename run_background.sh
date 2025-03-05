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

# Aplica correções para o ambiente Termux
echo "Aplicando correções para o ambiente Termux..."
python fix_termux.py

# Executa o bot em segundo plano
echo "Iniciando o bot Cerebro em segundo plano..."
nohup python cerebro.py > cerebro.log 2>&1 &

# Mostra o PID do processo
echo "Bot iniciado com PID: $!"
echo "Para verificar os logs, use o comando: cat cerebro.log"
echo "Para parar o bot, use o comando: kill $!"
