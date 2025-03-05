"""
Repositório para gerenciamento de brainstorms no banco de dados.
"""
import logging
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional

from src.config.settings import DB_PATH, USE_SUPABASE
from src.database.supabase_service import supabase_service

logger = logging.getLogger(__name__)

class BrainstormRepository:
    """
    Repositório para operações relacionadas a brainstorms no banco de dados.
    """
    
    def __init__(self, db_path: str = DB_PATH):
        """
        Inicializa o repositório de brainstorms.
        
        Args:
            db_path: Caminho para o arquivo do banco de dados
        """
        self.db_path = db_path
    
    def salvar_brainstorm(self, ideia_id: int, conteudo: str) -> Optional[int]:
        """
        Salva um novo brainstorm no banco de dados.
        
        Args:
            ideia_id: ID da ideia relacionada
            conteudo: Conteúdo do brainstorm
            
        Returns:
            int: ID do brainstorm salvo ou None em caso de erro
        """
        # Verifica se deve usar o Supabase
        if USE_SUPABASE:
            try:
                # Preparar os dados para inserir
                dados = {
                    "ideia_id": ideia_id,
                    "conteudo": conteudo
                }
                
                # Inserir o brainstorm no Supabase
                response = supabase_service.supabase.table("brainstorms").insert(dados).execute()
                
                # Verificar se a inserção foi bem-sucedida
                if response.data and len(response.data) > 0:
                    brainstorm_id = response.data[0].get("id")
                    logger.info(f"Brainstorm salvo no Supabase com ID: {brainstorm_id}")
                    return brainstorm_id
                
                logger.error(f"Erro ao salvar brainstorm no Supabase: {response.error}")
                return None
                
            except Exception as e:
                logger.error(f"Erro ao salvar brainstorm no Supabase: {e}", exc_info=True)
                return None
        
        # Caso contrário, usa o SQLite
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtém a data atual
            data_criacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Insere o brainstorm no banco de dados
            cursor.execute(
                "INSERT INTO brainstorms (ideia_id, conteudo, data_criacao) VALUES (?, ?, ?)",
                (ideia_id, conteudo, data_criacao)
            )
            
            # Obtém o ID do brainstorm inserido
            brainstorm_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            logger.info(f"Brainstorm salvo com sucesso no SQLite. ID: {brainstorm_id}")
            return brainstorm_id
        
        except Exception as e:
            logger.error(f"Erro ao salvar brainstorm no SQLite: {str(e)}", exc_info=True)
            return None
    
    def obter_brainstorms_por_ideia(self, ideia_id: int) -> List[Dict[str, Any]]:
        """
        Obtém todos os brainstorms de uma ideia.
        
        Args:
            ideia_id: ID da ideia
            
        Returns:
            List[Dict[str, Any]]: Lista de brainstorms
        """
        # Verifica se deve usar o Supabase
        if USE_SUPABASE:
            try:
                logger.info(f"Obtendo brainstorms para ideia {ideia_id} no Supabase")
                
                # Construir a query
                query = supabase_service.supabase.table("brainstorms").select("*")
                
                # Filtrar por ideia_id
                query = query.eq("ideia_id", ideia_id)
                
                # Ordenar por data de criação (decrescente)
                query = query.order("created_at", desc=True)
                
                # Executar a query
                response = query.execute()
                
                # Verificar se a consulta foi bem-sucedida
                if response.data is not None:
                    return response.data
                
                logger.error(f"Erro ao obter brainstorms no Supabase: {response.error}")
                return []
                
            except Exception as e:
                logger.error(f"Erro ao obter brainstorms no Supabase: {e}")
                return []
        
        # Caso contrário, usa o SQLite
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Busca os brainstorms da ideia
            cursor.execute(
                "SELECT * FROM brainstorms WHERE ideia_id = ? ORDER BY data_criacao DESC",
                (ideia_id,)
            )
            
            # Converte os resultados para dicionários
            brainstorms = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            return brainstorms
        
        except Exception as e:
            logger.error(f"Erro ao obter brainstorms no SQLite: {str(e)}", exc_info=True)
            return []
    
    def obter_brainstorm(self, brainstorm_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtém um brainstorm específico pelo ID.
        
        Args:
            brainstorm_id: ID do brainstorm
            
        Returns:
            Dict[str, Any]: Dados do brainstorm ou None se não encontrado
        """
        # Verifica se deve usar o Supabase
        if USE_SUPABASE:
            try:
                logger.info(f"Obtendo brainstorm {brainstorm_id} no Supabase")
                
                # Construir a query
                query = supabase_service.supabase.table("brainstorms").select("*")
                
                # Filtrar por id
                query = query.eq("id", brainstorm_id)
                
                # Executar a query
                response = query.execute()
                
                # Verificar se a consulta foi bem-sucedida e se retornou algum resultado
                if response.data is not None and len(response.data) > 0:
                    return response.data[0]
                
                logger.warning(f"Brainstorm com ID {brainstorm_id} não encontrado no Supabase")
                return None
                
            except Exception as e:
                logger.error(f"Erro ao obter brainstorm no Supabase: {e}", exc_info=True)
                return None
        
        # Caso contrário, usa o SQLite
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Busca o brainstorm
            cursor.execute(
                "SELECT * FROM brainstorms WHERE id = ?",
                (brainstorm_id,)
            )
            
            # Obtém o resultado
            row = cursor.fetchone()
            
            conn.close()
            
            # Converte o resultado para dicionário se existir
            if row:
                return dict(row)
            else:
                logger.warning(f"Brainstorm com ID {brainstorm_id} não encontrado no SQLite")
                return None
        
        except Exception as e:
            logger.error(f"Erro ao obter brainstorm no SQLite: {str(e)}", exc_info=True)
            return None
    
    def atualizar_brainstorm(self, brainstorm_id: int, novo_conteudo: str) -> bool:
        """
        Atualiza o conteúdo de um brainstorm existente.
        
        Args:
            brainstorm_id: ID do brainstorm
            novo_conteudo: Novo conteúdo do brainstorm
            
        Returns:
            bool: True se o brainstorm foi atualizado com sucesso, False caso contrário
        """
        # Verifica se deve usar o Supabase
        if USE_SUPABASE:
            try:
                logger.info(f"Verificando se o brainstorm {brainstorm_id} existe no Supabase")
                
                # Verificar se o brainstorm existe
                brainstorm = self.obter_brainstorm(brainstorm_id)
                if not brainstorm:
                    logger.warning(f"Brainstorm com ID {brainstorm_id} não encontrado no Supabase")
                    return False
                
                # Preparar os dados para atualizar
                dados = {
                    "conteudo": novo_conteudo
                    # Não usamos updated_at pois a coluna não existe na tabela
                }
                
                # Atualizar o brainstorm no Supabase
                response = supabase_service.supabase.table("brainstorms").update(dados).eq("id", brainstorm_id).execute()
                
                # Verificar se a atualização foi bem-sucedida
                if response.data and len(response.data) > 0:
                    logger.info(f"Brainstorm {brainstorm_id} atualizado com sucesso no Supabase")
                    return True
                
                logger.error(f"Erro ao atualizar brainstorm no Supabase: {response.error}")
                return False
                
            except Exception as e:
                logger.error(f"Erro ao atualizar brainstorm no Supabase: {e}", exc_info=True)
                return False
        
        # Caso contrário, usa o SQLite
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verifica se o brainstorm existe
            cursor.execute(
                "SELECT id FROM brainstorms WHERE id = ?",
                (brainstorm_id,)
            )
            
            if not cursor.fetchone():
                conn.close()
                logger.warning(f"Brainstorm com ID {brainstorm_id} não encontrado no SQLite")
                return False
            
            # Obtém a data atual
            data_criacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Atualiza o brainstorm
            cursor.execute(
                "UPDATE brainstorms SET conteudo = ?, data_criacao = ? WHERE id = ?",
                (novo_conteudo, data_criacao, brainstorm_id)
            )
            
            conn.commit()
            conn.close()
            
            logger.info(f"Brainstorm {brainstorm_id} atualizado com sucesso no SQLite")
            return True
        
        except Exception as e:
            logger.error(f"Erro ao atualizar brainstorm no SQLite: {str(e)}", exc_info=True)
            return False

# Instância global do repositório de brainstorms
brainstorm_repository = BrainstormRepository()
