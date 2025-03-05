"""
Handlers para mensagens de texto do bot Telegram.
"""
import logging
from typing import Optional

from telegram import Update, ParseMode
from telegram.ext import CallbackContext

from src.bot.bot_utils import check_authorization
from src.database.idea_repository import idea_repository
from src.database.brainstorm_repository import brainstorm_repository
from src.services.openai_service import openai_service

logger = logging.getLogger(__name__)

def process_message(update: Update, context: CallbackContext, message_text: str) -> None:
    """
    Processa uma mensagem de texto.
    
    Args:
        update: Objeto Update do Telegram
        context: Contexto do callback
        message_text: Texto da mensagem a ser processada
    """
    if not message_text:
        update.message.reply_text("Não consegui entender sua mensagem. Por favor, tente novamente.")
        return
    
    # Verifica se é uma resposta a uma pergunta anterior
    if 'esperando_confirmacao_brainstorm' in context.user_data:
        handle_brainstorm_response(update, context)
        return
    
    # Verifica se é uma confirmação para apagar uma ideia
    if 'ideia_para_apagar' in context.user_data:
        from src.bot.command_handlers import confirmar_apagar_ideia
        confirmar_apagar_ideia(update, context)
        return
    
    # Classifica a mensagem
    classificacao, categoria, acao = openai_service.classificar_mensagem(message_text)
    
    logger.info(f"Mensagem classificada: {classificacao} | Categoria: {categoria} | Ação: {acao}")
    
    if classificacao.upper() == "IDEIA":
        # Salva a ideia no banco de dados
        chat_id = update.effective_chat.id
        
        # Usa o tipo, categoria e ação para salvar a ideia
        tipo = classificacao.lower()
        resumo = categoria
        ideia_id = idea_repository.salvar_ideia(message_text, chat_id, tipo, resumo)
        
        if ideia_id:
            # Pergunta se o usuário quer um brainstorm
            context.user_data['esperando_confirmacao_brainstorm'] = True
            context.user_data['ideia_atual'] = ideia_id
            
            update.message.reply_text(
                f"✅ Sua ideia foi salva com ID: {ideia_id}\n\n"
                "Deseja que eu faça um brainstorm para desenvolver esta ideia? Responda com 'sim' ou 'não'."
            )
        else:
            update.message.reply_text("❌ Erro ao salvar sua ideia. Por favor, tente novamente mais tarde.")
    else:
        # Responde de acordo com a classificação
        update.message.reply_text(
            f"Entendi sua mensagem como: {classificacao}\n"
            f"Categoria: {categoria}\n"
            f"Ação recomendada: {acao}\n\n"
            "Para salvar uma ideia e gerar um brainstorm, por favor envie uma mensagem descrevendo sua ideia."
        )

def handle_message(update: Update, context: CallbackContext) -> None:
    """
    Lida com mensagens de texto ou áudio enviadas pelo usuário.
    
    Args:
        update: Objeto Update do Telegram
        context: Contexto do callback
    """
    if not check_authorization(update):
        update.message.reply_text("Você não está autorizado a usar este bot.")
        return
    
    # Verifica se a mensagem contém texto
    if update.message.text:
        process_message(update, context, update.message.text)
    # Verifica se a mensagem contém áudio
    elif update.message.voice:
        from src.bot.voice_handlers import handle_voice_message
        handle_voice_message(update, context)
    else:
        update.message.reply_text(
            "Por favor, envie uma mensagem de texto ou áudio para que eu possa processar sua ideia."
        )

def handle_brainstorm_response(update: Update, context: CallbackContext) -> None:
    """
    Lida com a resposta do usuário sobre fazer brainstorm.
    
    Args:
        update: Objeto Update do Telegram
        context: Contexto do callback
    """
    if not check_authorization(update):
        update.message.reply_text("Você não está autorizado a usar este bot.")
        return
    
    # Verifica se estamos esperando uma confirmação
    if 'esperando_confirmacao_brainstorm' not in context.user_data:
        return
    
    # Obtém a resposta do usuário
    resposta = update.message.text.lower()
    
    # Limpa os dados do usuário
    del context.user_data['esperando_confirmacao_brainstorm']
    
    # Obtém o ID da ideia atual
    ideia_id = context.user_data.get('ideia_atual')
    if not ideia_id:
        update.message.reply_text("Erro ao recuperar sua ideia. Por favor, tente novamente.")
        return
    
    # Limpa o ID da ideia atual
    del context.user_data['ideia_atual']
    
    # Verifica a resposta do usuário
    if resposta in ['sim', 's', 'yes', 'y']:
        # Busca a ideia no banco de dados
        chat_id = update.effective_chat.id
        ideia = idea_repository.obter_ideia(ideia_id, chat_id)
        
        if not ideia:
            update.message.reply_text("Erro ao recuperar sua ideia. Por favor, tente novamente.")
            return
        
        # Envia mensagem de processamento
        processing_message = update.message.reply_text("🧠 Gerando brainstorm... Isso pode levar alguns segundos.")
        
        # Gera o brainstorm
        brainstorm = openai_service.gerar_brainstorm(ideia['conteudo'])
        
        # Salva o brainstorm no banco de dados
        brainstorm_id = brainstorm_repository.salvar_brainstorm(ideia_id, brainstorm)
        
        if brainstorm_id:
            # Formata a mensagem com o brainstorm
            mensagem = f"✅ *Brainstorm para sua ideia:*\n\n"
            mensagem += f"*Ideia:* {ideia['conteudo'][:100]}"
            if len(ideia['conteudo']) > 100:
                mensagem += "..."
            mensagem += "\n\n*Brainstorm:*\n\n"
            mensagem += brainstorm
            
            update.message.reply_text(mensagem, parse_mode=ParseMode.MARKDOWN)
        else:
            update.message.reply_text("❌ Erro ao salvar o brainstorm. Por favor, tente novamente mais tarde.")
    else:
        update.message.reply_text(
            "Ok, não vou gerar um brainstorm para esta ideia agora.\n"
            "Você pode solicitar um brainstorm mais tarde usando o comando /refazer seguido do ID da ideia."
        )
