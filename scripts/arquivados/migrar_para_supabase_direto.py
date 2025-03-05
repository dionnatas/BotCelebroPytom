#!/usr/bin/env python3
"""
Script para migrar dados do SQLite para o Supabase usando a chave de serviço diretamente.
"""
import os
import sys
import sqlite3
import logging
import datetime
import shutil
from typing import List, Dict, Any, Optional

# Adiciona o diretório raiz ao path para importar os módulos do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase import create_client, Client
from src.config.settings import DB_PATH

# Configuração de logging
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

# Nomes das tabelas
TABELA_IDEIAS = "ideias"
TABELA_BRAINSTORMS = "brainstorms"

def criar_backup_db() -> str:
    """
    Cria um backup do banco de dados SQLite.
    
    Returns:
        str: Caminho para o arquivo de backup
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    backup_path = f"{DB_PATH}.bak.{timestamp}"
    
    try:
        shutil.copy2(DB_PATH, backup_path)
        logger.info(f"Backup do banco de dados criado em {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Erro ao criar backup: {e}")
        raise

def obter_ideias_sqlite() -> List[Dict[str, Any]]:
    """
    Obtém todas as ideias do banco de dados SQLite.
    
    Returns:
        List[Dict[str, Any]]: Lista de ideias
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM ideias")
        ideias = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return ideias
    except Exception as e:
        logger.error(f"Erro ao obter ideias do SQLite: {e}")
        raise

