import logging
import openai
import secrets_cerebro
import tempfile
import time
import pytz
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Configuração de logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Chaves de API
TELEGRAM_API_KEY = secrets_cerebro.TELEGRAM_API_KEY
OPENAI_API_KEY = secrets_cerebro.OPENAI_API_KEY
MY_CHAT_ID = secrets_cerebro.MY_CHAT_ID

# Inicializa a API da OpenAI
openai.api_key = OPENAI_API_KEY

def start(update: Update, context: CallbackContext) -> None:
    """Envia mensagem de boas-vindas ao usuário."""
    if update.message.chat_id not in MY_CHAT_ID:
        update.message.reply_text("Acesso não autorizado.")
        return
    update.message.reply_text("Olá! Envie uma mensagem de texto ou áudio para começar.")

def handle_message(update: Update, context: CallbackContext) -> None:
    """Lida com mensagens de texto ou áudio enviadas pelo usuário."""
    if update.message.chat_id not in MY_CHAT_ID:
        update.message.reply_text("Acesso não autorizado.")
        return
    
    if update.message.voice:
        # Baixar e transcrever áudio
        file = context.bot.get_file(update.message.voice.file_id)
        with tempfile.NamedTemporaryFile(delete=True) as temp_audio:
            file.download(out=temp_audio.name)
            temp_audio.flush()
            try:
                logger.info("Transcrevendo áudio...")
                transcription = openai.Audio.transcribe("whisper-1", open(temp_audio.name, "rb"))
                user_message = transcription['text']
                update.message.reply_text(f"Transcrição: {user_message}")
            except Exception as e:
                logger.error(f"Erro na transcrição: {e}")
                update.message.reply_text("Erro ao transcrever o áudio.")
                return
    else:
        user_message = update.message.text
    
    # Chamar OpenAI para gerar resposta
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente."},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response['choices'][0]['message']['content']
        update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"Erro ao gerar resposta do OpenAI: {e}")
        update.message.reply_text("Erro ao gerar resposta. Tente novamente.")

def main():
    """Inicializa o bot."""
    while True:
        try:
            app = Application.builder().token(TELEGRAM_API_KEY).local_timezone(pytz.utc).build()
            app.add_handler(CommandHandler("start", start))
            app.add_handler(MessageHandler(filters.TEXT | filters.VOICE, handle_message))
            
            logger.info("Bot iniciado com sucesso!")
            app.run_polling()
        except Exception as e:
            logger.error(f"Erro na conexão: {e}. Tentando reconectar em 5 segundos...")
            time.sleep(5)  # Espera 5 segundos antes de tentar novamente

if __name__ == "__main__":
    main()
