#!/usr/bin/env python3
"""
Script para corrigir problemas de compatibilidade no ambiente Termux.
"""

import os
import sys
import re
import subprocess

def fix_parsemode_issue():
    """Corrige o problema de importação do ParseMode no arquivo cerebro.py."""
    file_path = "cerebro.py"
    
    if not os.path.exists(file_path):
        print(f"Erro: Arquivo {file_path} não encontrado.")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Verifica se já aplicamos a correção
    if "try:\n    from telegram import ParseMode" in content:
        print("Correção do ParseMode já aplicada. Nenhuma ação necessária.")
        return True
    
    # Substitui a importação do ParseMode
    pattern = r"from telegram import Update, ParseMode"
    replacement = """from telegram import Update

# Compatibilidade com diferentes versões da biblioteca python-telegram-bot
try:
    from telegram import ParseMode
except ImportError:
    # Para versões mais recentes da biblioteca
    from telegram.constants import ParseMode
except ImportError:
    # Fallback se não conseguir importar de nenhum lugar
    class ParseMode:
        HTML = "HTML"
        MARKDOWN = "Markdown"
        MARKDOWN_V2 = "MarkdownV2"
"""
    
    if pattern in content:
        new_content = content.replace(pattern, replacement)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        print("Correção do ParseMode aplicada com sucesso!")
        return True
    else:
        print("Padrão de importação não encontrado. Nenhuma alteração feita.")
        return False

def main():
    """Função principal."""
    print("Iniciando correções para o ambiente Termux...")
    
    # Corrige o problema do ParseMode
    fix_parsemode_issue()
    
    print("\nVerificando dependências...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError:
        print("Erro ao instalar dependências. Verifique se o arquivo requirements.txt existe.")
    
    print("\nCorreções concluídas! Agora você pode executar o bot com o comando:")
    print("python cerebro.py")

if __name__ == "__main__":
    main()
