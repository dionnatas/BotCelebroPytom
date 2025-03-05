"""
Handlers para os comandos e mensagens do bot Telegram.
"""
import logging
import os
import tempfile
from typing import Optional

from telegram import Update, ParseMode
from telegram.ext import CallbackContext

from src.config.settings import MY_CHAT_ID
from src.database.db_manager import db_manager
from src.services.openai_service import openai_service
from src.transcription.transcriber import audio_transcriber

logger = logging.getLogger(__name__)

def check_authorization(update: Update) -> bool:
    """
    Verifica se o usuário está autorizado a usar o bot.
    
    Args:
        update: Objeto Update do Telegram
        
    Returns:
        bool: True se autorizado, False caso contrário
    """
    chat_id = update.effective_chat.id
    authorized = False
    
    if isinstance(MY_CHAT_ID, list):
        authorized = chat_id in MY_CHAT_ID
    else:
        authorized = chat_id == MY_CHAT_ID
        
    if not authorized:
        update.message.reply_text("Acesso não autorizado.")
        logger.warning(f"Tentativa de acesso não autorizado do chat_id: {chat_id}")
    
    return authorized

def start(update: Update, context: CallbackContext) -> None:
    """
    Envia mensagem de boas-vindas ao usuário.
    
    Args:
        update: Objeto Update do Telegram
        context: Contexto do callback
    """
    if not check_authorization(update):
        return
    
    update.message.reply_text(
        "Olá! Eu sou o Cerebro, seu assistente para capturar e organizar ideias.\n\n"
        "Você pode me enviar mensagens de texto ou áudio, e eu vou classificá-las e armazená-las.\n\n"
        "Comandos principais:\n"
        "/start - Exibe esta mensagem de boas-vindas\n"
        "/comandos - Mostra a lista completa de comandos disponíveis\n"
        "/listar - Lista suas ideias salvas\n"
        "/ver [id] - Mostra detalhes de uma ideia específica\n"
        "/apagar [id] - Apaga uma ideia específica"
    )

def process_message(update: Update, context: CallbackContext, message_text: str) -> None:
    """
    Processa uma mensagem de texto.
    
    Args:
        update: Objeto Update do Telegram
        context: Contexto do callback
        message_text: Texto da mensagem a ser processada
    """
    # Classifica a mensagem
    tipo, conteudo, resumo = openai_service.classificar_mensagem(message_text)
    
    # Salva a ideia no banco de dados
    ideia_id = db_manager.salvar_ideia(tipo, conteudo, resumo)
    
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
        update.message.reply_text(
            f"Identifiquei uma questão: *{resumo}*\n\n"
            f"Salvei isso para você. Use /listar para ver todas as suas ideias e questões.",
            parse_mode=ParseMode.MARKDOWN
        )

def handle_message(update: Update, context: CallbackContext) -> None:
    """
    Lida com mensagens de texto ou áudio enviadas pelo usuário.
    
    Args:
        update: Objeto Update do Telegram
        context: Contexto do callback
    """
    if not check_authorization(update):
        return
    
    # Verifica se estamos aguardando confirmação para apagar uma ideia
    if 'ideia_para_apagar' in context.user_data and update.message.text:
        confirmar_apagar_ideia(update, context)
        return
    
    # Verifica se a mensagem é uma resposta a um brainstorm
    if 'ultima_ideia' in context.user_data and update.message.text:
        resposta = update.message.text.lower()
        if resposta in ['sim', 'yes', 's', 'y']:
            return handle_brainstorm_response(update, context)
    
    # Processa mensagem de voz (áudio)
    if update.message.voice:
        handle_voice_message(update, context)
    # Processa mensagem de texto
    elif update.message.text:
        process_message(update, context, update.message.text)

