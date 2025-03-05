"""
Utilitários para o bot Telegram.
"""
import logging
from telegram import Update

from src.config.settings import MY_CHAT_ID

logger = logging.getLogger(__name__)

def check_authorization(update: Update) -> bool:
    """
    Verifica se o usuário está autorizado a usar o bot.
    
    Args:
        update: Objeto Update do Telegram
        
    Returns:
        bool: True se autorizado, False caso contrário
    """
    chat_id = update.effective_chat.id
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
    user = update.effective_user
    username = user.username if user.username else "Sem username"
    if authorized:
        logger.info(f"Acesso autorizado: {username} (ID: {chat_id})")
    else:
        logger.warning(f"Tentativa de acesso não autorizado: {username} (ID: {chat_id})")
    
    return authorized
