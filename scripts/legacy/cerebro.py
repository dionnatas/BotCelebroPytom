"""
Arquivo de compatibilidade para a versão antiga do Cerebro.
Este arquivo permite que o código antigo continue funcionando,
redirecionando para a nova estrutura.
"""
import logging
import os
import sys

# Adiciona o diretório raiz ao path para importações relativas
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configura o logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """
    Função principal para iniciar o bot.
    """
    logger.info("Iniciando o bot Cerebro (modo de compatibilidade)...")
    logger.info("Redirecionando para a nova estrutura...")
    
    try:
        # Importa o módulo principal da nova estrutura
        from main import main as new_main
        
        # Executa a função principal da nova estrutura
        new_main()
    except Exception as e:
        logger.error(f"Erro ao iniciar o bot: {e}", exc_info=True)
        print(f"Erro ao iniciar o bot: {e}")
        print("Verifique os logs para mais detalhes.")

if __name__ == "__main__":
    main()
