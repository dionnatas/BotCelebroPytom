"""
Utilitários para o bot Telegram.
"""
import logging
from telegram import Update

from src.config.settings import MY_CHAT_ID, SUPERUSERS_CHAT_ID

logger = logging.getLogger(__name__)

def check_authorization(update: Update) -> bool:
    """
    Verifica se o usuário está autorizado a usar o bot.
    
    Args:
        update: Objeto Update do Telegram
        
    Returns:
        bool: True se autorizado, False caso contrário
    """
    return is_authorized(update.effective_chat.id)

def is_authorized(chat_id: int) -> bool:
    """
    Verifica se um chat_id está autorizado a usar o bot.
    
    Args:
        chat_id: ID do chat a verificar
        
    Returns:
        bool: True se autorizado, False caso contrário
    """
    authorized = False
    
    # Verifica se é um chat autorizado
    if isinstance(MY_CHAT_ID, list):
        if chat_id in MY_CHAT_ID:
            authorized = True
    else:
        if chat_id == MY_CHAT_ID:
            authorized = True
    
    # Verifica se é um grupo autorizado
    # Adicione aqui lógica para verificar grupos autorizados se necessário
    
    # Registra a tentativa de acesso
    logger.info(f"Verificando autorização para chat_id: {chat_id}")
    if authorized:
        logger.info(f"Acesso autorizado para chat_id: {chat_id}")
    else:
        logger.warning(f"Tentativa de acesso não autorizado para chat_id: {chat_id}")
    
    return authorized

def is_superuser(chat_id: int) -> bool:
    """
    Verifica se um chat_id é um superusuário.
    
    Args:
        chat_id: ID do chat a verificar
        
    Returns:
        bool: True se for superusuário, False caso contrário
    """
    if isinstance(SUPERUSERS_CHAT_ID, list):
        return chat_id in SUPERUSERS_CHAT_ID
    else:
        return chat_id == SUPERUSERS_CHAT_ID
