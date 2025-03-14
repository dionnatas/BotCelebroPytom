#!/bin/bash
# Script para empacotar o Bot Cerebro para envio ao servidor
# Autor: Dionnatas
# Data: 14/03/2025

# Diretório do projeto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# Nome do arquivo de saída
OUTPUT_FILE="botcerebro.tar.gz"

echo "===== Empacotando Bot Cerebro para o servidor ====="
echo "Diretório do projeto: $PROJECT_DIR"
echo "Arquivo de saída: $OUTPUT_FILE"
echo

# Criar arquivo temporário com lista de arquivos a excluir
EXCLUDE_FILE=$(mktemp)
cat > "$EXCLUDE_FILE" << EOL
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.git/
.pytest_cache/
.DS_Store
EOL

echo "Arquivos e diretórios que serão excluídos:"
cat "$EXCLUDE_FILE"
echo

# Perguntar se deve preservar o arquivo secrets_cerebro.py no servidor
read -p "Preservar o arquivo secrets_cerebro.py no servidor? (s/n): " preserve_secrets
if [[ "$preserve_secrets" == "s" || "$preserve_secrets" == "S" ]]; then
    echo "secrets_cerebro.py" >> "$EXCLUDE_FILE"
    echo "O arquivo secrets_cerebro.py será preservado no servidor."
else
    echo "O arquivo secrets_cerebro.py será incluído no pacote."
fi
echo

# Perguntar se deve preservar o banco de dados no servidor
read -p "Preservar o banco de dados no servidor? (s/n): " preserve_db
if [[ "$preserve_db" == "s" || "$preserve_db" == "S" ]]; then
    echo "var/db/*.db" >> "$EXCLUDE_FILE"
    echo "var/db/*.db-journal" >> "$EXCLUDE_FILE"
    echo "Os arquivos de banco de dados serão preservados no servidor."
else
    echo "Os arquivos de banco de dados serão incluídos no pacote."
fi
echo

# Criar o arquivo tar.gz
echo "Criando arquivo $OUTPUT_FILE..."
tar -czf "$OUTPUT_FILE" -X "$EXCLUDE_FILE" -C "$PROJECT_DIR" .

# Remover arquivo temporário
rm "$EXCLUDE_FILE"

# Verificar tamanho do arquivo
SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
echo "Arquivo $OUTPUT_FILE criado com sucesso ($SIZE)."
echo

echo "===== Instruções para o servidor ====="
echo "1. Faça upload do arquivo para o servidor:"
echo "   scp $OUTPUT_FILE usuario@seu-servidor.com:/tmp/"
echo
echo "2. No servidor, extraia o arquivo:"
echo "   cd /caminho/para/BotCelebroPytom"
echo "   tar -xzf /tmp/$OUTPUT_FILE"
echo
echo "3. Configure o Git para atualizações automáticas:"
echo "   ./scripts/inicializar_git.sh"
echo "   ./scripts/setup_auto_update.sh"
echo
echo "4. Reinicie o bot:"
echo "   ./scripts/restart_bot.sh"
