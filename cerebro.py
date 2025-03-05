import logging
import os
import tempfile
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import openai
import secrets_cerebro

# Configurações de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Chaves de API e IDs de chat
TELEGRAM_API_KEY = secrets_cerebro.TELEGRAM_API_KEY
OPENAI_API_KEY = secrets_cerebro.OPENAI_API_KEY
MY_CHAT_ID = secrets_cerebro.MY_CHAT_ID

# Inicializa o cliente da OpenAI
openai.api_key = OPENAI_API_KEY

def start(update: Update, context: CallbackContext) -> None:
    """Envia uma mensagem de boas-vindas quando o comando /start é emitido."""
    if update.message.chat_id != MY_CHAT_ID:
        update.message.reply_text("Acesso não autorizado.")
        return
    update.message.reply_text('Olá! Envie uma mensagem de texto ou um áudio para eu processar.')

def handle_message(update: Update, context: CallbackContext) -> None:
    """Processa mensagens de texto e áudio."""
    if update.message.chat_id != MY_CHAT_ID:
        update.message.reply_text("Acesso não autorizado.")
        return

    if update.message.voice:
        # Baixa o arquivo de áudio
        file = context.bot.get_file(update.message.voice.file_id)
        with tempfile.NamedTemporaryFile(delete=True) as temp_audio:
            file.download(out=temp_audio.name)
            temp_audio.flush()
            # Transcreve o áudio usando OpenAI Whisper
            try:
                logger.info("Transcrevendo arquivo de áudio...")
                transcription = openai.Audio.transcribe("whisper-1", open(temp_audio.name, "rb"))
                user_message = transcription['text']
                update.message.reply_text(f"Transcrição: {user_message}")
            except Exception as e:
                logger.error(f"Erro na transcrição: {e}")
                update.message.reply_text("Desculpe, não consegui transcrever o áudio.")
                return
    else:
        user_message = update.message.text

    # Gera a resposta usando o ChatGPT
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente útil."},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message['content'].strip()
        update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"Erro ao gerar resposta: {e}")
        update.message.reply_text("Desculpe, ocorreu um erro ao processar sua mensagem.")

def error_handler(update: Update, context: CallbackContext) -> None:
    """Loga os erros causados por Updates."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    if update and update.message:
        update.message.reply_text('Ocorreu um erro inesperado.')

def main() -> None:
    """Inicia o bot."""
    updater = Updater(TELEGRAM_API_KEY, use_context=True)
    dispatcher = updater.dispatcher

    # Handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text | Filters.voice, handle_message))
    dispatcher.add_error_handler(error_handler)

    # Inicia o polling
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

