#!/bin/bash
# Script para atualizar o Bot Cerebro a partir do GitHub
# Autor: Dionnatas
# Data: 14/03/2025

# Diretório do projeto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "===== Atualizando Bot Cerebro a partir do GitHub ====="
echo "Diretório do projeto: $PROJECT_DIR"
echo

# Verificar se há alterações locais não commitadas
if ! git diff-index --quiet HEAD --; then
    echo "AVISO: Existem alterações locais não commitadas."
    echo "Você pode perder essas alterações se continuar."
    read -p "Deseja continuar mesmo assim? (s/n): " resposta
    if [[ "$resposta" != "s" && "$resposta" != "S" ]]; then
        echo "Atualização cancelada."
        exit 1
    fi
    echo "Continuando com a atualização..."
    echo
fi

# Backup do banco de dados
echo "Criando backup do banco de dados..."
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
mkdir -p "$PROJECT_DIR/backups"
if [ -f "$PROJECT_DIR/var/db/cerebro.db" ]; then
    cp "$PROJECT_DIR/var/db/cerebro.db" "$PROJECT_DIR/backups/cerebro_$TIMESTAMP.db"
    echo "Backup criado em: backups/cerebro_$TIMESTAMP.db"
else
    echo "Banco de dados local não encontrado, pulando backup."
fi
echo

# Atualizar a partir do GitHub
echo "Baixando atualizações do GitHub..."
git fetch origin
git reset --hard origin/main
echo

# Atualizar dependências
echo "Atualizando dependências..."
if [ -f "$PROJECT_DIR/venv/bin/activate" ]; then
    source "$PROJECT_DIR/venv/bin/activate"
    pip install -r requirements.txt
    echo "Dependências atualizadas."
else
    echo "Ambiente virtual não encontrado em venv/."
    echo "Instalando dependências globalmente (não recomendado)..."
    pip install -r requirements.txt
fi
echo

# Verificar se o bot está em execução
if [ -f "$PROJECT_DIR/var/run/cerebro.pid" ]; then
    echo "Bot está em execução. Reiniciando..."
    "$PROJECT_DIR/scripts/restart_bot.sh"
else
    echo "Bot não está em execução. Iniciando..."
    "$PROJECT_DIR/scripts/run_background.sh"
fi
echo

echo "===== Atualização concluída! ====="
echo "Use scripts/status_bot.sh para verificar o status do bot."
