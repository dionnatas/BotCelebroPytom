"""
Configurações para conexão com o Supabase.
"""
import os
import sys
from typing import Optional
from pathlib import Path

# Adicionar o diretório raiz ao PYTHONPATH para importar secrets_cerebro
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

# Importar a chave de serviço do arquivo secrets_cerebro.py
try:
    from secrets_cerebro import SUPABASE_SERVICE_KEY as SECRET_SERVICE_KEY
except ImportError:
    SECRET_SERVICE_KEY = None

# Substitua estas variáveis com as informações do seu projeto Supabase
SUPABASE_URL = "https://apeivlffyrsiqcnhskvo.supabase.co"

# Chave anônima (pública) - usada para operações normais do cliente
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFwZWl2bGZmeXJzaXFjbmhza3ZvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDEyMDE3MDgsImV4cCI6MjA1Njc3NzcwOH0.0tX6Lfop-D6KuwPLz04lMpfUfBhcNHDVW4Ab7pP8sas"

# Chave de serviço (secreta) - usada para operações administrativas
# Agora obtida do arquivo secrets_cerebro.py para maior segurança
SUPABASE_SERVICE_KEY: Optional[str] = SECRET_SERVICE_KEY

# Configurações das tabelas
TABELA_IDEIAS = "ideias"
TABELA_BRAINSTORMS = "brainstorms"

def get_supabase_key(use_service_key: bool = False) -> str:
    """Retorna a chave apropriada do Supabase.
    
    Args:
        use_service_key: Se True, retorna a chave de serviço (se disponível)
        
    Returns:
        str: A chave do Supabase
    """
    if use_service_key and SUPABASE_SERVICE_KEY:
        return SUPABASE_SERVICE_KEY
    return SUPABASE_KEY
