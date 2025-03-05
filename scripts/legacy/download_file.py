import os
import requests
import logging

logger = logging.getLogger(__name__)

def download_file_func(message, token, output_path=None, overwrite=False):
    """
    Baixa um arquivo de áudio do Telegram.
    
    Args:
        message: Objeto de mensagem do Telegram
        token: Token de API do Telegram
        output_path: Caminho para salvar o arquivo (opcional)
        overwrite: Se True, sobrescreve o arquivo se já existir
    
    Returns:
        str: Caminho do arquivo baixado ou None em caso de erro
    """
    try:
        # Verifica se a mensagem contém áudio ou voz
        if message.audio is not None:
            file_id = message.audio.file_id
            default_filename = f"audio_{message.message_id}.ogg"
        elif message.voice is not None:
            file_id = message.voice.file_id
            default_filename = f"voice_{message.message_id}.ogg"
        else:
            logger.error("Mensagem não contém áudio ou voz")
            return None
        
        # Define o caminho de saída
        if output_path is None:
            output_path = default_filename
        
        # Verifica se o arquivo já existe
        if os.path.exists(output_path) and not overwrite:
            logger.info(f"Arquivo {output_path} já existe e não será sobrescrito")
            return output_path
        
        # Obtém informações do arquivo da API do Telegram
        file_info_url = f"https://api.telegram.org/bot{token}/getFile?file_id={file_id}"
        file_info_response = requests.get(file_info_url)
        
        if not file_info_response.ok:
            logger.error(f"Erro ao obter informações do arquivo: {file_info_response.text}")
            return None
        
        file_info = file_info_response.json()
        
        if not file_info.get('ok'):
            logger.error(f"Erro na resposta da API do Telegram: {file_info}")
            return None
        
        file_path = file_info['result']['file_path']
        
        # Baixa o arquivo
        download_url = f"https://api.telegram.org/file/bot{token}/{file_path}"
        response = requests.get(download_url)
        
        if not response.ok:
            logger.error(f"Erro ao baixar o arquivo: {response.text}")
            return None
        
        # Cria diretórios se necessário
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Salva o arquivo localmente
        with open(output_path, 'wb') as file:
            file.write(response.content)
        
        logger.info(f"Arquivo salvo em {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Erro ao baixar arquivo: {e}")
        return None
    