def handle_voice_message(update: Update, context: CallbackContext) -> None:
    """
    Processa uma mensagem de voz (áudio).
    
    Args:
        update: Objeto Update do Telegram
        context: Contexto do callback
    """
    import requests
    import subprocess
    
    user_id = update.effective_user.id
    username = update.effective_user.username or f"user_{user_id}"
    
    logger.info(f"Mensagem de voz recebida de {username} (ID: {user_id})")
    update.message.reply_text("Processando seu áudio, por favor aguarde...")
    
    temp_audio_path = None
    
    try:
        # Obtém informações sobre o arquivo de áudio
        voice_file_id = update.message.voice.file_id
        voice_duration = update.message.voice.duration
        logger.info(f"Arquivo de áudio do Telegram: ID={voice_file_id}, Duração={voice_duration}s")
        
        # Obtém o token do bot a partir do contexto
        bot_token = context.bot.token
        
        # Obtém informações do arquivo usando a API do Telegram
        file_info_url = f"https://api.telegram.org/bot{bot_token}/getFile?file_id={voice_file_id}"
        file_info_response = requests.get(file_info_url)
        
        if file_info_response.status_code != 200:
            logger.error(f"Erro ao obter informações do arquivo: {file_info_response.status_code}")
            update.message.reply_text("Erro ao processar seu áudio. Por favor, tente novamente.")
            return
        
        file_info = file_info_response.json()
        logger.info(f"Informações do arquivo: {file_info}")
        
        file_path = file_info.get('result', {}).get('file_path')
        if not file_path:
            logger.error("Não foi possível obter o caminho do arquivo")
            update.message.reply_text("Erro ao processar seu áudio. Por favor, tente novamente.")
            return
        
        logger.info(f"Caminho do arquivo no servidor do Telegram: {file_path}")
        
        # URL para download direto do arquivo
        file_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
        
        # Cria um arquivo temporário para o áudio original
        temp_fd, temp_audio_path = tempfile.mkstemp(suffix='.ogg')
        os.close(temp_fd)
        
        # Baixa o arquivo usando requests
        try:
            logger.info(f"Baixando arquivo de {file_url}")
            download_response = requests.get(file_url, stream=True)
            
            if download_response.status_code != 200:
                logger.error(f"Erro ao baixar arquivo: {download_response.status_code}")
                update.message.reply_text("Erro ao processar seu áudio. Por favor, tente novamente.")
                return
            
            # Salva o arquivo baixado
            with open(temp_audio_path, 'wb') as f:
                for chunk in download_response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Verifica o tamanho do arquivo baixado
            file_size = os.path.getsize(temp_audio_path)
            logger.info(f"Arquivo baixado para {temp_audio_path} ({file_size} bytes)")
            
            if file_size == 0:
                logger.error("Arquivo baixado tem tamanho zero")
                update.message.reply_text("Erro ao processar seu áudio. Por favor, tente novamente.")
                return
            
            # Verifica o formato do arquivo
            try:
                result = subprocess.run(['file', temp_audio_path], capture_output=True, text=True, check=True)
                formato = result.stdout.strip()
                logger.info(f"Formato do arquivo: {formato}")
            except Exception as e:
                logger.warning(f"Não foi possível verificar o formato do arquivo: {e}")
        
        except Exception as e:
            logger.error(f"Erro ao baixar arquivo de áudio: {e}")
            update.message.reply_text("Erro ao processar seu áudio. Por favor, tente novamente.")
            return
        
        # Salva uma cópia do áudio para testes
        test_audio_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "test_audio")
        os.makedirs(test_audio_dir, exist_ok=True)
        test_audio_path = os.path.join(test_audio_dir, "telegram_audio.ogg")
        
        try:
            # Verifica o formato do arquivo usando o comando 'file'
            try:
                result = subprocess.run(['file', temp_audio_path], capture_output=True, text=True, check=True)
                formato = result.stdout.strip()
                logger.info(f"Formato do arquivo: {formato}")
            except Exception as e:
                logger.warning(f"Não foi possível verificar o formato do arquivo: {e}")
            
            # Copia o arquivo usando modo binário para garantir que todos os bytes sejam copiados
            with open(temp_audio_path, 'rb') as src_file:
                with open(test_audio_path, 'wb') as dst_file:
                    conteudo = src_file.read()
                    logger.info(f"Lendo {len(conteudo)} bytes do arquivo original")
                    dst_file.write(conteudo)
            
            # Verifica se a cópia foi bem-sucedida
            if os.path.exists(test_audio_path) and os.path.getsize(test_audio_path) > 0:
                logger.info(f"Cópia do áudio salva para testes em: {test_audio_path} ({os.path.getsize(test_audio_path)} bytes)")
            else:
                logger.error(f"Cópia do áudio falhou: arquivo vazio ou inexistente")
        except Exception as e:
            logger.error(f"Erro ao salvar cópia do áudio para testes: {e}")
        
        # Verifica se o arquivo existe e tem tamanho válido
        if not os.path.exists(temp_audio_path) or os.path.getsize(temp_audio_path) == 0:
            logger.error(f"Arquivo de áudio inválido: {temp_audio_path}")
            update.message.reply_text("Erro: O arquivo de áudio não pôde ser processado. Por favor, tente novamente.")
            return
        
        logger.info(f"Arquivo de áudio válido: {temp_audio_path} ({os.path.getsize(temp_audio_path)} bytes)")
        
        # Transcreve o áudio
        success, transcription = audio_transcriber.transcrever_audio(temp_audio_path)
        
        if success and transcription:
            logger.info(f"Transcrição bem-sucedida: '{transcription}'")
            
            # Processa a mensagem transcrita como texto
            process_message(update, context, transcription)
        else:
            logger.error("Falha na transcrição do áudio")
            update.message.reply_text(
                "Erro: Não foi possível transcrever o áudio. Por favor, tente novamente com um áudio mais claro ou:"
                "\n- Verifique se o áudio tem boa qualidade"
                "\n- Certifique-se de que o áudio contém fala clara"
                "\n- Tente gravar em um ambiente com menos ruído"
            )
    
    except Exception as e:
        logger.error(f"Erro ao processar áudio: {e}")
        update.message.reply_text(
            "Erro ao processar seu áudio. Por favor, tente novamente ou envie sua mensagem como texto."
        )
    
    finally:
        # Limpa os arquivos temporários apenas se a cópia foi salva com sucesso
        if 'test_audio_path' in locals() and os.path.exists(test_audio_path) and os.path.getsize(test_audio_path) > 0:
            if temp_audio_path and os.path.exists(temp_audio_path):
                try:
                    os.remove(temp_audio_path)
                    logger.info(f"Arquivo temporário removido: {temp_audio_path}")
                except Exception as e:
                    logger.error(f"Erro ao remover arquivo temporário: {e}")
        else:
            logger.warning(f"Mantendo arquivo temporário {temp_audio_path} pois a cópia não foi salva com sucesso")

