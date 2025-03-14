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
    
    # Inicializa a variável user_message
    user_message = ""
    
    if update.message.voice:
        try:
            import os
            update.message.reply_text("Processando seu áudio, por favor aguarde...")
            file = context.bot.get_file(update.message.voice.file_id)
            temp_audio_path = None
            temp_wav_path = None
            
            # Inicializa a variável transcription_success
            transcription_success = False
            
            try:
                # Cria um arquivo temporário para o arquivo original
                temp_fd, temp_audio_path = tempfile.mkstemp(suffix='.ogg')
                os.close(temp_fd)  # Fecha o descritor de arquivo
                
                # Baixa o arquivo de áudio para o arquivo temporário
                file.download(out=temp_audio_path)
                logger.info(f"Arquivo de áudio baixado para: {temp_audio_path}")
                
                # Verifica se o arquivo existe e tem tamanho
                if os.path.exists(temp_audio_path) and os.path.getsize(temp_audio_path) > 0:
                    logger.info(f"Arquivo de áudio existe e tem tamanho: {os.path.getsize(temp_audio_path)} bytes")
                else:
                    logger.error("Arquivo de áudio não existe ou está vazio")
                    raise Exception("Arquivo de áudio inválido")
                
                # Converte para WAV usando pydub
                logger.info("Convertendo áudio para WAV...")
                temp_wav_fd, temp_wav_path = tempfile.mkstemp(suffix='.wav')
                os.close(temp_wav_fd)
                
                try:
                    # Certifica-se de que pydub está instalado
                    try:
                        from pydub import AudioSegment
                    except ImportError:
                        logger.info("Instalando pydub...")
                        import subprocess
                        subprocess.run(["python3", "-m", "pip", "install", "pydub"], check=True)
                        from pydub import AudioSegment
                    
                    # Carrega o áudio e converte para WAV
                    logger.info("Carregando arquivo de áudio com pydub...")
                    try:
                        # Tenta determinar o formato do arquivo
                        import subprocess
                        result = subprocess.run(['file', temp_audio_path], capture_output=True, text=True)
                        logger.info(f"Informações do arquivo: {result.stdout}")
                        
                        # Tenta carregar com formato específico primeiro
                        if 'ogg' in result.stdout.lower():
                            logger.info("Detectado formato OGG")
                            sound = AudioSegment.from_file(temp_audio_path, format="ogg")
                        elif 'mp3' in result.stdout.lower():
                            logger.info("Detectado formato MP3")
                            sound = AudioSegment.from_file(temp_audio_path, format="mp3")
                        elif 'wav' in result.stdout.lower():
                            logger.info("Detectado formato WAV")
                            sound = AudioSegment.from_file(temp_audio_path, format="wav")
                        else:
                            # Tenta formato genérico
                            logger.info("Formato não reconhecido, tentando formato genérico")
                            sound = AudioSegment.from_file(temp_audio_path)
                        
                        # Exporta para WAV com configurações específicas compatíveis com Whisper
                        logger.info("Exportando para WAV...")
                        sound = sound.set_channels(1)  # Mono
                        sound = sound.set_frame_rate(16000)  # 16kHz
                        sound.export(temp_wav_path, format="wav")
                        logger.info(f"Arquivo WAV exportado com configurações: mono, 16kHz")
                        
                        # Verifica se o arquivo WAV foi criado corretamente
                        if os.path.exists(temp_wav_path) and os.path.getsize(temp_wav_path) > 0:
                            logger.info(f"Arquivo WAV criado com sucesso: {os.path.getsize(temp_wav_path)} bytes")
                            # Substitui o arquivo original pelo convertido
                            temp_audio_path = temp_wav_path
                        else:
                            raise Exception("Arquivo WAV não foi criado corretamente")
                    except Exception as e:
                        logger.error(f"Erro na conversão para WAV: {e}")
                        raise
                
                    logger.info("Iniciando transcrição...")
                    
                    # Usando o método mais direto e confiável - chamada direta à API REST
                    try:
                        logger.info("Transcrevendo áudio usando chamada direta à API REST...")
                        
                        # Configura a chave da API
                        openai.api_key = OPENAI_API_KEY
                        logger.info(f"OPENAI_API_KEY configurada: {bool(OPENAI_API_KEY)} (comprimento: {len(OPENAI_API_KEY)})")                    
                        # Lê o arquivo de áudio
                        with open(temp_audio_path, "rb") as audio_file:
                            audio_data = audio_file.read()
                        
                        logger.info(f"Arquivo de áudio lido: {len(audio_data)} bytes")
                        
                        # Configura os cabeçalhos para a solicitação
                        headers = {
                            "Authorization": f"Bearer {OPENAI_API_KEY}"
                        }
                        
                        # Prepara os dados para upload
                        files = {
                            "file": ("audio.wav", audio_data, "audio/wav")
                        }
                        data = {
                            "model": "whisper-1",
                            "language": "pt",  # Especifica o idioma português
                            "response_format": "json",  # Garante resposta em JSON
                            "temperature": 0.0  # Reduz a criatividade para maior precisão
                        }
                        
                        # Faz a solicitação para a API
                        logger.info("Enviando solicitação para a API OpenAI...")
                        response = requests.post(
                            "https://api.openai.com/v1/audio/transcriptions",
                            headers=headers,
                            files=files,
                            data=data
                        )
                        
                        # Verifica a resposta
                        logger.info(f"Código de status da resposta: {response.status_code}")
                        logger.info(f"Cabeçalhos da resposta: {response.headers}")
                        
                        if response.status_code == 200:
                            # Processa a resposta bem-sucedida
                            result = response.json()
                            logger.info(f"Resposta completa da API: {result}")
                            
                            user_message = result.get("text", "")
                            logger.info(f"Texto transcrito: '{user_message}'")
                            
                            if user_message and user_message.strip():
                                logger.info("Transcrição bem-sucedida!")
                                transcription_success = True
                            else:
                                logger.error("A transcrição retornou texto vazio")
                                # Tenta novamente com temperatura mais alta para casos difíceis
                                logger.info("Tentando novamente com temperatura mais alta...")
                                
                                # Atualiza os parâmetros para uma segunda tentativa
                                data["temperature"] = 0.2  # Aumenta um pouco a criatividade
                                
                                # Faz a solicitação para a API novamente
                                logger.info("Enviando segunda solicitação para a API OpenAI...")
                                response = requests.post(
                                    "https://api.openai.com/v1/audio/transcriptions",
                                    headers=headers,
                                    files={
                                        "file": ("audio.wav", audio_data, "audio/wav")
                                    },
                                    data=data
                                )
                                
                                if response.status_code == 200:
                                    result = response.json()
                                    logger.info(f"Resposta da segunda tentativa: {result}")
                                    
                                    user_message = result.get("text", "")
                                    logger.info(f"Texto transcrito (segunda tentativa): '{user_message}'")
                                    
                                    if user_message and user_message.strip():
                                        logger.info("Transcrição bem-sucedida na segunda tentativa!")
                                        transcription_success = True
                                    else:
                                        logger.error("A transcrição retornou texto vazio mesmo na segunda tentativa")
                                        raise Exception("Transcrição vazia após múltiplas tentativas")
                                else:
                                    logger.error(f"Erro na API (segunda tentativa): {response.status_code}")
                                    logger.error(f"Detalhes do erro: {response.text}")
                                    raise Exception(f"Erro na API: {response.status_code}")
                        else:
                            # Registra detalhes do erro
                            logger.error(f"Erro na API: {response.status_code}")
                            logger.error(f"Detalhes do erro: {response.text}")
                            raise Exception(f"Erro na API: {response.status_code}")
                        
                    except Exception as e:
                        logger.error(f"Erro na transcrição: {e}")
                        raise Exception(f"Falha na transcrição: {e}")
                
                finally:
                    # Limpa os arquivos temporários
                    for temp_file in [temp_audio_path, temp_wav_path]:
                        if temp_file and os.path.exists(temp_file):
                            try:
                                os.remove(temp_file)
                                logger.info(f"Arquivo temporário removido: {temp_file}")
                            except Exception as e:
                                logger.error(f"Erro ao remover arquivo temporário: {e}")
                    
                    # Verifica se a transcrição foi bem-sucedida e se há conteúdo
                    logger.info(f"Transcrição bem-sucedida: {transcription_success}")
                    logger.info(f"Conteúdo da transcrição: '{user_message}'")
                
                    if not user_message or user_message.strip() == "":
                        logger.error("A transcrição do áudio retornou vazia")
                        update.message.reply_text(
                            "Erro: Não foi possível transcrever o áudio. Por favor, tente novamente com um áudio mais claro ou:"
                            "\n- Verifique se o áudio tem boa qualidade"
                            "\n- Certifique-se de que o áudio contém fala clara"
                            "\n- Tente gravar em um ambiente com menos ruído"
                        )
                        return
                    
                    # Processa a mensagem transcrita como se fosse uma mensagem de texto normal
                    logger.info("Processando a transcrição como mensagem de texto")
                    process_message(update, context, user_message)
                    return  # Importante: retorna após processar o áudio
                    
            except Exception as e:
                logger.error(f"Erro na transcrição: {e}")
                update.message.reply_text(
                    "Erro ao processar seu áudio. Por favor, tente novamente ou envie sua mensagem como texto."
                )
                return
        except Exception as e:
            logger.error(f"Erro ao processar áudio: {e}")
            update.message.reply_text(
                "Erro ao processar seu áudio. Por favor, tente novamente ou envie sua mensagem como texto."
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
