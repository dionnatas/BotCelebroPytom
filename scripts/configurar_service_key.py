#!/usr/bin/env python3
"""
Script para configurar a chave de serviço do Supabase como variável de ambiente.
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    """Configura a chave de serviço do Supabase."""
    print("Configuração da chave de serviço do Supabase")
    print("-" * 50)
    print("Esta chave é necessária para operações administrativas como migração de dados.")
    print("Você pode encontrá-la no painel do Supabase em: Settings > API > Project API keys > service_role")
    print()
    
    # Solicitar a chave de serviço
    service_key = input("Cole sua chave de serviço do Supabase: ").strip()
    
    if not service_key:
        print("Nenhuma chave fornecida. Operação cancelada.")
        return
    
    # Verificar se a chave parece válida (formato básico de JWT)
    if not service_key.startswith("eyJ"):
        print("Aviso: A chave fornecida não parece ser um token JWT válido.")
        confirm = input("Deseja continuar mesmo assim? (s/n): ").lower()
        if confirm != 's':
            print("Operação cancelada.")
            return
    
    # Determinar o shell do usuário
    shell = os.environ.get('SHELL', '/bin/bash')
    shell_name = os.path.basename(shell)
    
    # Determinar o arquivo de perfil apropriado
    if shell_name == 'zsh':
        profile_file = os.path.expanduser('~/.zshrc')
    elif shell_name == 'bash':
        profile_file = os.path.expanduser('~/.bashrc')
    else:
        profile_file = os.path.expanduser(f'~/.{shell_name}rc')
    
    # Verificar se o arquivo de perfil existe
    if not os.path.exists(profile_file):
        print(f"Arquivo de perfil {profile_file} não encontrado.")
        alt_profile = input(f"Forneça o caminho para seu arquivo de perfil {shell_name} ou pressione Enter para criar um novo: ")
        if alt_profile:
            profile_file = os.path.expanduser(alt_profile)
        else:
            Path(profile_file).touch()
            print(f"Arquivo {profile_file} criado.")
    
    # Verificar se a variável já está definida no arquivo de perfil
    with open(profile_file, 'r') as f:
        content = f.read()
    
    if 'SUPABASE_SERVICE_KEY' in content:
        print("A variável SUPABASE_SERVICE_KEY já está definida no seu arquivo de perfil.")
        confirm = input("Deseja substituí-la? (s/n): ").lower()
        if confirm != 's':
            print("Operação cancelada.")
            return
    
    # Adicionar a variável ao arquivo de perfil
    with open(profile_file, 'a') as f:
        f.write(f'\n# Supabase Service Key para o bot Cerebro\nexport SUPABASE_SERVICE_KEY="{service_key}"\n')
    
    print(f"Chave de serviço adicionada ao arquivo {profile_file}")
    print("Para aplicar as alterações, execute:")
    print(f"source {profile_file}")
    
    # Perguntar se deseja aplicar imediatamente
    apply_now = input("Deseja aplicar as alterações agora? (s/n): ").lower()
    if apply_now == 's':
        try:
            # Definir a variável no ambiente atual
            os.environ['SUPABASE_SERVICE_KEY'] = service_key
            print("Variável de ambiente definida para a sessão atual.")
            
            # Tentar carregar o perfil (isso pode não funcionar dependendo do ambiente)
            try:
                subprocess.run(f"source {profile_file}", shell=True, executable=shell)
                print("Perfil carregado com sucesso.")
            except Exception as e:
                print(f"Não foi possível carregar o perfil automaticamente: {e}")
                print(f"Por favor, execute manualmente: source {profile_file}")
        except Exception as e:
            print(f"Erro ao aplicar as alterações: {e}")
    
    print("\nConfiguração concluída!")

if __name__ == "__main__":
    main()