def handle_brainstorm_response(update: Update, context: CallbackContext) -> None:
    """
    Lida com a resposta do usuário sobre fazer brainstorm.
    
    Args:
        update: Objeto Update do Telegram
        context: Contexto do callback
    """
    if 'ultima_ideia' not in context.user_data:
        update.message.reply_text("Não encontrei uma ideia recente para fazer brainstorm.")
        return
    
    ideia = context.user_data['ultima_ideia']
    
    update.message.reply_text(
        f"Gerando brainstorm para a ideia: *{ideia['resumo']}*\n\n"
        "Isso pode levar alguns segundos...",
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Gera o brainstorm
    brainstorm_text = openai_service.gerar_brainstorm(ideia['conteudo'])
    
    # Salva o brainstorm no banco de dados
    db_manager.salvar_brainstorm(ideia['id'], brainstorm_text)
    
    # Envia o brainstorm para o usuário
    update.message.reply_text(
        f"*Brainstorm para: {ideia['resumo']}*\n\n{brainstorm_text}",
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Limpa a última ideia do contexto
    del context.user_data['ultima_ideia']

def listar_ideias(update: Update, context: CallbackContext) -> None:
    """
    Lista as ideias salvas no banco de dados.
    
    Args:
        update: Objeto Update do Telegram
        context: Contexto do callback
    """
    if not check_authorization(update):
        return
    
    ideias = db_manager.listar_ideias(limite=20)
    
    if not ideias:
        update.message.reply_text("Você ainda não tem ideias salvas.")
        return
    
    mensagem = "*Suas ideias salvas:*\n\n"
    
    for ideia in ideias:
        tipo_emoji = "💡" if ideia['tipo'] == "IDEIA" else "❓"
        data_formatada = ideia['data_criacao'].split(" ")[0] if isinstance(ideia['data_criacao'], str) else ideia['data_criacao'].strftime("%Y-%m-%d")
        
        mensagem += f"{tipo_emoji} *ID {ideia['id']}*: {ideia['resumo']} ({data_formatada})\n"
    
    mensagem += "\nPara ver detalhes de uma ideia, use o comando /ver seguido do ID."
    
    update.message.reply_text(mensagem, parse_mode=ParseMode.MARKDOWN)

def apagar_ideia(update: Update, context: CallbackContext) -> None:
    """
    Apaga uma ideia e seus brainstorms relacionados.
    
    Args:
        update: Objeto Update do Telegram
        context: Contexto do callback
    """
    if not check_authorization(update):
        return
    
    # Verifica se foi fornecido um ID
    if not context.args or not context.args[0].isdigit():
        update.message.reply_text(
            "Por favor, forneça o ID da ideia que deseja apagar.\n"
            "Exemplo: /apagar 123"
        )
        return
    
    ideia_id = int(context.args[0])
    
    # Obtém a ideia para confirmar antes de apagar
    ideia = db_manager.obter_ideia(ideia_id)
    if not ideia:
        update.message.reply_text(f"Ideia com ID {ideia_id} não encontrada.")
        return
    
    # Pede confirmação antes de apagar
    context.user_data['ideia_para_apagar'] = ideia_id
    
    update.message.reply_text(
        f"Você está prestes a apagar a ideia:\n\n"
        f"*{ideia['resumo']}*\n\n"
        f"Esta ação não pode ser desfeita. Para confirmar, responda com 'confirmar'.\n"
        f"Para cancelar, responda com qualquer outra mensagem.",
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Registra o próximo handler para processar a confirmação
    return 'AGUARDANDO_CONFIRMACAO'

def confirmar_apagar_ideia(update: Update, context: CallbackContext) -> None:
    """
    Confirma a exclusão de uma ideia após o usuário confirmar.
    
    Args:
        update: Objeto Update do Telegram
        context: Contexto do callback
    """
    if 'ideia_para_apagar' not in context.user_data:
        update.message.reply_text("Nenhuma ideia selecionada para apagar.")
        return
    
    resposta = update.message.text.lower().strip()
    
    if resposta == 'confirmar':
        ideia_id = context.user_data['ideia_para_apagar']
        sucesso = db_manager.apagar_ideia(ideia_id)
        
        if sucesso:
            update.message.reply_text(f"✅ Ideia {ideia_id} apagada com sucesso!")
        else:
            update.message.reply_text(f"❌ Erro ao apagar a ideia {ideia_id}. Tente novamente mais tarde.")
    else:
        update.message.reply_text("Operação cancelada. A ideia não foi apagada.")
    
    # Limpa os dados temporários
    if 'ideia_para_apagar' in context.user_data:
        del context.user_data['ideia_para_apagar']

def listar_comandos(update: Update, context: CallbackContext) -> None:
    """
    Lista todos os comandos disponíveis no bot.
    
    Args:
        update: Objeto Update do Telegram
        context: Contexto do callback
    """
    if not check_authorization(update):
        return
    
    comandos = [
        ("/start", "Inicia o bot e exibe mensagem de boas-vindas"),
        ("/listar", "Lista todas as suas ideias salvas"),
        ("/ver ID", "Mostra os detalhes de uma ideia específica"),
        ("/apagar ID", "Apaga uma ideia e seus brainstorms relacionados"),
        ("/comandos", "Mostra esta lista de comandos disponíveis")
    ]
    
    mensagem = "*Comandos disponíveis:*\n\n"
    
    for comando, descricao in comandos:
        mensagem += f"{comando} - {descricao}\n"
    
    mensagem += "\n*Como usar:*\n"
    mensagem += "• Envie uma mensagem de texto para registrar uma ideia\n"
    mensagem += "• Envie uma mensagem de voz para transcrição automática\n"
    mensagem += "• Após registrar uma ideia, o bot perguntará se você deseja fazer um brainstorm\n"
    
    update.message.reply_text(mensagem, parse_mode=ParseMode.MARKDOWN)

def ver_ideia(update: Update, context: CallbackContext) -> None:
    """
    Mostra os detalhes de uma ideia específica.
    
    Args:
        update: Objeto Update do Telegram
        context: Contexto do callback
    """
    if not check_authorization(update):
        return
    
    # Verifica se o ID foi fornecido
    if not context.args or not context.args[0].isdigit():
        update.message.reply_text(
            "Por favor, forneça o ID da ideia que deseja visualizar.\n"
            "Exemplo: /ver 42"
        )
        return
    
    ideia_id = int(context.args[0])
    ideia = db_manager.obter_ideia(ideia_id)
    
    if not ideia:
        update.message.reply_text(f"Ideia com ID {ideia_id} não encontrada.")
        return
    
    # Formata a data
    data_formatada = ideia['data_criacao'].split(" ")[0] if isinstance(ideia['data_criacao'], str) else ideia['data_criacao'].strftime("%Y-%m-%d %H:%M")
    
    # Prepara a mensagem
    tipo_emoji = "💡" if ideia['tipo'] == "IDEIA" else "❓"
    mensagem = f"{tipo_emoji} *{ideia['resumo']}*\n"
    mensagem += f"*ID:* {ideia['id']}\n"
    mensagem += f"*Tipo:* {ideia['tipo']}\n"
    mensagem += f"*Data:* {data_formatada}\n\n"
    mensagem += f"*Conteúdo:*\n{ideia['conteudo']}\n\n"
    
    # Adiciona brainstorms, se existirem
    if 'brainstorms' in ideia and ideia['brainstorms']:
        mensagem += "*Brainstorms:*\n\n"
        for i, brainstorm in enumerate(ideia['brainstorms']):
            data_bs = brainstorm['data_criacao'].split(" ")[0] if isinstance(brainstorm['data_criacao'], str) else brainstorm['data_criacao'].strftime("%Y-%m-%d")
            mensagem += f"*Brainstorm {i+1}* ({data_bs}):\n{brainstorm['conteudo']}\n\n"
    
    # Se for uma ideia sem brainstorm, oferece a opção
    elif ideia['tipo'] == "IDEIA" and ('brainstorms' not in ideia or not ideia['brainstorms']):
        mensagem += "Deseja fazer um brainstorm sobre essa ideia? Responda com 'sim'."
        context.user_data['ultima_ideia'] = {
            'id': ideia['id'],
            'conteudo': ideia['conteudo'],
            'resumo': ideia['resumo']
        }
    
    update.message.reply_text(mensagem, parse_mode=ParseMode.MARKDOWN)
