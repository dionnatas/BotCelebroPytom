"""
Funções auxiliares para o bot Cerebro.
"""
import logging
import os
import tempfile
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

def criar_arquivo_temporario(suffix: str = None) -> Tuple[bool, Optional[str]]:
    """
    Cria um arquivo temporário com o sufixo especificado.
    
    Args:
        suffix: Sufixo para o arquivo temporário (ex: '.wav', '.ogg')
        
    Returns:
        Tuple[bool, Optional[str]]: Sucesso da operação e caminho do arquivo temporário
    """
    try:
        temp_fd, temp_path = tempfile.mkstemp(suffix=suffix)
        os.close(temp_fd)
        
        logger.info(f"Arquivo temporário criado: {temp_path}")
        return True, temp_path
    except Exception as e:
        logger.error(f"Erro ao criar arquivo temporário: {e}")
        return False, None

def remover_arquivo_temporario(file_path: str) -> bool:
    """
    Remove um arquivo temporário.
    
    Args:
        file_path: Caminho do arquivo a ser removido
        
    Returns:
        bool: True se o arquivo foi removido com sucesso, False caso contrário
    """
    if not file_path or not os.path.exists(file_path):
        logger.warning(f"Arquivo não existe para remoção: {file_path}")
        return False
    
    try:
        os.remove(file_path)
        logger.info(f"Arquivo temporário removido: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Erro ao remover arquivo temporário {file_path}: {e}")
        return False

def verificar_arquivo(file_path: str) -> Tuple[bool, int]:
    """
    Verifica se um arquivo existe e retorna seu tamanho.
    
    Args:
        file_path: Caminho do arquivo a ser verificado
        
    Returns:
        Tuple[bool, int]: True se o arquivo existe, e seu tamanho em bytes
    """
    if not file_path or not os.path.exists(file_path):
        logger.warning(f"Arquivo não existe: {file_path}")
        return False, 0
    
    try:
        size = os.path.getsize(file_path)
        logger.info(f"Arquivo verificado: {file_path}, tamanho: {size} bytes")
        return True, size
    except Exception as e:
        logger.error(f"Erro ao verificar arquivo {file_path}: {e}")
        return False, 0
