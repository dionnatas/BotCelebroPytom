"""
Script principal para iniciar o bot Cerebro.
"""
import logging
import os
import sys

# Adiciona o diretório raiz ao path para importações relativas
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config.settings import configure_logging
from src.bot.cerebro_bot import cerebro_bot

def main():
    """
    Função principal para iniciar o bot.
    """
    # Configura o logging
    configure_logging()
    
    logger = logging.getLogger(__name__)
    logger.info("Iniciando o bot Cerebro...")
    
    try:
        # Inicia o bot
        cerebro_bot.start()
    except KeyboardInterrupt:
        logger.info("Bot interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro ao iniciar o bot: {e}", exc_info=True)
    finally:
        logger.info("Bot finalizado")

if __name__ == "__main__":
    main()
