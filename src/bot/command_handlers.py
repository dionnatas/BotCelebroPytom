"""
Handlers para comandos do bot Telegram.
"""
import logging
from typing import Optional, List, Dict, Any

from telegram import Update, ParseMode
from telegram.ext import CallbackContext

from src.bot.bot_utils import check_authorization
from src.database.idea_repository import idea_repository
from src.database.brainstorm_repository import brainstorm_repository
from src.services.openai_service import openai_service

logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    """
    Envia mensagem de boas-vindas ao usuário.
    
    Args:
        update: Objeto Update do Telegram
        context: Contexto do callback
    """
    if not check_authorization(update):
        update.message.reply_text("Você não está autorizado a usar este bot.")
        return
    
    update.message.reply_text(
        "Olá! Eu sou o Cerebro, seu assistente para brainstorming de ideias.\n\n"
        "Você pode me enviar uma mensagem de texto ou áudio com sua ideia, e eu vou "
        "gerar um brainstorm para ajudar a desenvolvê-la.\n\n"
        "Comandos disponíveis:\n"
        "/comandos - Mostra a lista completa de comandos disponíveis\n"
        "/listar - Lista suas ideias salvas\n"
        "/ver [id] - Mostra detalhes de uma ideia específica\n"
        "/apagar [id] - Apaga uma ideia específica\n"
        "/refazer [id] - Refaz o brainstorm de uma ideia"
    )

def listar_ideias(update: Update, context: CallbackContext) -> None:
    """
    Lista as ideias salvas no banco de dados.
    
    Args:
        update: Objeto Update do Telegram
        context: Contexto do callback
    """
    if not check_authorization(update):
        update.message.reply_text("Você não está autorizado a usar este bot.")
        return
    
    chat_id = update.effective_chat.id
    ideias = idea_repository.listar_ideias(chat_id)
    
    if not ideias:
        update.message.reply_text("Você ainda não tem ideias salvas. Envie uma mensagem com sua ideia para começar!")
        return
    
    # Formata a lista de ideias
    mensagem = "📋 *Suas ideias salvas:*\n\n"
    for ideia in ideias:
        # Limita o tamanho da descrição para a listagem
        descricao = ideia['conteudo']
        if len(descricao) > 50:
            descricao = descricao[:47] + "..."
        
        mensagem += f"*ID {ideia['id']}:* {descricao}\n"
    
    mensagem += "\nUse /ver [id] para ver os detalhes de uma ideia específica."
    
    update.message.reply_text(mensagem, parse_mode=ParseMode.MARKDOWN)

def ver_ideia(update: Update, context: CallbackContext) -> None:
    """
    Mostra os detalhes de uma ideia específica.
    
    Args:
        update: Objeto Update do Telegram
        context: Contexto do callback
    """
    if not check_authorization(update):
        update.message.reply_text("Você não está autorizado a usar este bot.")
        return
    
    # Verifica se o ID foi fornecido
    if not context.args:
        update.message.reply_text("Por favor, forneça o ID da ideia que deseja visualizar. Exemplo: /ver 1")
        return
    
    try:
        ideia_id = int(context.args[0])
    except ValueError:
        update.message.reply_text("O ID da ideia deve ser um número. Exemplo: /ver 1")
        return
    
    # Busca a ideia no banco de dados
    chat_id = update.effective_chat.id
    ideia = idea_repository.obter_ideia(ideia_id, chat_id)
    
    if not ideia:
        update.message.reply_text(f"Ideia com ID {ideia_id} não encontrada ou não pertence a você.")
        return
    
    # Busca os brainstorms relacionados
    brainstorms = brainstorm_repository.obter_brainstorms_por_ideia(ideia_id)
    
    # Formata a mensagem com os detalhes da ideia
    mensagem = f"📝 *Ideia {ideia_id}*\n\n"
    mensagem += f"{ideia['conteudo']}\n\n"
    
    if brainstorms:
        mensagem += "*Brainstorm:*\n\n"
        # Pega o brainstorm mais recente
        ultimo_brainstorm = brainstorms[0]
        mensagem += f"{ultimo_brainstorm['conteudo']}\n\n"
        
        if len(brainstorms) > 1:
            mensagem += f"Esta ideia tem {len(brainstorms)} versões de brainstorm.\n"
    else:
        mensagem += "*Sem brainstorms*\n\n"
        mensagem += "Esta ideia ainda não tem brainstorms associados."
    
    # Adiciona informações sobre comandos relacionados
    mensagem += "\nUse /refazer para gerar um novo brainstorm para esta ideia."
    mensagem += "\nUse /apagar para excluir esta ideia e seus brainstorms."
    
    update.message.reply_text(mensagem, parse_mode=ParseMode.MARKDOWN)

