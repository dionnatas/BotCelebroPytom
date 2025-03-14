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

def fix_regex_filter_issue():
    """Corrige o problema com Filters.regex e re.IGNORECASE."""
    file_path = "cerebro.py"
    
    if not os.path.exists(file_path):
        print(f"Erro: Arquivo {file_path} não encontrado.")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Verifica se já aplicamos a correção
    if "pattern = re.compile('^(sim|s|yes|y|não|nao|n|no)$', re.IGNORECASE)" in content:
        print("Correção do Filters.regex já aplicada. Nenhuma ação necessária.")
        return True
    
    # Procura pelo padrão do Filters.regex com re.IGNORECASE
    pattern = r"dispatcher\.add_handler\(MessageHandler\(Filters\.text & \(Filters\.regex\('\^\(sim\|s\|yes\|y\|não\|nao\|n\|no\)\$', re\.IGNORECASE\)\), handle_brainstorm_response\)\)"
    replacement = """    # Cria um padrão regex com flag de case insensitive
    pattern = re.compile('^(sim|s|yes|y|não|nao|n|no)$', re.IGNORECASE)
    dispatcher.add_handler(MessageHandler(Filters.text & (Filters.regex(pattern)), handle_brainstorm_response))"""
    
    # Padrão alternativo (sem re.IGNORECASE)
    alt_pattern = r"dispatcher\.add_handler\(MessageHandler\(Filters\.text & \(Filters\.regex\('\^\(sim\|s\|yes\|y\|não\|nao\|n\|no\)\$'\)\), handle_brainstorm_response\)\)"
    
    if pattern in content:
        new_content = content.replace(pattern, replacement)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print("Correção do Filters.regex aplicada com sucesso!")
        return True
    elif alt_pattern in content:
        new_content = content.replace(alt_pattern, replacement)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print("Correção do Filters.regex aplicada com sucesso!")
        return True
    else:
        # Se não encontrar o padrão exato, procura por qualquer linha com Filters.regex e handle_brainstorm_response
        import re as regex_module
        regex_pattern = regex_module.compile(r".*Filters\.regex.*handle_brainstorm_response.*")
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if regex_module.match(regex_pattern, line):
                # Substitui a linha inteira
                lines[i] = "    # Cria um padrão regex com flag de case insensitive"
                lines.insert(i+1, "    pattern = re.compile('^(sim|s|yes|y|não|nao|n|no)$', re.IGNORECASE)")
                lines.insert(i+2, "    dispatcher.add_handler(MessageHandler(Filters.text & (Filters.regex(pattern)), handle_brainstorm_response))")
                
                # Escreve o conteúdo modificado de volta para o arquivo
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write('\n'.join(lines))
                
                print("Correção do Filters.regex aplicada com sucesso (usando método alternativo)!")
                return True
        
        print("Padrão do Filters.regex não encontrado. Nenhuma alteração feita.")
        return False

def main():
    """Função principal."""
    print("Iniciando correções para o ambiente Termux...")
    
    # Corrige o problema do ParseMode
    fix_parsemode_issue()
    
    # Corrige o problema do Filters.regex
    fix_regex_filter_issue()
    
    print("\nVerificando dependências...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError:
        print("Erro ao instalar dependências. Verifique se o arquivo requirements.txt existe.")
    
    print("\nCorreções concluídas! Agora você pode executar o bot com o comando:")
    print("python cerebro.py")

if __name__ == "__main__":
    main()
