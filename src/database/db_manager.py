"""
Gerenciador de banco de dados do bot Cerebro.
Este módulo mantém compatibilidade com o código antigo, mas internamente
usa os novos repositórios idea_repository e brainstorm_repository.
"""
import logging
from typing import Tuple, List, Dict, Any, Optional

from src.database.idea_repository import idea_repository
from src.database.brainstorm_repository import brainstorm_repository

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Gerencia as operações de banco de dados para o bot Cerebro.
    Esta classe mantém compatibilidade com o código antigo, mas internamente
    usa os novos repositórios idea_repository e brainstorm_repository.
    """
    
    def __init__(self):
        """
        Inicializa o gerenciador de banco de dados.
        """
        pass
    
    def init_db(self) -> None:
        """
        Inicializa o banco de dados SQLite.
        Este método é mantido para compatibilidade, mas não faz nada.
        """
        # Não faz nada, pois a inicialização é feita nos repositórios
        pass
    
    def salvar_ideia(self, conteudo: str, chat_id: int) -> Optional[int]:
        """
        Salva uma nova ideia no banco de dados.
        
        Args:
            conteudo: Conteúdo da ideia
            chat_id: ID do chat do usuário
            
        Returns:
            int: ID da ideia salva ou None em caso de erro
        """
        return idea_repository.salvar_ideia(conteudo, chat_id)
    
    def listar_ideias(self, chat_id: int) -> List[Dict[str, Any]]:
        """
        Lista todas as ideias de um usuário.
        
        Args:
            chat_id: ID do chat do usuário
            
        Returns:
            List[Dict[str, Any]]: Lista de ideias
        """
        return idea_repository.listar_ideias(chat_id)
    
    def obter_ideia(self, ideia_id: int, chat_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtém uma ideia específica pelo ID.
        
        Args:
            ideia_id: ID da ideia
            chat_id: ID do chat do usuário
            
        Returns:
            Dict[str, Any]: Dados da ideia ou None se não encontrada
        """
        return idea_repository.obter_ideia(ideia_id, chat_id)
    
    def salvar_brainstorm(self, ideia_id: int, conteudo: str) -> Optional[int]:
        """
        Salva um novo brainstorm no banco de dados.
        
        Args:
            ideia_id: ID da ideia relacionada
            conteudo: Conteúdo do brainstorm
            
        Returns:
            int: ID do brainstorm salvo ou None em caso de erro
        """
        return brainstorm_repository.salvar_brainstorm(ideia_id, conteudo)
    
    def obter_brainstorms_por_ideia(self, ideia_id: int) -> List[Dict[str, Any]]:
        """
        Obtém todos os brainstorms de uma ideia.
        
        Args:
            ideia_id: ID da ideia
            
        Returns:
            List[Dict[str, Any]]: Lista de brainstorms
        """
        return brainstorm_repository.obter_brainstorms_por_ideia(ideia_id)
    
    def apagar_ideia(self, ideia_id: int, chat_id: int) -> bool:
        """
        Apaga uma ideia e seus brainstorms relacionados.
        
        Args:
            ideia_id: ID da ideia
            chat_id: ID do chat do usuário
            
        Returns:
            bool: True se a ideia foi apagada com sucesso, False caso contrário
        """
        return idea_repository.apagar_ideia(ideia_id, chat_id)
    
    def atualizar_brainstorm(self, brainstorm_id: int, novo_conteudo: str) -> bool:
        """
        Atualiza o conteúdo de um brainstorm existente.
        
        Args:
            brainstorm_id: ID do brainstorm
            novo_conteudo: Novo conteúdo do brainstorm
            
        Returns:
            bool: True se o brainstorm foi atualizado com sucesso, False caso contrário
        """
        return brainstorm_repository.atualizar_brainstorm(brainstorm_id, novo_conteudo)

# Instância global do gerenciador de banco de dados
db_manager = DatabaseManager()
