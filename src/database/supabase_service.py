"""
Serviço para interação com o Supabase.
"""
import logging
from typing import Dict, List, Optional, Any

from supabase import create_client, Client

from src.config.supabase_config import SUPABASE_URL, TABELA_IDEIAS, TABELA_BRAINSTORMS, get_supabase_key

logger = logging.getLogger(__name__)

class SupabaseService:
    """
    Serviço para interação com o Supabase.
    """
    
    def __init__(self, use_service_key: bool = True):
        """
        Inicializa o cliente Supabase.
        
        Args:
            use_service_key: Se True, tenta usar a chave de serviço para autenticação.
                             Por padrão, usa a chave de serviço para evitar problemas com RLS.
        """
        try:
            # Obter a chave apropriada (serviço ou anônima)
            key = get_supabase_key(use_service_key)
            
            # Inicializar o cliente Supabase
            self.supabase: Client = create_client(SUPABASE_URL, key)
            
            # Registrar o tipo de chave usada
            key_type = "serviço" if use_service_key and key != get_supabase_key(False) else "anônima"
            logger.info(f"Cliente Supabase inicializado com sucesso usando chave de {key_type}")
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente Supabase: {e}")
            raise
    
    def criar_tabelas(self) -> None:
        """
        Cria as tabelas necessárias no Supabase se elas não existirem.
        """
        try:
            # Verificar se as tabelas existem e criar se necessário
            # Nota: No Supabase, geralmente criamos as tabelas via SQL Editor no dashboard
            # Esta função é mais para documentação da estrutura
            logger.info("Estrutura de tabelas deve ser criada manualmente no Supabase")
        except Exception as e:
            logger.error(f"Erro ao criar tabelas: {e}")
            raise
    
    def salvar_ideia(self, conteudo: str, chat_id: int, tipo: str = "ideia", resumo: str = "") -> Optional[int]:
        """
        Salva uma ideia no Supabase.
        
        Args:
            conteudo: Conteúdo da ideia
            chat_id: ID do chat do usuário
            tipo: Tipo da ideia
            resumo: Resumo da ideia
            
        Returns:
            Optional[int]: ID da ideia salva ou None em caso de erro
        """
        try:
            logger.info(f"Salvando ideia no Supabase para chat_id {chat_id}")
            
            # Preparar os dados para inserir
            dados = {
                "conteudo": conteudo,
                "chat_id": chat_id,
                "tipo": tipo,
                "resumo": resumo
            }
            logger.info(f"Dados a serem inseridos: {dados}")
            
            # Inserir a ideia no Supabase
            response = self.supabase.table(TABELA_IDEIAS).insert(dados).execute()
            
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
    
    def listar_ideias(self, chat_id: int, is_superuser: bool = False) -> List[Dict[str, Any]]:
        """
        Lista as ideias do usuário ou todas as ideias (para superusuários).
        
        Args:
            chat_id: ID do chat do usuário
            is_superuser: Se o usuário é um superusuário
            
        Returns:
            List[Dict[str, Any]]: Lista de ideias
        """
        try:
            logger.info(f"Listando ideias para chat_id {chat_id} (superuser: {is_superuser})")
            
            # Construir a query
            query = self.supabase.table(TABELA_IDEIAS)
            
            # Se não for superusuário, filtrar por chat_id
            if not is_superuser:
                query = query.eq("chat_id", chat_id)
            
            # Executar a query
            response = query.select("*").order("id").execute()
            
            # Verificar se a consulta foi bem-sucedida
            if response.data is not None:
                return response.data
            
            logger.error(f"Erro ao listar ideias: {response.error}")
            return []
            
        except Exception as e:
            logger.error(f"Erro ao listar ideias: {e}")
            return []
    
    def obter_ideia(self, ideia_id: int, chat_id: int, is_superuser: bool = False) -> Optional[Dict[str, Any]]:
        """
        Obtém uma ideia específica.
        
        Args:
            ideia_id: ID da ideia
            chat_id: ID do chat do usuário
            is_superuser: Se o usuário é um superusuário
            
        Returns:
            Optional[Dict[str, Any]]: Dados da ideia ou None se não encontrada
        """
        try:
            logger.info(f"Obtendo ideia {ideia_id} para chat_id {chat_id} (superuser: {is_superuser})")
            
            # Construir a query
            query = self.supabase.table(TABELA_IDEIAS).select("*")
            
            # Filtrar por ID
            query = query.eq("id", ideia_id)
            
            # Se não for superusuário, filtrar por chat_id
            if not is_superuser:
                query = query.eq("chat_id", chat_id)
            
            # Executar a query
            response = query.execute()
            
            # Verificar se a consulta foi bem-sucedida e se retornou algum resultado
            if response.data and len(response.data) > 0:
                return response.data[0]
            
            logger.warning(f"Ideia {ideia_id} não encontrada ou acesso não autorizado")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter ideia: {e}")
            return None
    
    def apagar_ideia(self, ideia_id: int, chat_id: int, is_superuser: bool = False) -> bool:
        """
        Apaga uma ideia específica.
        
        Args:
            ideia_id: ID da ideia
            chat_id: ID do chat do usuário
            is_superuser: Se o usuário é um superusuário
            
        Returns:
            bool: True se a ideia foi apagada com sucesso, False caso contrário
        """
        try:
            logger.info(f"Apagando ideia {ideia_id} para chat_id {chat_id} (superuser: {is_superuser})")
            
            # Verificar se o usuário tem permissão para apagar a ideia
            if not is_superuser:
                ideia = self.obter_ideia(ideia_id, chat_id)
                if not ideia:
                    logger.warning(f"Tentativa de apagar ideia {ideia_id} não autorizada")
                    return False
            
            # Apagar a ideia
            response = self.supabase.table(TABELA_IDEIAS).delete().eq("id", ideia_id).execute()
            
            # Verificar se a exclusão foi bem-sucedida
            if response.data is not None:
                logger.info(f"Ideia {ideia_id} apagada com sucesso")
                return True
            
            logger.error(f"Erro ao apagar ideia: {response.error}")
            return False
            
        except Exception as e:
            logger.error(f"Erro ao apagar ideia: {e}")
            return False
    
    def salvar_brainstorm(self, ideia_id: int, conteudo: str) -> Optional[int]:
        """
        Salva um brainstorm no Supabase.
        
        Args:
            ideia_id: ID da ideia
            conteudo: Conteúdo do brainstorm
            
        Returns:
            Optional[int]: ID do brainstorm salvo ou None em caso de erro
        """
        try:
            logger.info(f"Salvando brainstorm para ideia {ideia_id}")
            
            # Inserir o brainstorm no Supabase
            response = self.supabase.table(TABELA_BRAINSTORMS).insert({
                "ideia_id": ideia_id,
                "conteudo": conteudo
            }).execute()
            
            # Verificar se a inserção foi bem-sucedida
            if response.data and len(response.data) > 0:
                brainstorm_id = response.data[0].get("id")
                logger.info(f"Brainstorm salvo com ID: {brainstorm_id}")
                return brainstorm_id
            
            logger.error(f"Erro ao salvar brainstorm: {response.error}")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao salvar brainstorm: {e}")
            return None
    
    def obter_brainstorm(self, ideia_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtém o brainstorm para uma ideia específica.
        
        Args:
            ideia_id: ID da ideia
            
        Returns:
            Optional[Dict[str, Any]]: Dados do brainstorm ou None se não encontrado
        """
        try:
            logger.info(f"Obtendo brainstorm para ideia {ideia_id}")
            
            # Executar a query
            response = self.supabase.table(TABELA_BRAINSTORMS).eq("ideia_id", ideia_id).select("*").execute()
            
            # Verificar se a consulta foi bem-sucedida e se retornou algum resultado
            if response.data and len(response.data) > 0:
                return response.data[0]
            
            logger.warning(f"Brainstorm para ideia {ideia_id} não encontrado")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter brainstorm: {e}")
            return None


# Instância global do serviço Supabase
# Por padrão, tenta usar a chave de serviço para operações administrativas
supabase_service = SupabaseService(use_service_key=True)
