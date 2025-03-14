<p align="center">
    <img src="img/cerebro.png" alt="cerebro">
</p>

# Cerebro - Bot Telegram

## Índice
- [Visão Geral](#visão-geral)
- [Características](#características)
- [Instalação Rápida](#instalação-rápida)
- [Configuração](#configuração)
- [Uso](#uso)
- [Banco de Dados](#banco-de-dados)
- [Solução de Problemas](#solução-de-problemas)
- [Documentação Detalhada](#documentação-detalhada)

## Visão Geral

Cerebro é um bot do Telegram que tem o objetivo de ser seu segundo cérebro por meio do processamento de linguagem natural e inteligência artificial. Ele utiliza LLMs para interpretar entradas de voz e texto, facilitando uma experiência única para alavancar seu potencial. Ideal para criadores, escritores e qualquer pessoa que deseje explorar e expandir suas ideias, o Cérebro atua como um parceiro usando ferramentas de inteligência artificial.

## Características

Principais funcionalidades implementadas:
- Processamento de entradas de voz e texto
- Identificação e categorização de ideias
- Sessão de brainstorming automatizada com base nas ideias identificadas
- Armazenamento persistente de ideias e sessões no Supabase (banco de dados PostgreSQL na nuvem)
- Backup local em SQLite como alternativa
- Modelo de interação flexível, apoiando tanto a exploração imediata quanto adiada das ideias

## Instalação

### Pré-requisitos

- Python 3.9+ (testado com Python 3.9.6 e 3.10.7)
- Uma conta no Telegram
- Chaves de API para OpenAI e Telegram Bot
- Conta no Supabase (opcional, pode usar SQLite local)

### Configuração

1. **Copie os arquivos do projeto**: Baixe os arquivos projeto para sua máquina local e salve em uma pasta ou faça o clone do repositório do GitHub usando o comando `git clone`.
```sh
git clone https://github.com/dionnatas/BotCelebroPytom.git
```

2. **Navegue até o Diretório do Projeto**

Segue como arquivos devem estar apresentados no diretório do projeto:

<p align="center">
    <img src="img/arquivos_instalacao.png" alt="estrura arquivos">
</p>

3. **Configure o Ambiente Python (Opcional, mas recomendado)**: Use um ambiente virtual para evitar conflitos com outros projetos.

#### Windows:

No prompt de comando ou no terminal do vscode.

Crie o ambiente virtual:

Se você tiver várias versões do Python, use o seguinte comando (substitua USERNAME pelo seu usuário):
```sh
C:\Users\USERNAME\AppData\Local\Programs\Python\Python310\python -m venv venv
```

```sh
python -m venv venv
```
Ative o ambiente virtual
Se for no <b>vscode</b> ou <b>PowerShell</b>
```sh
.\venv\Scripts\Activate.ps1
```
Se for no <b>prompt de comando</b>
```sh
.\venv\Scripts\activate.bat
```
4. **Instale as Dependências**: Instale os requisitos do projeto.

```sh
pip install -r requirements.txt
```

### Criando Seu Bot do Telegram com o BotFather

1. **Inicie o BotFather**: No Telegram, procure pela conta do BotFather (@BotFather), o bot oficial para criar e gerenciar bots do Telegram.

2. **Crie um Novo Bot**: Envie `/newbot` para o BotFather e siga as instruções. Você precisará fornecer um nome e um nome de usuário único para o seu bot.

3. **Obtenha o Token da API**: Após a criação bem-sucedida, o BotFather fornecerá um token da API para o seu novo bot. Esse token permite que seu bot se comunique com a API do Telegram.

4. **Configuração de APIs**: Renomeie `secrets_cerebro.py.example` para `secrets_cerebro.py` e preencha-o com suas chaves de API do Telegram, OpenAI e Supabase (se estiver usando) conforme necessário.

## Executando o Cérebro

Execute `main.py` para iniciar o bot:
```sh
python main.py
```
Isso ativará o Cerebro na sua conta do Telegram, pronto para receber e processar suas entradas. Da primeira vez que você tentar conversar com o Cerebro ele não identificará você. Você precisará capturar o código do usuário no terminal e inserí-lo no arquivo `secrets_cerebro.py`

**Inicialização do Banco de Dados**: A primeira execução do `main.py` configurará automaticamente o banco de dados necessário (Supabase ou SQLite local, dependendo da configuração em `src/config/settings.py`) para armazenar dados da sessão.

## Uso

- **Captura de Ideias por Voz**: Envie uma mensagem de voz para o Cérebro com sua ideia, e ele a processará e perguntará se você deseja fazer um brainstorming sobre essa ideia.
- **Entrada de Texto**: Envie mensagens de texto para ideias rápidas ou comandos para gerenciar suas sessões de ideias.
- **Sessões de Brainstorming**: Siga as instruções do bot para explorar e expandir suas ideias.

### Comandos Disponíveis

| Comando | Descrição |
|---------|------------|
| `/start` | Inicia a conversa com o bot e exibe uma mensagem de boas-vindas |
| `/listar` | Lista as últimas 10 ideias salvas no banco de dados |
| `/ver <id>` | Mostra os detalhes completos de uma ideia específica, incluindo brainstorms associados |

## Banco de Dados

O Cerebro suporta dois tipos de armazenamento de dados:

### SQLite (Local)

- Armazenamento local em arquivo SQLite
- Não requer configuração adicional
- Ideal para uso pessoal ou testes

### Supabase (PostgreSQL na nuvem)

- Armazenamento em banco de dados PostgreSQL na nuvem
- Requer conta no Supabase e configuração das chaves de API
- Ideal para uso em produção ou quando múltiplos usuários precisam acessar os dados

Para alternar entre SQLite e Supabase, edite a configuração `USE_SUPABASE` no arquivo `src/config/settings.py`:

```python
# Configuração para usar Supabase em vez do SQLite
USE_SUPABASE = True  # Mude para False para usar o SQLite local
```

Para mais informações sobre a configuração do Supabase, consulte o arquivo `README_SUPABASE.md`.

## Ideias para implementação futura

- **Gestão de aniversários**: Sempre esqueço de algumas datas, gostaria de ajuda pra me lembrar e eventualmente escrever mensagens personalizadas
- **Adicionar elementos às ideias existentes**: Permitir ao usuário complementar elementos às ideias existentes
- **Incorporar agentes (crewAI) para realização de tarefas específicas**

## Execução no Termux (Android)

Você pode executar o Cerebro diretamente no seu celular Android usando o Termux. Isso permite que você mantenha o bot funcionando no seu dispositivo móvel.

### Instalação do Termux

1. Instale o Termux pela [F-Droid](https://f-droid.org/en/packages/com.termux/) (recomendado) ou pela Google Play Store.
2. Abra o Termux e execute os seguintes comandos:

```sh
# Atualizar pacotes
pkg update -y && pkg upgrade -y

# Instalar dependências necessárias
pkg install -y python git clang libffi openssl

# Clonar o repositório (ou copie os arquivos manualmente)
git clone https://github.com/dionnatas/BotCelebroPytom.git
cd BotCelebroPytom

# Dar permissão de execução ao script de configuração
chmod +x setup_termux.sh

# Executar o script de configuração
./setup_termux.sh
```

### Configurando as chaves de API

Certifique-se de configurar corretamente o arquivo `secrets_cerebro.py` com suas chaves de API:

```python
# secrets_cerebro.py
TELEGRAM_API_KEY = "sua_chave_telegram_aqui"
OPENAI_API_KEY = "sua_chave_openai_aqui"
MY_CHAT_ID = "seu_chat_id_aqui"  # ou ["id1", "id2"] para múltiplos IDs
SUPABASE_URL = "sua_url_supabase_aqui"  # opcional, para usar Supabase
SUPABASE_KEY = "sua_chave_supabase_aqui"  # opcional, para uso anônimo
SUPABASE_SERVICE_KEY = "sua_chave_servico_supabase_aqui"  # opcional, para operações administrativas
```

### Executando o bot

Você tem várias opções para executar o bot no Termux:

#### 1. Usando os scripts prontos

O projeto inclui vários scripts para facilitar a execução e gerenciamento do bot no Termux:

##### Scripts de configuração e execução:
- `setup_termux.sh`: Configura o ambiente, instala dependências e verifica a configuração.
- `run_termux.sh`: Executa o bot no modo normal (terminal ativo).
- `run_background.sh`: Executa o bot em segundo plano, permitindo fechar o Termux.

##### Scripts de gerenciamento:
- `status_bot.sh`: Verifica o status atual do bot, mostra informações de uso de recursos e últimas linhas do log.
- `stop_bot.sh`: Para o bot de forma segura, garantindo que todos os processos sejam encerrados corretamente.
- `restart_bot.sh`: Reinicia o bot, útil para aplicar atualizações ou corrigir problemas.

##### Scripts de correção:
- `fix_termux.py`: Corrige problemas de compatibilidade específicos do Termux.
- `check_telegram_bot.py`: Verifica e instala a versão correta da biblioteca python-telegram-bot.
- `check_openai.py`: Verifica e instala a versão recomendada (0.28.0) da API OpenAI.

Para usar os scripts:

```sh
# Dê permissão de execução aos scripts (apenas uma vez)
chmod +x setup_termux.sh run_termux.sh run_background.sh stop_bot.sh status_bot.sh restart_bot.sh

# Configure o ambiente
./setup_termux.sh

# Execute o bot em segundo plano
./run_background.sh

# Verifique o status do bot
./status_bot.sh

# Para o bot quando quiser
./stop_bot.sh

# Reinicie o bot (para aplicar atualizações)
./restart_bot.sh
```

#### 2. Executando manualmente

Se preferir, você pode executar o bot manualmente:

```sh
# Execução normal
python main.py

# Execução em segundo plano
nohup python main.py > cerebro.log 2>&1 &
```

#### 3. Corrigindo problemas de compatibilidade

Se encontrar problemas de compatibilidade, execute o script de correção:

```sh
python fix_termux.py
```

Este script corrige problemas comuns, como a importação do `ParseMode`.

## Solução de Problemas

### Problemas com transcrição de áudio

Se você encontrar erros ao enviar mensagens de áudio, como `'str' object has no attribute 'write'`, tente as seguintes soluções:

1. **Verifique a versão da API OpenAI**:
   ```sh
   python check_openai.py
   ```
   A versão recomendada é a 0.28.0, que é compatível com o código do bot.

2. **Aplique as correções para o Termux**:
   ```sh
   python fix_termux.py
   ```

3. **Reinicie o bot**:
   ```sh
   ./restart_bot.sh
   ```

### Problemas com respostas ao brainstorm

Se o bot não reconhecer suas respostas como "Sim" ou "Não", certifique-se de que o script `fix_termux.py` foi executado, pois ele corrige o problema de case sensitivity nas respostas.

### Outros problemas

Se você encontrar outros problemas, verifique os logs do bot:

```bash
cat logs/cerebro.log
```

## Documentação Detalhada

Para informações mais detalhadas sobre o projeto, consulte os seguintes documentos:

- [Estrutura do Projeto](docs/ESTRUTURA.md) - Descrição detalhada da arquitetura e organização do código
- [Guia de Instalação](docs/INSTALACAO.md) - Instruções detalhadas para instalação em diferentes ambientes
- [Documentação do Supabase](docs/SUPABASE.md) - Informações completas sobre a integração com o Supabase
- [Scripts](scripts/README.md) - Documentação dos scripts de utilidade disponíveis

## Contribuindo

Contribuições são bem-vindas! Se você deseja contribuir para o projeto, por favor:

1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Faça commit das suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Faça push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.
