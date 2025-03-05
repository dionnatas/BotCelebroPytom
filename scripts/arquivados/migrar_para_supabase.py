"""
Script para migrar dados do banco de dados SQLite local para o Supabase.
"""
import logging
import os
import sqlite3
import sys
from datetime import datetime

# Adiciona o diretório raiz ao path para importar os módulos do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.supabase_service import SupabaseService

# Criar uma instância do serviço Supabase com a chave de serviço
supabase_service = SupabaseService(use_service_key=True)
from src.config.settings import DB_PATH

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def criar_backup_banco_local():
    """
    Cria um backup do banco de dados local antes da migração.
    
    Returns:
        str: Caminho do arquivo de backup
    """
    backup_path = f"{DB_PATH}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    try:
        # Verifica se o banco de dados existe
        if not os.path.exists(DB_PATH):
            logger.error(f"Banco de dados não encontrado em {DB_PATH}")
            return None
        
        # Copia o arquivo do banco de dados
        import shutil
        shutil.copy2(DB_PATH, backup_path)
        logger.info(f"Backup do banco de dados criado em {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Erro ao criar backup do banco de dados: {e}")
        return None

def migrar_ideias():
    """
    Migra as ideias do banco de dados local para o Supabase.
    
    Returns:
        int: Número de ideias migradas com sucesso
    """
    try:
        # Conecta ao banco de dados local
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Obtém todas as ideias
        cursor.execute("SELECT * FROM ideias")
        ideias = cursor.fetchall()
        
        logger.info(f"Encontradas {len(ideias)} ideias para migrar")
        
        # Contador de ideias migradas com sucesso
        migradas = 0
        
        # Migra cada ideia para o Supabase
        for ideia in ideias:
            # Obtém os dados da ideia
            ideia_dict = dict(ideia)
            
            # Verifica se a ideia tem chat_id
            chat_id = ideia_dict.get("chat_id")
            if not chat_id:
                logger.warning(f"Ideia {ideia_dict['id']} não tem chat_id, usando valor padrão")
                chat_id = 123456789  # Valor padrão para ideias sem chat_id
            
            # Obtém tipo e resumo (se disponíveis)
            tipo = ideia_dict.get("tipo", "ideia")
            resumo = ideia_dict.get("resumo", "")
            
            # Salva a ideia no Supabase
            ideia_id = supabase_service.salvar_ideia(
                conteudo=ideia_dict["conteudo"],
                chat_id=chat_id,
                tipo=tipo,
                resumo=resumo
            )
            
            if ideia_id:
                logger.info(f"Ideia {ideia_dict['id']} migrada com sucesso para o Supabase com ID {ideia_id}")
                
                # Verifica se a ideia tem brainstorms associados
                cursor.execute("SELECT * FROM brainstorms WHERE ideia_id = ?", (ideia_dict["id"],))
                brainstorms = cursor.fetchall()
                
                for brainstorm in brainstorms:
                    brainstorm_dict = dict(brainstorm)
                    
                    # Salva o brainstorm no Supabase
                    brainstorm_id = supabase_service.salvar_brainstorm(
                        ideia_id=ideia_id,  # Usa o novo ID gerado pelo Supabase
                        conteudo=brainstorm_dict["conteudo"]
                    )
                    
                    if brainstorm_id:
                        logger.info(f"Brainstorm para ideia {ideia_dict['id']} migrado com sucesso")
                    else:
                        logger.error(f"Erro ao migrar brainstorm para ideia {ideia_dict['id']}")
                
                migradas += 1
            else:
                logger.error(f"Erro ao migrar ideia {ideia_dict['id']}")
        
        conn.close()
        return migradas
    
    except Exception as e:
        logger.error(f"Erro ao migrar ideias: {e}")
        return 0

def main():
    """
    Função principal para executar a migração.
    """
    logger.info("Iniciando migração para o Supabase...")
    
    # Cria backup do banco de dados local
    backup_path = criar_backup_banco_local()
    if not backup_path:
        logger.error("Falha ao criar backup. Abortando migração.")
        return
    
    # Migra as ideias
    ideias_migradas = migrar_ideias()
    
    if ideias_migradas > 0:
        logger.info(f"Migração concluída com sucesso. {ideias_migradas} ideias migradas para o Supabase.")
    else:
        logger.error("Nenhuma ideia foi migrada. Verifique os logs para mais detalhes.")

if __name__ == "__main__":
    main()
