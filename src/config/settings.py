"""
Configurações do bot Cerebro.
"""
import logging
import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao sys.path para importações relativas
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

try:
    from secrets_cerebro import TELEGRAM_API_KEY, OPENAI_API_KEY, MY_CHAT_ID, SUPERUSERS_CHAT_ID
except ImportError:
    logging.error("Arquivo secrets_cerebro.py não encontrado ou não contém as chaves necessárias.")
    TELEGRAM_API_KEY = os.environ.get("TELEGRAM_API_KEY", "")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    MY_CHAT_ID = os.environ.get("MY_CHAT_ID", "")
    SUPERUSERS_CHAT_ID = os.environ.get("SUPERUSERS_CHAT_ID", "")

# Diretórios para arquivos de dados
VAR_DIR = BASE_DIR / "var"
LOGS_DIR = VAR_DIR / "logs"
DB_DIR = VAR_DIR / "db"
RUN_DIR = VAR_DIR / "run"

# Cria diretórios se não existirem
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(RUN_DIR, exist_ok=True)

# Função para configurar o logging
def configure_logging(log_file="var/logs/cerebro.log"):
    """
    Configura o logging para o bot Cerebro.
    
    Args:
        log_file (str): Nome do arquivo de log. Padrão: "cerebro.log"
    """
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

# Configura o logging
logger = configure_logging()

# Verifica se as chaves de API estão definidas
if not TELEGRAM_API_KEY:
    logger.error("TELEGRAM_API_KEY não está definida ou está vazia!")
    raise ValueError("TELEGRAM_API_KEY não está definida ou está vazia!")

if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY não está definida ou está vazia!")
    raise ValueError("OPENAI_API_KEY não está definida ou está vazia!")
else:
    logger.info(f"OPENAI_API_KEY está definida e tem {len(OPENAI_API_KEY)} caracteres")

# Configurações do banco de dados
DB_PATH = BASE_DIR / "var/db/cerebro.db"

# Configuração para usar Supabase em vez do SQLite
USE_SUPABASE = True  # Mude para False para usar o SQLite local

# Configurações da OpenAI
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_WHISPER_MODEL = "whisper-1"
OPENAI_TEMPERATURE = 0.7

# Configurações de transcrição de áudio
AUDIO_FORMATS = ["ogg", "mp3", "wav", "m4a"]
WHISPER_SAMPLE_RATE = 16000
