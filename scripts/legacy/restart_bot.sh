#!/bin/bash
# Script para reiniciar o bot Cerebro

echo "Reiniciando o bot Cerebro..."

# Para o bot atual
echo "Parando o bot atual..."
./stop_bot.sh

# Espera um pouco para garantir que o processo foi encerrado
sleep 2

# Inicia o bot novamente
echo "Iniciando o bot novamente..."
./run_background.sh

# Verifica o status
echo "Verificando o status do bot..."
sleep 1
./status_bot.sh
