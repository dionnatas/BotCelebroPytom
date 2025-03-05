import logging
import openai
import secrets_cerebro
import tempfile
import time
import json
import sqlite3
import requests
import re
from datetime import datetime
from telegram import Update

# Compatibilidade com diferentes versões da biblioteca python-telegram-bot
try:
    from telegram import ParseMode
except ImportError:
    # Para versões mais recentes da biblioteca
    from telegram.constants import ParseMode
except ImportError:
    # Fallback se não conseguir importar de nenhum lugar
    class ParseMode:
        HTML = "HTML"
        MARKDOWN = "Markdown"
        MARKDOWN_V2 = "MarkdownV2"

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from prompts import prompt_classificador, prompt_brainstorm

# Configuração de logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Chaves de API
TELEGRAM_API_KEY = secrets_cerebro.TELEGRAM_API_KEY
OPENAI_API_KEY = secrets_cerebro.OPENAI_API_KEY
MY_CHAT_ID = secrets_cerebro.MY_CHAT_ID

# Configuração da API da OpenAI
openai.api_key = OPENAI_API_KEY

# Verifica a versão da API OpenAI
try:
    openai_version = openai.__version__
    logger.info(f"Usando OpenAI API versão: {openai_version}")
except AttributeError:
    logger.info("Não foi possível determinar a versão da API OpenAI")

