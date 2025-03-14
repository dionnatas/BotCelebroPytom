#!/bin/bash
# Script para configurar atualização automática do Bot Cerebro
# Autor: Dionnatas
# Data: 14/03/2025

# Diretório do projeto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Criar arquivo de log
LOGDIR="$PROJECT_DIR/var/log"
mkdir -p "$LOGDIR"

# Configurar cron para atualização diária às 3:00 da manhã
CRON_JOB="0 3 * * * $PROJECT_DIR/scripts/update_from_github.sh >> $LOGDIR/auto_update.log 2>&1"

# Verificar se o cron job já existe
EXISTING_CRON=$(crontab -l 2>/dev/null | grep -F "$PROJECT_DIR/scripts/update_from_github.sh")

if [ -z "$EXISTING_CRON" ]; then
    # Adicionar novo cron job
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "Atualização automática configurada para rodar diariamente às 3:00 da manhã."
    echo "Os logs serão salvos em: $LOGDIR/auto_update.log"
else
    echo "Atualização automática já está configurada."
    echo "Cron job atual: $EXISTING_CRON"
fi

echo
echo "Para verificar a configuração atual do cron, execute:"
echo "crontab -l"
echo
echo "Para editar manualmente a configuração do cron, execute:"
echo "crontab -e"
