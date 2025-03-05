"""
Script para atualizar o código antigo para a nova estrutura.
"""
import logging
import os
import shutil
import sys
from datetime import datetime

# Adiciona o diretório raiz ao path para importações relativas
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.settings import configure_logging

# Configura o logging
configure_logging()
logger = logging.getLogger(__name__)

def criar_backup():
    """
    Cria um backup dos arquivos originais antes de modificá-los.
    
    Returns:
        bool: True se o backup foi criado com sucesso, False caso contrário
    """
    try:
        # Diretório raiz do projeto
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Diretório de backup
        backup_dir = os.path.join(root_dir, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(backup_dir, exist_ok=True)
        
        # Arquivos para fazer backup
        arquivos = ["cerebro.py", "prompts.py", "validar_transcricao.py"]
        
        # Copia os arquivos para o diretório de backup
        for arquivo in arquivos:
            arquivo_path = os.path.join(root_dir, arquivo)
            if os.path.exists(arquivo_path):
                shutil.copy2(arquivo_path, os.path.join(backup_dir, arquivo))
                logger.info(f"Backup criado para: {arquivo}")
        
        logger.info(f"Backup concluído em: {backup_dir}")
        return True
    
    except Exception as e:
        logger.error(f"Erro ao criar backup: {e}")
        return False

def criar_arquivo_compatibilidade():
    """
    Cria um arquivo de compatibilidade para o cerebro.py antigo.
    
    Returns:
        bool: True se o arquivo foi criado com sucesso, False caso contrário
    """
    try:
        # Diretório raiz do projeto
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Caminho do arquivo cerebro.py
        cerebro_path = os.path.join(root_dir, "cerebro.py")
        
        # Conteúdo do arquivo de compatibilidade
        conteudo = '''"""
Arquivo de compatibilidade para a versão antiga do Cerebro.
Este arquivo permite que o código antigo continue funcionando,
redirecionando para a nova estrutura.
"""
import logging
import os
import sys

# Adiciona o diretório raiz ao path para importações relativas
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configura o logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """
    Função principal para iniciar o bot.
    """
    logger.info("Iniciando o bot Cerebro (modo de compatibilidade)...")
    logger.info("Redirecionando para a nova estrutura...")
    
    try:
        # Importa o módulo principal da nova estrutura
        from main import main as new_main
        
        # Executa a função principal da nova estrutura
        new_main()
    except Exception as e:
        logger.error(f"Erro ao iniciar o bot: {e}", exc_info=True)
        print(f"Erro ao iniciar o bot: {e}")
        print("Verifique os logs para mais detalhes.")

if __name__ == "__main__":
    main()
'''
        
        # Cria o arquivo de compatibilidade
        with open(cerebro_path, "w") as f:
            f.write(conteudo)
        
        logger.info(f"Arquivo de compatibilidade criado: {cerebro_path}")
        return True
    
    except Exception as e:
        logger.error(f"Erro ao criar arquivo de compatibilidade: {e}")
        return False

def atualizar_projeto():
    """
    Atualiza o projeto para a nova estrutura.
    
    Returns:
        bool: True se a atualização foi concluída com sucesso, False caso contrário
    """
    try:
        # Cria backup dos arquivos originais
        if not criar_backup():
            logger.error("Falha ao criar backup. Interrompendo atualização.")
            return False
        
        # Cria arquivo de compatibilidade
        if not criar_arquivo_compatibilidade():
            logger.error("Falha ao criar arquivo de compatibilidade. Interrompendo atualização.")
            return False
        
        # Executa a migração do banco de dados
        from scripts.migrate_db import migrar_banco_dados
        if not migrar_banco_dados():
            logger.warning("Falha na migração do banco de dados. Continuando com a atualização...")
        
        logger.info("Atualização concluída com sucesso!")
        return True
    
    except Exception as e:
        logger.error(f"Erro durante a atualização do projeto: {e}")
        return False

if __name__ == "__main__":
    logger.info("Iniciando atualização do projeto...")
    
    if atualizar_projeto():
        logger.info("Atualização do projeto concluída com sucesso!")
        print("Atualização do projeto concluída com sucesso!")
        print("O código antigo foi preservado em um diretório de backup.")
        print("O arquivo cerebro.py foi atualizado para redirecionar para a nova estrutura.")
    else:
        logger.error("Falha na atualização do projeto")
        print("Falha na atualização do projeto. Verifique os logs para mais detalhes.")
