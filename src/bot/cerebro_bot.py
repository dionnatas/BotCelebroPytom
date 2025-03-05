"""
Implementação principal do bot Telegram Cerebro.
"""
import logging
import os
from typing import Dict, Any

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from src.config.settings import TELEGRAM_API_KEY
from src.bot.command_handlers import start, listar_ideias, ver_ideia, apagar_ideia, listar_comandos, refazer_brainstorm
from src.bot.message_handlers import handle_message

logger = logging.getLogger(__name__)

class CerebroBot:
    """
    Implementação principal do bot Telegram Cerebro.
    """
    
    def __init__(self):
        """
        Inicializa o bot Telegram.
        """
        self.updater = Updater(token=TELEGRAM_API_KEY, use_context=True)
        self.dispatcher = self.updater.dispatcher
        
        # Registra os handlers
        self._register_handlers()
        
        logger.info("Bot Cerebro inicializado com sucesso")
    
    def _register_handlers(self) -> None:
        """
        Registra os handlers para comandos e mensagens.
        """
        # Handlers de comandos
        self.dispatcher.add_handler(CommandHandler("start", start))
        self.dispatcher.add_handler(CommandHandler("listar", listar_ideias))
        self.dispatcher.add_handler(CommandHandler("ver", ver_ideia))
        self.dispatcher.add_handler(CommandHandler("apagar", apagar_ideia))
        self.dispatcher.add_handler(CommandHandler("refazer", refazer_brainstorm))
        self.dispatcher.add_handler(CommandHandler("comandos", listar_comandos))
        self.dispatcher.add_handler(CommandHandler("help", listar_comandos))  # Alias para /comandos
        
        # Handler para mensagens de texto e áudio
        self.dispatcher.add_handler(MessageHandler(
            Filters.text | Filters.voice, handle_message
        ))
        
        logger.info("Handlers registrados com sucesso")
    
    def start(self) -> None:
        """
        Inicia o bot em modo de polling.
        """
        logger.info("Iniciando o bot...")
        self.updater.start_polling()
        
        # Salva o PID para facilitar o gerenciamento do processo
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "cerebro.pid"), "w") as f:
            f.write(str(os.getpid()))
        
        logger.info(f"Bot iniciado com PID {os.getpid()}")
        
        # Bloqueia até que o processo seja interrompido
        self.updater.idle()
    
    def stop(self) -> None:
        """
        Para o bot.
        """
        logger.info("Parando o bot...")
        self.updater.stop()
        logger.info("Bot parado com sucesso")


# Instância global do bot
cerebro_bot = CerebroBot()
