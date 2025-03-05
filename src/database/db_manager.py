"""
Gerenciador de banco de dados do bot Cerebro.
"""
import logging
import sqlite3
from datetime import datetime
from typing import Tuple, List, Dict, Any, Optional

from src.config.settings import DB_PATH

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Gerencia as operações de banco de dados para o bot Cerebro.
    """
    
    def __init__(self):
        """
        Inicializa o gerenciador de banco de dados.
        """
        self.db_path = DB_PATH
        self.init_db()
    
    def init_db(self) -> None:
        """
        Inicializa o banco de dados SQLite.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabela de ideias
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ideias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo TEXT NOT NULL,
                    conteudo TEXT NOT NULL,
                    resumo TEXT NOT NULL,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de brainstorms
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS brainstorms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ideia_id INTEGER NOT NULL,
                    conteudo TEXT NOT NULL,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ideia_id) REFERENCES ideias (id)
                )
            ''')
            
            conn.commit()
            logger.info("Banco de dados inicializado com sucesso.")
        except sqlite3.Error as e:
            logger.error(f"Erro ao inicializar o banco de dados: {e}")
        finally:
            if conn:
                conn.close()
    
    def salvar_ideia(self, tipo: str, conteudo: str, resumo: str) -> int:
        """
        Salva uma ideia no banco de dados.
        
        Args:
            tipo: Tipo da ideia (IDEIA, QUESTAO, etc.)
            conteudo: Conteúdo completo da ideia
            resumo: Resumo da ideia
            
        Returns:
            int: ID da ideia salva
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO ideias (tipo, conteudo, resumo, data_criacao) VALUES (?, ?, ?, ?)",
                (tipo, conteudo, resumo, datetime.now())
            )
            
            ideia_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Ideia salva com ID: {ideia_id}")
            return ideia_id
        except sqlite3.Error as e:
            logger.error(f"Erro ao salvar ideia: {e}")
            return -1
        finally:
            if conn:
                conn.close()
    
    def salvar_brainstorm(self, ideia_id: int, conteudo: str) -> int:
        """
        Salva um brainstorm no banco de dados.
        
        Args:
            ideia_id: ID da ideia relacionada
            conteudo: Conteúdo do brainstorm
            
        Returns:
            int: ID do brainstorm salvo
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO brainstorms (ideia_id, conteudo, data_criacao) VALUES (?, ?, ?)",
                (ideia_id, conteudo, datetime.now())
            )
            
            brainstorm_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Brainstorm salvo com ID: {brainstorm_id}")
            return brainstorm_id
        except sqlite3.Error as e:
            logger.error(f"Erro ao salvar brainstorm: {e}")
            return -1
        finally:
            if conn:
                conn.close()
    
    def listar_ideias(self, limite: int = 10) -> List[Dict[str, Any]]:
        """
        Lista as ideias salvas no banco de dados.
        
        Args:
            limite: Número máximo de ideias a retornar
            
        Returns:
            List[Dict]: Lista de ideias
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, tipo, resumo, data_criacao FROM ideias ORDER BY data_criacao DESC LIMIT ?",
                (limite,)
            )
            
            ideias = [dict(row) for row in cursor.fetchall()]
            logger.info(f"Listadas {len(ideias)} ideias")
            return ideias
        except sqlite3.Error as e:
            logger.error(f"Erro ao listar ideias: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def obter_ideia(self, ideia_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtém uma ideia específica pelo ID.
        
        Args:
            ideia_id: ID da ideia
            
        Returns:
            Dict: Dados da ideia ou None se não encontrada
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM ideias WHERE id = ?",
                (ideia_id,)
            )
            
            ideia = cursor.fetchone()
            if ideia:
                ideia_dict = dict(ideia)
                
                # Obtém os brainstorms relacionados
                cursor.execute(
                    "SELECT * FROM brainstorms WHERE ideia_id = ? ORDER BY data_criacao DESC",
                    (ideia_id,)
                )
                
                brainstorms = [dict(row) for row in cursor.fetchall()]
                ideia_dict['brainstorms'] = brainstorms
                
                logger.info(f"Ideia {ideia_id} obtida com sucesso")
                return ideia_dict
            else:
                logger.warning(f"Ideia {ideia_id} não encontrada")
                return None
        except sqlite3.Error as e:
            logger.error(f"Erro ao obter ideia {ideia_id}: {e}")
            return None
        finally:
            if conn:
                conn.close()


# Instância global do gerenciador de banco de dados
db_manager = DatabaseManager()