def apagar_ideia(update: Update, context: CallbackContext) -> None:
    """
    Apaga uma ideia e seus brainstorms relacionados.
    
    Args:
        update: Objeto Update do Telegram
        context: Contexto do callback
    """
    if not check_authorization(update):
        update.message.reply_text("Você não está autorizado a usar este bot.")
        return
    
    # Verifica se o ID foi fornecido
    if not context.args:
        update.message.reply_text("Por favor, forneça o ID da ideia que deseja apagar. Exemplo: /apagar 1")
        return
    
    try:
        ideia_id = int(context.args[0])
    except ValueError:
        update.message.reply_text("O ID da ideia deve ser um número. Exemplo: /apagar 1")
        return
    
    # Verifica se a ideia existe e pertence ao usuário
    chat_id = update.effective_chat.id
    ideia = idea_repository.obter_ideia(ideia_id, chat_id)
    
    if not ideia:
        update.message.reply_text(f"Ideia com ID {ideia_id} não encontrada ou não pertence a você.")
        return
    
    # Pede confirmação antes de apagar
    context.user_data['ideia_para_apagar'] = ideia_id
    
    mensagem = f"Você tem certeza que deseja apagar a ideia {ideia_id}?\n\n"
    mensagem += f"*{ideia['conteudo'][:100]}*"
    if len(ideia['conteudo']) > 100:
        mensagem += "..."
    mensagem += "\n\nResponda com 'sim' para confirmar ou 'não' para cancelar."
    
    update.message.reply_text(mensagem, parse_mode=ParseMode.MARKDOWN)

def confirmar_apagar_ideia(update: Update, context: CallbackContext) -> None:
    """
    Confirma a exclusão de uma ideia após o usuário confirmar.
    
    Args:
        update: Objeto Update do Telegram
        context: Contexto do callback
    """
    if not check_authorization(update):
        update.message.reply_text("Você não está autorizado a usar este bot.")
        return
    
    # Verifica se há uma ideia pendente para apagar
    ideia_id = context.user_data.get('ideia_para_apagar')
    if not ideia_id:
        update.message.reply_text("Não há nenhuma ideia pendente para exclusão.")
        return
    
    # Obtém a resposta do usuário
    resposta = update.message.text.lower()
    
    if resposta == 'sim':
        # Apaga a ideia e seus brainstorms
        chat_id = update.effective_chat.id
        sucesso = idea_repository.apagar_ideia(ideia_id, chat_id)
        
        if sucesso:
            update.message.reply_text(f"✅ Ideia {ideia_id} e seus brainstorms foram apagados com sucesso.")
        else:
            update.message.reply_text(f"❌ Erro ao apagar a ideia {ideia_id}. Tente novamente mais tarde.")
    else:
        update.message.reply_text("Exclusão cancelada. A ideia não foi apagada.")
    
    # Limpa os dados do usuário
    if 'ideia_para_apagar' in context.user_data:
        del context.user_data['ideia_para_apagar']

