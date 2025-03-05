"""
Repositório para gerenciamento de brainstorms no banco de dados.
"""
import logging
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional

from src.config.settings import DB_PATH

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
            
            logger.info(f"Brainstorm salvo com sucesso. ID: {brainstorm_id}")
            return brainstorm_id
        
        except Exception as e:
            logger.error(f"Erro ao salvar brainstorm: {str(e)}", exc_info=True)
            return None
    
    def obter_brainstorms_por_ideia(self, ideia_id: int) -> List[Dict[str, Any]]:
        """
        Obtém todos os brainstorms de uma ideia.
        
        Args:
            ideia_id: ID da ideia
            
        Returns:
            List[Dict[str, Any]]: Lista de brainstorms
        """
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
            logger.error(f"Erro ao obter brainstorms: {str(e)}", exc_info=True)
            return []
    
    def obter_brainstorm(self, brainstorm_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtém um brainstorm específico pelo ID.
        
        Args:
            brainstorm_id: ID do brainstorm
            
        Returns:
            Dict[str, Any]: Dados do brainstorm ou None se não encontrado
        """
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
                return None
        
        except Exception as e:
            logger.error(f"Erro ao obter brainstorm: {str(e)}", exc_info=True)
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
                logger.warning(f"Brainstorm com ID {brainstorm_id} não encontrado")
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
            
            logger.info(f"Brainstorm {brainstorm_id} atualizado com sucesso")
            return True
        
        except Exception as e:
            logger.error(f"Erro ao atualizar brainstorm: {str(e)}", exc_info=True)
            return False

# Instância global do repositório de brainstorms
brainstorm_repository = BrainstormRepository()
