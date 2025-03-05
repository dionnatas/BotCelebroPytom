#!/bin/bash
# Script para migrar arquivos da raiz para os novos diretórios

# Diretório do projeto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# Cria diretórios se não existirem
mkdir -p "$PROJECT_DIR/var/db" "$PROJECT_DIR/var/logs" "$PROJECT_DIR/var/run" "$PROJECT_DIR/scripts/legacy"

echo "Migrando arquivos para os novos diretórios..."

# Migra arquivos de banco de dados
if [ -f "$PROJECT_DIR/cerebro.db" ]; then
    echo "Movendo cerebro.db para var/db/"
    mv "$PROJECT_DIR/cerebro.db" "$PROJECT_DIR/var/db/"
fi

if [ -f "$PROJECT_DIR/cerebro.db.bak" ]; then
    echo "Movendo cerebro.db.bak para var/db/"
    mv "$PROJECT_DIR/cerebro.db.bak" "$PROJECT_DIR/var/db/"
fi

# Migra arquivos de log
if [ -f "$PROJECT_DIR/cerebro.log" ]; then
    echo "Movendo cerebro.log para var/logs/"
    mv "$PROJECT_DIR/cerebro.log" "$PROJECT_DIR/var/logs/"
fi

# Migra arquivo PID
if [ -f "$PROJECT_DIR/cerebro.pid" ]; then
    echo "Movendo cerebro.pid para var/run/"
    mv "$PROJECT_DIR/cerebro.pid" "$PROJECT_DIR/var/run/"
fi

# Move scripts antigos para scripts/legacy
echo "Movendo scripts antigos para scripts/legacy/"
for file in check_openai.py check_telegram_bot.py download_file.py fix_termux.py handle_message_fixed.py validar_transcricao.py run_termux.sh; do
    if [ -f "$PROJECT_DIR/$file" ]; then
        echo "Movendo $file para scripts/legacy/"
        mv "$PROJECT_DIR/$file" "$PROJECT_DIR/scripts/legacy/"
    fi
done

# Move arquivos de compatibilidade para scripts/legacy
echo "Movendo arquivos de compatibilidade para scripts/legacy/"
for file in cerebro.py prompts.py; do
    if [ -f "$PROJECT_DIR/$file" ]; then
        echo "Movendo $file para scripts/legacy/"
        mv "$PROJECT_DIR/$file" "$PROJECT_DIR/scripts/legacy/"
    fi
done

# Move scripts shell antigos para scripts/legacy
echo "Movendo scripts shell antigos para scripts/legacy/"
for file in run_background.sh restart_bot.sh status_bot.sh stop_bot.sh setup_termux.sh; do
    if [ -f "$PROJECT_DIR/$file" ] && [ -f "$PROJECT_DIR/scripts/$file" ]; then
        echo "Movendo $file para scripts/legacy/"
        mv "$PROJECT_DIR/$file" "$PROJECT_DIR/scripts/legacy/"
    fi
done

echo "Migração concluída!"
echo "Os arquivos foram movidos para os seguintes diretórios:"
echo "- Banco de dados: var/db/"
echo "- Logs: var/logs/"
echo "- PID: var/run/"
echo "- Scripts antigos: scripts/legacy/"