def refazer_brainstorm(update: Update, context: CallbackContext) -> None:
    """
    Refaz um brainstorm existente.
    
    Args:
        update: Objeto Update do Telegram
        context: Contexto do callback
    """
    if not check_authorization(update):
        update.message.reply_text("Você não está autorizado a usar este bot.")
        return
    
    # Verifica se o ID foi fornecido
    if not context.args:
        update.message.reply_text("Por favor, forneça o ID da ideia para a qual deseja refazer o brainstorm. Exemplo: /refazer 1")
        return
    
    try:
        ideia_id = int(context.args[0])
    except ValueError:
        update.message.reply_text("O ID da ideia deve ser um número. Exemplo: /refazer 1")
        return
    
    # Verifica se a ideia existe e pertence ao usuário
    chat_id = update.effective_chat.id
    ideia = idea_repository.obter_ideia(ideia_id, chat_id)
    
    if not ideia:
        update.message.reply_text(f"Ideia com ID {ideia_id} não encontrada ou não pertence a você.")
        return
    
    # Verifica se a ideia tem brainstorms
    brainstorms = brainstorm_repository.obter_brainstorms_por_ideia(ideia_id)
    if not brainstorms:
        update.message.reply_text(f"A ideia com ID {ideia_id} não tem brainstorms para refazer.")
        return
    
    # Envia mensagem de processamento
    processing_message = update.message.reply_text("🧠 Gerando novo brainstorm... Isso pode levar alguns segundos.")
    
    # Gera um novo brainstorm
    novo_brainstorm = openai_service.gerar_brainstorm(ideia['conteudo'])
    
    # Atualiza o brainstorm mais recente
    brainstorm_id = brainstorms[0]['id']  # Pega o ID do brainstorm mais recente
    sucesso = brainstorm_repository.atualizar_brainstorm(brainstorm_id, novo_brainstorm)
    
    if sucesso:
        # Formata a mensagem com o novo brainstorm
        mensagem = f"✅ *Brainstorm refeito para a ideia {ideia_id}*\n\n"
        mensagem += f"*Ideia:* {ideia['conteudo'][:100]}"
        if len(ideia['conteudo']) > 100:
            mensagem += "..."
        mensagem += "\n\n*Novo Brainstorm:*\n\n"
        mensagem += novo_brainstorm
        
        update.message.reply_text(mensagem, parse_mode=ParseMode.MARKDOWN)
    else:
        update.message.reply_text(f"❌ Erro ao atualizar o brainstorm para a ideia {ideia_id}. Tente novamente mais tarde.")

def listar_comandos(update: Update, context: CallbackContext) -> None:
    """
    Lista todos os comandos disponíveis no bot.
    
    Args:
        update: Objeto Update do Telegram
        context: Contexto do callback
    """
    if not check_authorization(update):
        update.message.reply_text("Você não está autorizado a usar este bot.")
        return
    
    mensagem = "🤖 *Comandos disponíveis:*\n\n"
    mensagem += "/start - Inicia o bot e mostra a mensagem de boas-vindas\n"
    mensagem += "/comandos - Mostra esta lista de comandos\n"
    mensagem += "/listar - Lista todas as suas ideias salvas\n"
    mensagem += "/ver [id] - Mostra os detalhes de uma ideia específica\n"
    mensagem += "/apagar [id] - Apaga uma ideia e seus brainstorms\n"
    mensagem += "/refazer [id] - Refaz o brainstorm para uma ideia existente\n\n"
    
    mensagem += "*Como usar:*\n"
    mensagem += "• Envie uma mensagem de texto ou áudio com sua ideia\n"
    mensagem += "• O bot irá classificar sua mensagem e perguntar se deseja um brainstorm\n"
    mensagem += "• Responda 'sim' para gerar um brainstorm para sua ideia\n"
    mensagem += "• Use /listar para ver suas ideias salvas\n"
    mensagem += "• Use /ver [id] para ver os detalhes de uma ideia específica\n"
    
    update.message.reply_text(mensagem, parse_mode=ParseMode.MARKDOWN)
