#!/bin/bash
# Script para inicializar o repositório Git no servidor
# Autor: Dionnatas
# Data: 14/03/2025

# Diretório do projeto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "===== Inicializando repositório Git para o Bot Cerebro ====="
echo "Diretório do projeto: $PROJECT_DIR"
echo

# Verificar se já é um repositório Git
if [ -d "$PROJECT_DIR/.git" ]; then
    echo "Este diretório já é um repositório Git."
    echo "Configuração atual:"
    git remote -v
    
    read -p "Deseja reconfigurá-lo? (s/n): " resposta
    if [[ "$resposta" != "s" && "$resposta" != "S" ]]; then
        echo "Operação cancelada."
        exit 0
    fi
    
    # Remover configuração Git existente
    echo "Removendo configuração Git existente..."
    rm -rf .git
    echo
fi

# Inicializar repositório Git
echo "Inicializando repositório Git..."
git init

# Configurar usuário e email (opcional)
read -p "Deseja configurar usuário e email Git? (s/n): " config_user
if [[ "$config_user" == "s" || "$config_user" == "S" ]]; then
    read -p "Digite seu nome de usuário Git: " git_user
    read -p "Digite seu email Git: " git_email
    
    git config user.name "$git_user"
    git config user.email "$git_email"
    echo "Usuário Git configurado."
    echo
fi

# Adicionar remote para o GitHub
echo "Configurando remote para o GitHub..."
git remote add origin https://github.com/dionnatas/BotCelebroPytom.git
echo "Remote 'origin' configurado."
echo

# Criar .gitignore se não existir
if [ ! -f "$PROJECT_DIR/.gitignore" ]; then
    echo "Criando arquivo .gitignore..."
    cat > "$PROJECT_DIR/.gitignore" << EOL
# Arquivos de ambiente virtual
venv/
env/
ENV/

# Arquivos de configuração com dados sensíveis
secrets_cerebro.py

# Arquivos de cache
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/

# Logs e bancos de dados
*.log
var/db/*.db
var/db/*.db-journal
var/log/*
var/run/*
!var/db/.gitkeep
!var/log/.gitkeep
!var/run/.gitkeep

# Arquivos temporários
.DS_Store
.idea/
.vscode/
*.swp
*.swo
EOL
    echo "Arquivo .gitignore criado."
    echo
fi

# Criar diretórios necessários
mkdir -p var/db var/log var/run
touch var/db/.gitkeep var/log/.gitkeep var/run/.gitkeep

# Adicionar todos os arquivos
echo "Adicionando arquivos ao repositório..."
git add .

# Fazer commit inicial
echo "Realizando commit inicial..."
git commit -m "Initial commit"

# Configurar branch main
echo "Configurando branch main..."
git branch -M main

echo
echo "===== Repositório Git inicializado com sucesso! ====="
echo
echo "Para atualizar o código a partir do GitHub, execute:"
echo "./scripts/update_from_github.sh"
echo
echo "Para configurar atualizações automáticas, execute:"
echo "./scripts/setup_auto_update.sh"
