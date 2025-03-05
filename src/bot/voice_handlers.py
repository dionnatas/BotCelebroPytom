"""
Handlers para mensagens de voz do bot Telegram.
"""
import logging
import os
import tempfile
from typing import Optional

from telegram import Update, ParseMode
from telegram.ext import CallbackContext

from src.bot.bot_utils import check_authorization
from src.transcription.transcriber import audio_transcriber

logger = logging.getLogger(__name__)

def handle_voice_message(update: Update, context: CallbackContext) -> None:
    """
    Processa uma mensagem de voz (áudio).
    
    Args:
        update: Objeto Update do Telegram
        context: Contexto do callback
    """
    if not check_authorization(update):
        update.message.reply_text("Você não está autorizado a usar este bot.")
        return
    
    # Verifica se há uma mensagem de voz
    if not update.message.voice:
        update.message.reply_text("Não consegui encontrar o áudio na sua mensagem.")
        return
    
    # Envia mensagem de processamento
    processing_message = update.message.reply_text("🎙️ Processando seu áudio... Isso pode levar alguns segundos.")
    
    try:
        # Obtém o arquivo de áudio
        voice = update.message.voice
        voice_file = context.bot.get_file(voice.file_id)
        
        # Cria um diretório temporário para o arquivo de áudio
        with tempfile.TemporaryDirectory() as temp_dir:
            # Define o caminho para o arquivo de áudio
            audio_path = os.path.join(temp_dir, f"audio_{voice.file_id}.ogg")
            
            # Baixa o arquivo de áudio
            voice_file.download(audio_path)
            
            # Verifica se o arquivo existe
            if not os.path.exists(audio_path):
                update.message.reply_text("❌ Erro ao baixar o arquivo de áudio. Por favor, tente novamente.")
                return
            
            # Transcreve o áudio
            processing_message.edit_text("🔍 Transcrevendo áudio... Isso pode levar alguns segundos.")
            sucesso, transcricao = audio_transcriber.transcrever_audio(audio_path)
            
            if not sucesso:
                update.message.reply_text(
                    f"❌ Erro ao transcrever o áudio: {transcricao}\n\n"
                    "Por favor, tente novamente ou envie uma mensagem de texto."
                )
                return
            
            # Processa a transcrição como uma mensagem de texto
            processing_message.edit_text("✅ Áudio transcrito com sucesso! Processando sua ideia...")
            
            # Envia a transcrição para o usuário
            update.message.reply_text(
                f"🎙️ *Transcrição do seu áudio:*\n\n{transcricao}",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Processa a mensagem transcrita
            from src.bot.message_handlers import process_message
            process_message(update, context, transcricao)
    
    except Exception as e:
        logger.error(f"Erro ao processar mensagem de voz: {str(e)}", exc_info=True)
        update.message.reply_text(
            f"❌ Ocorreu um erro ao processar seu áudio: {str(e)}\n\n"
            "Por favor, tente novamente ou envie uma mensagem de texto."
        )
