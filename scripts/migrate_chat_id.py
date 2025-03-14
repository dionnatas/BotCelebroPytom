#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para migrar o banco de dados, adicionando chat_id às ideias existentes.
"""

import os
import sys
import sqlite3
import logging
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Caminho para o banco de dados
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'var', 'db', 'cerebro.db')

# ID do chat padrão para ideias existentes (substitua pelo seu chat_id)
DEFAULT_CHAT_ID = 123456789  # Substitua pelo seu chat_id real

def migrar_chat_id():
    """
    Adiciona chat_id às ideias existentes no banco de dados.
    """
    try:
        # Verifica se o banco de dados existe
        if not os.path.exists(DB_PATH):
            logger.error(f"Banco de dados não encontrado em {DB_PATH}")
            return False
        
        # Faz backup do banco de dados
        backup_path = f"{DB_PATH}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        with open(DB_PATH, 'rb') as src, open(backup_path, 'wb') as dst:
            dst.write(src.read())
        logger.info(f"Backup do banco de dados criado em {backup_path}")
        
        # Conecta ao banco de dados
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verifica se a coluna chat_id já existe
        cursor.execute("PRAGMA table_info(ideias)")
        colunas = [coluna[1] for coluna in cursor.fetchall()]
        
        if 'chat_id' not in colunas:
            # Adiciona a coluna chat_id à tabela ideias
            cursor.execute("ALTER TABLE ideias ADD COLUMN chat_id INTEGER")
            logger.info("Coluna chat_id adicionada à tabela ideias")
        
        # Atualiza todas as ideias existentes com o chat_id padrão
        cursor.execute("UPDATE ideias SET chat_id = ? WHERE chat_id IS NULL", (DEFAULT_CHAT_ID,))
        logger.info(f"Atualizadas {cursor.rowcount} ideias com chat_id = {DEFAULT_CHAT_ID}")
        
        # Commit das alterações
        conn.commit()
        conn.close()
        
        logger.info("Migração concluída com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"Erro durante a migração: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    logger.info("Iniciando migração do banco de dados...")
    if migrar_chat_id():
        logger.info("Migração concluída com sucesso")
    else:
        logger.error("Falha na migração")
        sys.exit(1)
