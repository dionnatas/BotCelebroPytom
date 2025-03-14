# Guia de Instalação do Bot Cerebro

Este guia descreve o processo de instalação e configuração do Bot Cerebro em diferentes ambientes.

## Requisitos

- Python 3.7 ou superior
- pip (gerenciador de pacotes Python)
- ffmpeg (para processamento de áudio)
- Chave de API do Telegram Bot
- Chave de API da OpenAI

## Instalação em Ambiente Desktop (Windows, macOS, Linux)

1. **Clone o repositório ou baixe os arquivos**

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure as chaves de API**
   - Crie um arquivo `secrets_cerebro.py` na raiz do projeto
   - Adicione suas chaves de API no seguinte formato:
   ```python
   TELEGRAM_API_KEY = "sua_chave_do_telegram"
   OPENAI_API_KEY = "sua_chave_da_openai"
   ALLOWED_CHAT_IDS = [123456789]  # IDs de chat autorizados
   ```

4. **Execute o bot**
   ```bash
   python main.py
   ```

## Instalação no Termux (Android)

O Termux é um emulador de terminal para Android que permite executar o bot diretamente no seu dispositivo móvel.

1. **Instale o Termux**
   - Baixe o Termux da [F-Droid](https://f-droid.org/packages/com.termux/)
   - Não use a versão da Play Store, pois está desatualizada

2. **Configure o Termux**
   ```bash
   pkg update && pkg upgrade
   pkg install python git ffmpeg libffi openssl
   ```

3. **Clone o repositório**
   ```bash
   git clone https://github.com/seu-usuario/cerebro-bot.git
   cd cerebro-bot
   ```

4. **Use o script de configuração automática**
   ```bash
   chmod +x scripts/setup_termux.sh
   ./scripts/setup_termux.sh
   ```

5. **Configure as chaves de API**
   - Edite o arquivo `secrets_cerebro.py` com suas chaves
   ```bash
   nano secrets_cerebro.py
   ```

6. **Execute o bot em segundo plano**
   ```bash
   ./scripts/run_background.sh
   ```

## Gerenciamento do Bot

O projeto inclui scripts para facilitar o gerenciamento do bot:

- **Iniciar em segundo plano**: `./scripts/run_background.sh`
- **Verificar status**: `./scripts/status_bot.sh`
- **Parar o bot**: `./scripts/stop_bot.sh`
- **Reiniciar o bot**: `./scripts/restart_bot.sh`

## Migração da Versão Antiga

Se você está atualizando de uma versão anterior do bot, execute o script de migração:

```bash
python scripts/update_cerebro.py
```

Este script:
1. Cria um backup dos arquivos originais
2. Configura a compatibilidade com a nova estrutura
3. Migra o banco de dados para o novo formato

## Solução de Problemas

### Problemas com Transcrição de Áudio

Se encontrar problemas com a transcrição de áudio, execute:

```bash
python scripts/fix_audio.py
```

Este script verifica:
- Instalação do ffmpeg
- Versão correta da API OpenAI
- Configuração da chave da API
- Funcionalidade de transcrição

### Logs

Os logs são salvos em `cerebro.log` na raiz do projeto. Verifique este arquivo para diagnóstico de problemas.

## Estrutura do Projeto

Para entender a estrutura do projeto, consulte o arquivo [ESTRUTURA.md](ESTRUTURA.md).