# Inicializa o banco de dados
def init_db():
    """Inicializa o banco de dados SQLite."""
    conn = sqlite3.connect('cerebro.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ideias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL,
        conteudo TEXT NOT NULL,
        resumo TEXT NOT NULL,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS brainstorms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ideia_id INTEGER,
        conteudo TEXT NOT NULL,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (ideia_id) REFERENCES ideias (id)
    )
    ''')
    conn.commit()
    conn.close()

def salvar_ideia(tipo, conteudo, resumo):
    """Salva uma ideia no banco de dados."""
    conn = sqlite3.connect('cerebro.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO ideias (tipo, conteudo, resumo) VALUES (?, ?, ?)",
        (tipo, conteudo, resumo)
    )
    ideia_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return ideia_id

def salvar_brainstorm(ideia_id, conteudo):
    """Salva um brainstorm no banco de dados."""
    conn = sqlite3.connect('cerebro.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO brainstorms (ideia_id, conteudo) VALUES (?, ?)",
        (ideia_id, conteudo)
    )
    conn.commit()
    conn.close()

def classificar_mensagem(texto):
    """Classifica a mensagem usando o modelo de IA."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt_classificador},
                {"role": "user", "content": texto}
            ]
        )
        
        resultado = response['choices'][0]['message']['content'].strip()
        # Tenta converter o resultado para uma lista
        try:
            # Remove os colchetes extras se houver
            if resultado.startswith('[') and resultado.endswith(']'):
                resultado = resultado[1:-1]
            
            # Divide a string em partes e limpa cada parte
            partes = resultado.split(',', 2)
            tipo = partes[0].strip().strip('"[]')
            conteudo = partes[1].strip().strip('"[]')
            resumo = partes[2].strip().strip('"[]')
            
            return tipo, conteudo, resumo
        except Exception as e:
            logger.error(f"Erro ao processar resultado da classificação: {e}")
            return "QUESTAO", texto, texto
    except Exception as e:
        logger.error(f"Erro ao classificar mensagem: {e}")
        return "QUESTAO", texto, texto

def gerar_brainstorm(ideia):
    """Gera um brainstorm para uma ideia usando o modelo de IA."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt_brainstorm},
                {"role": "user", "content": ideia}
            ]
        )
        
        return response['choices'][0]['message']['content']
    except Exception as e:
        logger.error(f"Erro ao gerar brainstorm: {e}")
        return "Erro ao gerar brainstorm. Tente novamente."

def start(update: Update, context: CallbackContext) -> None:
    """Envia mensagem de boas-vindas ao usuário."""
    chat_id = update.effective_chat.id
    authorized = False
    
    if isinstance(MY_CHAT_ID, list):
        authorized = chat_id in MY_CHAT_ID
    else:
        authorized = chat_id == MY_CHAT_ID
        
    if not authorized:
        update.message.reply_text("Acesso não autorizado.")
        return
    update.message.reply_text("Olá! Envie uma mensagem de texto ou áudio para começar.")

def handle_message(update: Update, context: CallbackContext) -> None:
    """Lida com mensagens de texto ou áudio enviadas pelo usuário."""
    chat_id = update.effective_chat.id
    authorized = False
    
    if isinstance(MY_CHAT_ID, list):
        authorized = chat_id in MY_CHAT_ID
    else:
        authorized = chat_id == MY_CHAT_ID
        
    if not authorized:
        update.message.reply_text("Acesso não autorizado.")
        return
    
    if update.message.voice:
        try:
            file = context.bot.get_file(update.message.voice.file_id)
            with tempfile.NamedTemporaryFile(delete=True, suffix='.ogg') as temp_audio:
                file.download(out=temp_audio.name)
                temp_audio.flush()
                
                logger.info("Transcrevendo áudio...")
                # Verifica a versão da API OpenAI e usa o método apropriado
                try:
                    # Para versão 0.28.0 ou anterior
                    with open(temp_audio.name, "rb") as audio_file:
                        transcription = openai.Audio.transcribe(
                            "whisper-1", 
                            audio_file
                        )
                    user_message = transcription.get('text', '')
                    logger.info(f"Transcrição bem-sucedida usando método antigo: {user_message[:30]}...")
                except (AttributeError, TypeError) as e:
                    logger.info(f"Tentando método alternativo de transcrição: {e}")
                    try:
                        # Para versões mais recentes da API
                        with open(temp_audio.name, "rb") as audio_file:
                            # Cria uma cópia temporária do arquivo para evitar problemas de seek
                            audio_data = audio_file.read()
                        
                        # Usa o método mais recente da API
                        import io
                        audio_bytes = io.BytesIO(audio_data)
                        audio_bytes.name = "audio.ogg"  # Nome necessário para alguns clientes da API
                        
                        try:
                            # Tenta o método da API v1
                            transcription = openai.audio.transcriptions.create(
                                model="whisper-1",
                                file=audio_bytes
                            )
                            user_message = transcription.text if hasattr(transcription, 'text') else str(transcription)
                            logger.info(f"Transcrição bem-sucedida usando método v1: {user_message[:30]}...")
                        except Exception as e3:
                            logger.info(f"Tentando método final de transcrição: {e3}")
                            # Última tentativa - método mais básico
                            import requests
                            
                            headers = {
                                "Authorization": f"Bearer {OPENAI_API_KEY}"
                            }
                            
                            audio_bytes.seek(0)  # Reinicia a posição do buffer
                            files = {
                                "file": ("audio.ogg", audio_bytes, "audio/ogg")
                            }
                            data = {
                                "model": "whisper-1"
                            }
                            
                            response = requests.post(
                                "https://api.openai.com/v1/audio/transcriptions",
                                headers=headers,
                                files=files,
                                data=data
                            )
                            
                            if response.status_code == 200:
                                result = response.json()
                                user_message = result.get("text", "")
                                logger.info(f"Transcrição bem-sucedida usando requests: {user_message[:30]}...")
                            else:
                                logger.error(f"Erro na API: {response.status_code} - {response.text}")
                                raise Exception(f"Erro na API: {response.status_code}")
                    except Exception as e2:
                        logger.error(f"Todos os métodos de transcrição falharam: {e2}")
                        raise
                
                if not user_message:
                    update.message.reply_text("Erro: A transcrição do áudio retornou vazia.")
                    return
                
                update.message.reply_text(f"Transcrição: {user_message}")
        except Exception as e:
            logger.error(f"Erro na transcrição: {e}")
            update.message.reply_text(
                "Erro ao transcrever o áudio. Por favor, tente novamente ou envie sua mensagem como texto.\n"
                "Se o problema persistir, verifique se a versão da biblioteca OpenAI é compatível (0.28.0 recomendada)."
            )
            return
    else:
        user_message = update.message.text
    
    # Classificar a mensagem
    tipo, conteudo, resumo = classificar_mensagem(user_message)
    
    # Salvar a ideia no banco de dados
    ideia_id = salvar_ideia(tipo, conteudo, resumo)
    
    if tipo == "IDEIA":
        update.message.reply_text(
            f"Identifiquei uma ideia: *{resumo}*\n\n"
            f"Deseja fazer um brainstorm sobre essa ideia? Responda com 'sim' ou 'não'.",
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['ultima_ideia'] = {
            'id': ideia_id,
            'conteudo': conteudo,
            'resumo': resumo
        }
    else:
        # Chamar OpenAI para gerar resposta para a questão
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um assistente útil e informativo."},
                    {"role": "user", "content": user_message}
                ]
            )
            
            reply = response['choices'][0]['message']['content']
            update.message.reply_text(reply)
        except Exception as e:
            logger.error(f"Erro ao gerar resposta do OpenAI: {e}")
            update.message.reply_text("Erro ao gerar resposta. Tente novamente.")

def handle_brainstorm_response(update: Update, context: CallbackContext) -> None:
    """Lida com a resposta do usuário sobre fazer brainstorm."""
    chat_id = update.effective_chat.id
    authorized = False
    
    if isinstance(MY_CHAT_ID, list):
        authorized = chat_id in MY_CHAT_ID
    else:
        authorized = chat_id == MY_CHAT_ID
        
    if not authorized:
        update.message.reply_text("Acesso não autorizado.")
        return
    
    if 'ultima_ideia' not in context.user_data:
        update.message.reply_text("Não encontrei nenhuma ideia recente para fazer brainstorm.")
        return
    
    resposta = update.message.text.lower()
    if resposta in ['sim', 's', 'yes', 'y']:
        ideia = context.user_data['ultima_ideia']['conteudo']
        update.message.reply_text("Gerando brainstorm... Isso pode levar alguns segundos.")
        
        brainstorm = gerar_brainstorm(ideia)
        
        # Salvar o brainstorm no banco de dados
        salvar_brainstorm(context.user_data['ultima_ideia']['id'], brainstorm)
        
        update.message.reply_text(
            f"*Brainstorm para: {context.user_data['ultima_ideia']['resumo']}*\n\n{brainstorm}",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Limpar a última ideia
        del context.user_data['ultima_ideia']
    elif resposta in ['não', 'nao', 'n', 'no']:
        update.message.reply_text("Ok, a ideia foi salva para referência futura.")
        # Limpar a última ideia
        del context.user_data['ultima_ideia']

def listar_ideias(update: Update, context: CallbackContext) -> None:
    """Lista as ideias salvas no banco de dados."""
    chat_id = update.effective_chat.id
    authorized = False
    
    if isinstance(MY_CHAT_ID, list):
        authorized = chat_id in MY_CHAT_ID
    else:
        authorized = chat_id == MY_CHAT_ID
        
    if not authorized:
        update.message.reply_text("Acesso não autorizado.")
        return
    
    conn = sqlite3.connect('cerebro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, tipo, resumo, data FROM ideias ORDER BY data DESC LIMIT 10")
    ideias = cursor.fetchall()
    conn.close()
    
    if not ideias:
        update.message.reply_text("Não há ideias salvas.")
        return
    
    mensagem = "*Últimas ideias:*\n\n"
    for ideia in ideias:
        data = datetime.strptime(ideia[3], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
        mensagem += f"*{ideia[0]}.* [{ideia[1]}] {ideia[2]} - {data}\n"
    
    update.message.reply_text(mensagem, parse_mode=ParseMode.MARKDOWN)

def ver_ideia(update: Update, context: CallbackContext) -> None:
    """Mostra os detalhes de uma ideia específica."""
    chat_id = update.effective_chat.id
    authorized = False
    
    if isinstance(MY_CHAT_ID, list):
        authorized = chat_id in MY_CHAT_ID
    else:
        authorized = chat_id == MY_CHAT_ID
        
    if not authorized:
        update.message.reply_text("Acesso não autorizado.")
        return
    
    args = context.args
    if not args or not args[0].isdigit():
        update.message.reply_text("Por favor, forneça o ID da ideia que deseja visualizar.")
        return
    
    ideia_id = int(args[0])
    
    conn = sqlite3.connect('cerebro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT tipo, conteudo, resumo, data FROM ideias WHERE id = ?", (ideia_id,))
    ideia = cursor.fetchone()
    
    if not ideia:
        update.message.reply_text(f"Ideia com ID {ideia_id} não encontrada.")
        conn.close()
        return
    
    cursor.execute("SELECT conteudo, data FROM brainstorms WHERE ideia_id = ? ORDER BY data DESC", (ideia_id,))
    brainstorms = cursor.fetchall()
    conn.close()
    
    # Formata a data da ideia
    data = datetime.strptime(ideia[3], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
    
    # Prepara a mensagem principal com os detalhes da ideia
    mensagem = f"*Ideia {ideia_id}*\n\n"
    mensagem += f"*Tipo:* {ideia[0]}\n"
    mensagem += f"*Resumo:* {ideia[2]}\n"
    mensagem += f"*Data:* {data}\n\n"
    mensagem += f"*Conteúdo:*\n{ideia[1]}\n\n"
    
    # Envia a primeira mensagem com os detalhes da ideia
    update.message.reply_text(mensagem, parse_mode=ParseMode.MARKDOWN)
    
    # Se houver brainstorms, envia cada um em uma mensagem separada
    if brainstorms:
        for i, brainstorm in enumerate(brainstorms):
            data_bs = datetime.strptime(brainstorm[1], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
            bs_mensagem = f"*Brainstorm {i+1} para Ideia {ideia_id}* - {data_bs}\n\n{brainstorm[0]}"
            
            # Divide a mensagem em partes se for muito grande
            if len(bs_mensagem) > 4000:  # Limite do Telegram é ~4096 caracteres
                partes = [bs_mensagem[i:i+4000] for i in range(0, len(bs_mensagem), 4000)]
                for j, parte in enumerate(partes):
                    # Adiciona cabeçalho para partes subsequentes
                    if j > 0:
                        parte = f"*Brainstorm {i+1} (continuação {j+1})* para Ideia {ideia_id}\n\n{parte}"
                    update.message.reply_text(parte, parse_mode=ParseMode.MARKDOWN)
            else:
                update.message.reply_text(bs_mensagem, parse_mode=ParseMode.MARKDOWN)
    else:
        update.message.reply_text("Esta ideia não possui brainstorms associados.")

def main():
    """Inicializa o bot."""
    # Inicializa o banco de dados
    init_db()
    
    # Inicializa o bot
    updater = Updater(token=TELEGRAM_API_KEY, use_context=True)
    dispatcher = updater.dispatcher
    
    # Adiciona os handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("listar", listar_ideias))
    dispatcher.add_handler(CommandHandler("ver", ver_ideia))
    
    # Adiciona handler para respostas de brainstorm
    # Cria um padrão regex com flag de case insensitive
    pattern = re.compile('^(sim|s|yes|y|não|nao|n|no)$', re.IGNORECASE)
    dispatcher.add_handler(MessageHandler(Filters.text & (Filters.regex(pattern)), handle_brainstorm_response))
    
    # Adiciona handler para mensagens gerais
    dispatcher.add_handler(MessageHandler(Filters.text | Filters.voice, handle_message))
    
    # Inicia o bot
    logger.info("Bot iniciado com sucesso!")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()