#!/bin/bash
# Script para executar o bot no Termux

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

# Executa o bot
echo "Iniciando o bot Cerebro..."
python cerebro.py
