"""
Script para migrar o banco de dados da versão antiga para a nova estrutura.
"""
import logging
import os
import sqlite3
import sys
from datetime import datetime

# Adiciona o diretório raiz ao path para importações relativas
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.settings import DB_PATH, configure_logging

# Configura o logging
configure_logging()
logger = logging.getLogger(__name__)

def migrar_banco_dados():
    """
    Migra os dados do banco de dados antigo (cerebro.db) para o novo.
    """
    # Caminho do banco de dados antigo
    db_antigo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cerebro.db")
    
    # Verifica se o banco de dados antigo existe
    if not os.path.exists(db_antigo_path):
        logger.warning(f"Banco de dados antigo não encontrado: {db_antigo_path}")
        return False
    
    # Caminho para o novo banco de dados
    db_novo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cerebro_novo.db")
    
    # Verifica se o novo banco já existe e o remove se necessário
    if os.path.exists(db_novo_path):
        try:
            os.remove(db_novo_path)
            logger.info(f"Banco de dados novo existente removido: {db_novo_path}")
        except Exception as e:
            logger.error(f"Erro ao remover banco de dados existente: {e}")
            return False
    
    try:
        # Conecta ao banco de dados antigo
        conn_antigo = sqlite3.connect(db_antigo_path)
        cursor_antigo = conn_antigo.cursor()
        
        # Verifica se as tabelas existem no banco antigo
        cursor_antigo.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ideias'")
        if not cursor_antigo.fetchone():
            logger.warning("Tabela 'ideias' não encontrada no banco de dados antigo")
            conn_antigo.close()
            return False
        
        # Conecta ao novo banco de dados
        conn_novo = sqlite3.connect(db_novo_path)
        cursor_novo = conn_novo.cursor()
        
        # Cria as tabelas no novo banco de dados se não existirem
        cursor_novo.execute('''
            CREATE TABLE IF NOT EXISTS ideias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                conteudo TEXT NOT NULL,
                resumo TEXT NOT NULL,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor_novo.execute('''
            CREATE TABLE IF NOT EXISTS brainstorms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ideia_id INTEGER NOT NULL,
                conteudo TEXT NOT NULL,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ideia_id) REFERENCES ideias (id)
            )
        ''')
        
        # Verifica o esquema da tabela ideias no banco antigo
        cursor_antigo.execute("PRAGMA table_info(ideias)")
        colunas = {info[1]: info[0] for info in cursor_antigo.fetchall()}
        logger.info(f"Colunas encontradas na tabela ideias: {list(colunas.keys())}")
        
        # Determina a consulta SQL com base nas colunas disponíveis
        if 'data' in colunas:
            # Esquema antigo com coluna 'data'
            cursor_antigo.execute("SELECT id, tipo, conteudo, resumo, data FROM ideias")
        elif 'data_criacao' in colunas:
            # Esquema já atualizado com coluna 'data_criacao'
            cursor_antigo.execute("SELECT id, tipo, conteudo, resumo, data_criacao FROM ideias")
        else:
            # Esquema sem data, usar apenas as colunas básicas
            cursor_antigo.execute("SELECT id, tipo, conteudo, resumo FROM ideias")
            
        ideias = cursor_antigo.fetchall()
        logger.info(f"Encontradas {len(ideias)} ideias para migração")
        
        # Migra as ideias
        for ideia in ideias:
            # Adapta os dados com base nas colunas disponíveis
            if 'data' in colunas or 'data_criacao' in colunas:
                id_antigo, tipo, conteudo, resumo, data = ideia
            else:
                id_antigo, tipo, conteudo, resumo = ideia
                data = datetime.now()
            
            # Insere a ideia no novo banco
            cursor_novo.execute(
                "INSERT INTO ideias (id, tipo, conteudo, resumo, data_criacao) VALUES (?, ?, ?, ?, ?)",
                (id_antigo, tipo, conteudo, resumo, data or datetime.now())
            )
        
        # Verifica o esquema da tabela brainstorms no banco antigo
        cursor_antigo.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='brainstorms'")
        if cursor_antigo.fetchone():
            cursor_antigo.execute("PRAGMA table_info(brainstorms)")
            colunas_bs = {info[1]: info[0] for info in cursor_antigo.fetchall()}
            logger.info(f"Colunas encontradas na tabela brainstorms: {list(colunas_bs.keys())}")
            
            # Determina a consulta SQL com base nas colunas disponíveis
            if 'data' in colunas_bs:
                # Esquema antigo com coluna 'data'
                cursor_antigo.execute("SELECT id, ideia_id, conteudo, data FROM brainstorms")
            elif 'data_criacao' in colunas_bs:
                # Esquema já atualizado com coluna 'data_criacao'
                cursor_antigo.execute("SELECT id, ideia_id, conteudo, data_criacao FROM brainstorms")
            else:
                # Esquema sem data, usar apenas as colunas básicas
                cursor_antigo.execute("SELECT id, ideia_id, conteudo FROM brainstorms")
                
            brainstorms = cursor_antigo.fetchall()
            logger.info(f"Encontrados {len(brainstorms)} brainstorms para migração")
            
            # Migra os brainstorms
            for brainstorm in brainstorms:
                # Adapta os dados com base nas colunas disponíveis
                if 'data' in colunas_bs or 'data_criacao' in colunas_bs:
                    id_antigo, ideia_id, conteudo, data = brainstorm
                else:
                    id_antigo, ideia_id, conteudo = brainstorm
                    data = datetime.now()
                
                # Insere o brainstorm no novo banco
                cursor_novo.execute(
                    "INSERT INTO brainstorms (id, ideia_id, conteudo, data_criacao) VALUES (?, ?, ?, ?)",
                    (id_antigo, ideia_id, conteudo, data or datetime.now())
                )
        else:
            logger.info("Tabela 'brainstorms' não encontrada no banco de dados antigo")
        
        # Commit das alterações
        conn_novo.commit()
        
        # Fecha as conexões
        conn_antigo.close()
        conn_novo.close()
        
        # Renomeia o banco de dados antigo para backup
        db_backup_path = f"{db_antigo_path}.bak"
        try:
            if os.path.exists(db_backup_path):
                os.remove(db_backup_path)
            os.rename(db_antigo_path, db_backup_path)
            logger.info(f"Banco de dados antigo renomeado para: {db_backup_path}")
            
            # Renomeia o novo banco de dados para o nome original
            os.rename(db_novo_path, db_antigo_path)
            logger.info(f"Novo banco de dados renomeado para: {db_antigo_path}")
        except Exception as e:
            logger.error(f"Erro ao renomear bancos de dados: {e}")
            return False
        
        logger.info(f"Migração concluída: {len(ideias)} ideias migradas com sucesso")
        return True
    
    except Exception as e:
        logger.error(f"Erro durante a migração do banco de dados: {e}")
        return False

if __name__ == "__main__":
    logger.info("Iniciando migração do banco de dados...")
    
    if migrar_banco_dados():
        logger.info("Migração do banco de dados concluída com sucesso!")
        print("Migração do banco de dados concluída com sucesso!")
    else:
        logger.error("Falha na migração do banco de dados")
        print("Falha na migração do banco de dados. Verifique os logs para mais detalhes.")
