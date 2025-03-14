#!/usr/bin/env python3
"""
Script para verificar a versão da biblioteca python-telegram-bot
e instalar a versão correta se necessário.
"""

import subprocess
import sys
import importlib.metadata as metadata

def get_installed_version(package_name):
    """Retorna a versão instalada de um pacote."""
    try:
        return metadata.version(package_name)
    except metadata.PackageNotFoundError:
        return None

def main():
    """Função principal."""
    package_name = "python-telegram-bot"
    required_version = "13.12"
    
    print(f"Verificando a versão do {package_name}...")
    
    installed_version = get_installed_version(package_name)
    
    if installed_version is None:
        print(f"{package_name} não está instalado. Instalando versão {required_version}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", f"{package_name}=={required_version}"])
        print(f"{package_name} {required_version} instalado com sucesso!")
    elif installed_version != required_version:
        print(f"Versão instalada: {installed_version}")
        print(f"Versão necessária: {required_version}")
        
        choice = input(f"Deseja desinstalar a versão atual e instalar a versão {required_version}? (s/n): ")
        
        if choice.lower() in ["s", "sim", "y", "yes"]:
            print(f"Desinstalando {package_name} {installed_version}...")
            subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", package_name])
            
            print(f"Instalando {package_name} {required_version}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", f"{package_name}=={required_version}"])
            
            print(f"{package_name} {required_version} instalado com sucesso!")
        else:
            print("Operação cancelada pelo usuário.")
    else:
        print(f"{package_name} {installed_version} já está instalado. Nenhuma ação necessária.")

if __name__ == "__main__":
    main()
