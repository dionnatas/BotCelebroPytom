"""
Repositório para gerenciamento de ideias no banco de dados.
"""
import logging
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional

from src.config.settings import DB_PATH, USE_SUPABASE
from src.database.supabase_service import supabase_service

logger = logging.getLogger(__name__)

class IdeaRepository:
    """
    Repositório para operações relacionadas a ideias no banco de dados.
    """
    
    def __init__(self, db_path: str = DB_PATH):
        """
        Inicializa o repositório de ideias.
        
        Args:
            db_path: Caminho para o arquivo do banco de dados
        """
        self.db_path = db_path
    
    def salvar_ideia(self, conteudo: str, chat_id: int, tipo: str = "ideia", resumo: str = "") -> Optional[int]:
        """
        Salva uma nova ideia no banco de dados.
        
        Args:
            conteudo: Conteúdo da ideia
            chat_id: ID do chat do usuário
            tipo: Tipo da ideia (padrão: "ideia")
            resumo: Resumo da ideia (padrão: vazio)
            
        Returns:
            int: ID da ideia salva ou None em caso de erro
        """
        # Se o resumo estiver vazio, usa as primeiras 100 caracteres do conteúdo
        if not resumo:
            resumo = conteudo[:100] + "..." if len(conteudo) > 100 else conteudo
            
        # Verifica se deve usar o Supabase
        if USE_SUPABASE:
            return supabase_service.salvar_ideia(conteudo, chat_id, tipo, resumo)
        
        # Caso contrário, usa o SQLite
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtém a data atual
            data_criacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Insere a ideia no banco de dados
            cursor.execute(
                "INSERT INTO ideias (tipo, conteudo, resumo, chat_id, data_criacao) VALUES (?, ?, ?, ?, ?)",
                (tipo, conteudo, resumo, chat_id, data_criacao)
            )
            
            # Obtém o ID da ideia inserida
            ideia_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            logger.info(f"Ideia salva com sucesso. ID: {ideia_id}")
            return ideia_id
        
        except Exception as e:
            logger.error(f"Erro ao salvar ideia: {str(e)}", exc_info=True)
            return None
    
    def listar_ideias(self, chat_id: int, is_superuser: bool = False) -> List[Dict[str, Any]]:
        """
        Lista ideias do banco de dados.
        
        Args:
            chat_id: ID do chat do usuário
            is_superuser: Se True, lista todas as ideias do banco de dados
            
        Returns:
            List[Dict[str, Any]]: Lista de ideias
        """
        # Verifica se deve usar o Supabase
        if USE_SUPABASE:
            return supabase_service.listar_ideias(chat_id, is_superuser)
        
        # Caso contrário, usa o SQLite
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Se for superusuário, busca todas as ideias
            # Senão, busca apenas as ideias do usuário
            if is_superuser:
                cursor.execute(
                    "SELECT id, tipo, conteudo, resumo, data_criacao, chat_id FROM ideias ORDER BY id DESC"
                )
            else:
                cursor.execute(
                    "SELECT id, tipo, conteudo, resumo, data_criacao, chat_id FROM ideias WHERE chat_id = ? ORDER BY id DESC",
                    (chat_id,)
                )
            
            # Converte os resultados para dicionários
            ideias = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            return ideias
        
        except Exception as e:
            logger.error(f"Erro ao listar ideias: {str(e)}", exc_info=True)
            return []
    
    def obter_ideia_por_id(self, ideia_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtém uma ideia específica pelo ID, sem verificar o chat_id.
        Esta função deve ser usada apenas por superusuários.
        
        Args:
            ideia_id: ID da ideia
            
        Returns:
            Dict[str, Any]: Dados da ideia ou None se não encontrada
        """
        # Verifica se deve usar o Supabase
        if USE_SUPABASE:
            try:
                # Para superusuários, podemos usar qualquer chat_id, pois não será verificado
                # is_superuser=True garante que apenas o ID será usado na consulta
                return supabase_service.obter_ideia(ideia_id, 0, True)
            except Exception as e:
                logger.error(f"Erro ao obter ideia por ID no Supabase: {str(e)}", exc_info=True)
                return None
        
        # Caso contrário, usa o SQLite
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Busca a ideia pelo ID
            cursor.execute("SELECT * FROM ideias WHERE id = ?", (ideia_id,))
            row = cursor.fetchone()
            
            conn.close()
            
            if row:
                return dict(row)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Erro ao obter ideia por ID no SQLite: {str(e)}", exc_info=True)
            return None
    
    def obter_ideia(self, ideia_id: int, chat_id: int, is_superuser: bool = False) -> Optional[Dict[str, Any]]:
        """
        Obtém uma ideia específica pelo ID.
        
        Args:
            ideia_id: ID da ideia
            chat_id: ID do chat do usuário
            is_superuser: Se o usuário é um superusuário
            
        Returns:
            Dict[str, Any]: Dados da ideia ou None se não encontrada
        """
        # Verifica se deve usar o Supabase
        if USE_SUPABASE:
            return supabase_service.obter_ideia(ideia_id, chat_id, is_superuser)
        
        # Caso contrário, usa o SQLite
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Se for superusuário, busca a ideia apenas pelo ID
            # Senão, busca pelo ID e chat_id
            if is_superuser:
                cursor.execute("SELECT * FROM ideias WHERE id = ?", (ideia_id,))
            else:
                cursor.execute(
                    "SELECT * FROM ideias WHERE id = ? AND chat_id = ?",
                    (ideia_id, chat_id)
                )
            row = cursor.fetchone()
            
            conn.close()
            
            if row:
                return dict(row)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Erro ao obter ideia: {str(e)}", exc_info=True)
            return None
    
    def apagar_ideia(self, ideia_id: int, chat_id: int, is_superuser: bool = False) -> bool:
        """
        Apaga uma ideia e seus brainstorms relacionados.
        
        Args:
            ideia_id: ID da ideia
            chat_id: ID do chat do usuário
            is_superuser: Se o usuário é um superusuário
            
        Returns:
            bool: True se a ideia foi apagada com sucesso, False caso contrário
        """
        # Verifica se deve usar o Supabase
        if USE_SUPABASE:
            return supabase_service.apagar_ideia(ideia_id, chat_id, is_superuser)
        
        # Caso contrário, usa o SQLite
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verifica se a ideia existe e pertence ao usuário (ou se é superusuário)
            if is_superuser:
                cursor.execute("SELECT id FROM ideias WHERE id = ?", (ideia_id,))
            else:
                cursor.execute(
                    "SELECT id FROM ideias WHERE id = ? AND chat_id = ?",
                    (ideia_id, chat_id)
                )
            
            if not cursor.fetchone():
                conn.close()
                return False
            
            # Inicia uma transação
            conn.execute("BEGIN TRANSACTION")
            
            # Apaga os brainstorms relacionados
            cursor.execute(
                "DELETE FROM brainstorms WHERE ideia_id = ?",
                (ideia_id,)
            )
            
            # Apaga a ideia
            if is_superuser:
                cursor.execute("DELETE FROM ideias WHERE id = ?", (ideia_id,))
            else:
                cursor.execute(
                    "DELETE FROM ideias WHERE id = ? AND chat_id = ?",
                    (ideia_id, chat_id)
                )
            
            # Confirma a transação
            conn.commit()
            conn.close()
            
            logger.info(f"Ideia {ideia_id} apagada com sucesso")
            return True
        
        except Exception as e:
            logger.error(f"Erro ao apagar ideia: {str(e)}", exc_info=True)
            return False

# Instância global do repositório de ideias
idea_repository = IdeaRepository()