def obter_brainstorms_sqlite(ideia_id: int) -> List[Dict[str, Any]]:
    """
    Obtém todos os brainstorms de uma ideia do banco de dados SQLite.
    
    Args:
        ideia_id: ID da ideia
        
    Returns:
        List[Dict[str, Any]]: Lista de brainstorms
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM brainstorms WHERE ideia_id = ?", (ideia_id,))
        brainstorms = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return brainstorms
    except Exception as e:
        logger.error(f"Erro ao obter brainstorms do SQLite: {e}")
        raise

def salvar_ideia_supabase(supabase: Client, ideia: Dict[str, Any]) -> Optional[int]:
    """
    Salva uma ideia no Supabase.
    
    Args:
        supabase: Cliente Supabase
        ideia: Dados da ideia
        
    Returns:
        Optional[int]: ID da ideia salva ou None em caso de erro
    """
    try:
        logger.info(f"Salvando ideia no Supabase para chat_id {ideia['chat_id']}")
        
        # Preparar os dados para inserir
        dados = {
            "conteudo": ideia['conteudo'],
            "chat_id": ideia['chat_id'],
            "tipo": ideia['tipo'],
            "resumo": ideia.get('resumo', ''),
            "created_at": ideia.get('created_at', datetime.datetime.now().isoformat())
        }
        logger.info(f"Dados a serem inseridos: {dados}")
        
        # Inserir a ideia no Supabase
        response = supabase.table(TABELA_IDEIAS).insert(dados).execute()
        
        # Verificar se a inserção foi bem-sucedida
        if response.data and len(response.data) > 0:
            ideia_id = response.data[0].get("id")
            logger.info(f"Ideia salva com ID: {ideia_id}")
            return ideia_id
        
        # Logar o erro detalhado
        if hasattr(response, 'error') and response.error:
            logger.error(f"Erro ao salvar ideia: {response.error}")
        else:
            logger.error(f"Erro desconhecido ao salvar ideia. Resposta: {response}")
        return None
        
    except Exception as e:
        logger.error(f"Erro ao salvar ideia: {e}", exc_info=True)
        return None

def salvar_brainstorm_supabase(supabase: Client, brainstorm: Dict[str, Any], novo_ideia_id: int) -> Optional[int]:
    """
    Salva um brainstorm no Supabase.
    
    Args:
        supabase: Cliente Supabase
        brainstorm: Dados do brainstorm
        novo_ideia_id: Novo ID da ideia no Supabase
        
    Returns:
        Optional[int]: ID do brainstorm salvo ou None em caso de erro
    """
    try:
        logger.info(f"Salvando brainstorm no Supabase para ideia_id {novo_ideia_id}")
        
        # Preparar os dados para inserir
        dados = {
            "ideia_id": novo_ideia_id,
            "conteudo": brainstorm['conteudo'],
            "created_at": brainstorm.get('created_at', datetime.datetime.now().isoformat())
        }
        
        # Inserir o brainstorm no Supabase
        response = supabase.table(TABELA_BRAINSTORMS).insert(dados).execute()
        
        # Verificar se a inserção foi bem-sucedida
        if response.data and len(response.data) > 0:
            brainstorm_id = response.data[0].get("id")
            logger.info(f"Brainstorm salvo com ID: {brainstorm_id}")
            return brainstorm_id
        
        # Logar o erro detalhado
        if hasattr(response, 'error') and response.error:
            logger.error(f"Erro ao salvar brainstorm: {response.error}")
        else:
            logger.error(f"Erro desconhecido ao salvar brainstorm. Resposta: {response}")
        return None
        
    except Exception as e:
        logger.error(f"Erro ao salvar brainstorm: {e}", exc_info=True)
        return None

def migrar_para_supabase():
    """
    Migra os dados do SQLite para o Supabase.
    """
    logger.info("Iniciando migração para o Supabase...")
    
    # Verificar a chave de serviço
    if SUPABASE_SERVICE_KEY == "COLOQUE_SUA_CHAVE_DE_SERVICO_AQUI":
        logger.error("Você precisa substituir a chave de serviço no script antes de executá-lo.")
        print("\n⚠️  ATENÇÃO: Você precisa editar o script e substituir SUPABASE_SERVICE_KEY pela sua chave de serviço real!")
        print("    Você pode encontrá-la no painel do Supabase em: Settings > API > Project API keys > service_role\n")
        return
    
    # Criar backup do banco de dados
    criar_backup_db()
    
    # Inicializar cliente Supabase com a chave de serviço
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        logger.info("Cliente Supabase inicializado com sucesso usando chave de serviço")
    except Exception as e:
        logger.error(f"Erro ao inicializar cliente Supabase: {e}")
        return
    
    # Obter todas as ideias do SQLite
    ideias = obter_ideias_sqlite()
    logger.info(f"Encontradas {len(ideias)} ideias para migrar")
    
    # Mapear IDs antigos para novos
    mapeamento_ids = {}
    ideias_migradas = 0
    
    # Migrar cada ideia e seus brainstorms
    for ideia in ideias:
        # Salvar ideia no Supabase
        novo_ideia_id = salvar_ideia_supabase(supabase, ideia)
        
        if novo_ideia_id:
            # Mapear ID antigo para novo
            mapeamento_ids[ideia['id']] = novo_ideia_id
            ideias_migradas += 1
            
            # Obter brainstorms da ideia
            brainstorms = obter_brainstorms_sqlite(ideia['id'])
            logger.info(f"Encontrados {len(brainstorms)} brainstorms para a ideia {ideia['id']}")
            
            # Migrar brainstorms
            brainstorms_migrados = 0
            for brainstorm in brainstorms:
                if salvar_brainstorm_supabase(supabase, brainstorm, novo_ideia_id):
                    brainstorms_migrados += 1
            
            logger.info(f"Migrados {brainstorms_migrados} de {len(brainstorms)} brainstorms para a ideia {ideia['id']}")
        else:
            logger.error(f"Erro ao migrar ideia {ideia['id']}")
    
    # Resumo da migração
    if ideias_migradas > 0:
        logger.info(f"Migração concluída com sucesso! {ideias_migradas} de {len(ideias)} ideias foram migradas.")
        print(f"\n✅ Migração concluída! {ideias_migradas} de {len(ideias)} ideias foram migradas para o Supabase.")
    else:
        logger.error("Nenhuma ideia foi migrada. Verifique os logs para mais detalhes.")
        print("\n❌ Falha na migração. Nenhuma ideia foi migrada. Verifique os logs para mais detalhes.")

if __name__ == "__main__":
    migrar_para_supabase()
