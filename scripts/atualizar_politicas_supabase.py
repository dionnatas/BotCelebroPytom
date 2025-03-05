#!/usr/bin/env python3
"""
Script para atualizar as políticas de segurança do Supabase.
Este script permite acesso total a todas as tabelas para qualquer usuário.
"""

import os
import sys
import logging
from pathlib import Path

# Adicionar o diretório raiz ao PYTHONPATH
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from supabase import create_client, Client

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurações do Supabase
SUPABASE_URL = "https://apeivlffyrsiqcnhskvo.supabase.co"

# Importar a chave de serviço do arquivo secrets_cerebro.py
try:
    from secrets_cerebro import SUPABASE_SERVICE_KEY
    logger.info("Chave de serviço obtida do arquivo secrets_cerebro.py")
except ImportError:
    logger.error("Não foi possível importar SUPABASE_SERVICE_KEY do arquivo secrets_cerebro.py")
    SUPABASE_SERVICE_KEY = None

def main():
    """Função principal para atualizar as políticas de segurança."""
    try:
        # Verificar se a chave de serviço foi configurada
        if SUPABASE_SERVICE_KEY == "COLOQUE_SUA_CHAVE_DE_SERVICO_AQUI":
            logger.error("⚠️ Você precisa configurar a chave de serviço no script antes de executá-lo.")
            logger.error("Abra o arquivo scripts/atualizar_politicas_supabase.py e substitua SUPABASE_SERVICE_KEY.")
            return False

        # Inicializar o cliente Supabase com a chave de serviço
        logger.info("Inicializando cliente Supabase com chave de serviço...")
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        
        # Ler o arquivo SQL
        sql_path = BASE_DIR / "scripts" / "atualizar_politicas_supabase.sql"
        with open(sql_path, "r") as f:
            sql = f.read()
        
        # Executar o SQL
        logger.info("Executando SQL para atualizar as políticas de segurança...")
        response = supabase.rpc("exec_sql", {"query": sql}).execute()
        
        # Verificar se houve erro
        if hasattr(response, 'error') and response.error:
            logger.error(f"Erro ao executar SQL: {response.error}")
            return False
        
        logger.info("✅ Políticas de segurança atualizadas com sucesso!")
        logger.info("Agora todos os usuários têm acesso total às tabelas.")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao atualizar políticas: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
