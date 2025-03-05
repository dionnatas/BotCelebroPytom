#!/usr/bin/env python3
"""
Script para verificar e corrigir a versão da API OpenAI.
"""

import os
import sys
import subprocess
import logging

# Configuração de logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def check_openai_version():
    """Verifica a versão da API OpenAI instalada."""
    try:
        import openai
        try:
            version = openai.__version__
            logger.info(f"Versão da API OpenAI instalada: {version}")
            return version
        except AttributeError:
            logger.info("Não foi possível determinar a versão da API OpenAI")
            return None
    except ImportError:
        logger.info("API OpenAI não instalada")
        return None

def install_openai_version(version="0.28.0"):
    """Instala a versão especificada da API OpenAI."""
    logger.info(f"Instalando OpenAI versão {version}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", f"openai=={version}"])
        logger.info(f"OpenAI versão {version} instalada com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao instalar OpenAI versão {version}: {e}")
        return False

def main():
    """Função principal."""
    print("Verificando a versão da API OpenAI...")
    
    current_version = check_openai_version()
    
    if current_version is None:
        print("Instalando a API OpenAI versão 0.28.0...")
        install_openai_version()
    elif current_version != "0.28.0":
        print(f"Versão atual: {current_version}")
        choice = input("A versão recomendada é 0.28.0. Deseja instalar esta versão? (s/n): ")
        if choice.lower() in ["s", "sim", "y", "yes"]:
            # Desinstala a versão atual
            subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", "openai"])
            # Instala a versão recomendada
            install_openai_version()
        else:
            print("Mantendo a versão atual.")
    else:
        print("Você já tem a versão recomendada (0.28.0) instalada.")
    
    # Verifica novamente após a instalação
    check_openai_version()
    
    print("\nVerificação concluída!")

if __name__ == "__main__":
    main()
