# Estrutura do Projeto Cerebro

Este documento descreve a estrutura do projeto Cerebro, um bot Telegram para captura e organização de ideias.

## Visão Geral da Arquitetura

O projeto segue uma arquitetura modular, com separação clara de responsabilidades:

```
BotCelebroPytom/
│
├── main.py                   # Ponto de entrada principal
├── cerebro.py                # Versão legada (mantida para compatibilidade)
├── requirements.txt          # Dependências do projeto
├── README.md                 # Documentação principal
│
├── src/                      # Código-fonte principal
│   ├── __init__.py           # Inicializador do pacote
│   │
│   ├── bot/                  # Módulo do bot Telegram
│   │   ├── __init__.py
│   │   ├── cerebro_bot.py    # Implementação principal do bot
│   │   └── handlers.py       # Handlers para comandos e mensagens
│   │
│   ├── config/               # Configurações
│   │   ├── __init__.py
│   │   ├── settings.py       # Configurações gerais
│   │   └── prompts.py        # Prompts para a IA
│   │
│   ├── database/             # Gerenciamento de banco de dados
│   │   ├── __init__.py
│   │   └── db_manager.py     # Operações de banco de dados
│   │
│   ├── services/             # Serviços externos
│   │   ├── __init__.py
│   │   └── openai_service.py # Integração com a API da OpenAI
│   │
│   ├── transcription/        # Processamento de áudio
│   │   ├── __init__.py
│   │   ├── audio_processor.py # Processamento de arquivos de áudio
│   │   └── transcriber.py     # Transcrição de áudio para texto
│   │
│   └── utils/                # Utilitários
│       ├── __init__.py
│       └── helpers.py        # Funções auxiliares
│
└── scripts/                  # Scripts de utilidade (para Termux, etc.)
```

## Componentes Principais

### 1. Bot Telegram (`src/bot/`)

- **cerebro_bot.py**: Implementação principal do bot, gerenciando a inicialização e o ciclo de vida.
- **handlers.py**: Handlers para comandos e mensagens, processando entradas do usuário.

### 2. Configuração (`src/config/`)

- **settings.py**: Configurações gerais, incluindo chaves de API, configuração de logging e caminhos.
- **prompts.py**: Prompts utilizados para interação com a API da OpenAI.

### 3. Banco de Dados (`src/database/`)

- **db_manager.py**: Gerencia operações de banco de dados, incluindo inicialização, consultas e atualizações.

### 4. Serviços (`src/services/`)

- **openai_service.py**: Integração com a API da OpenAI para classificação de mensagens e geração de brainstorms.

### 5. Transcrição (`src/transcription/`)

- **audio_processor.py**: Processamento de arquivos de áudio, incluindo conversão para formatos compatíveis.
- **transcriber.py**: Transcrição de áudio para texto usando a API da OpenAI.

### 6. Utilitários (`src/utils/`)

- **helpers.py**: Funções auxiliares para manipulação de arquivos, logging, etc.

## Fluxo de Dados

1. O usuário envia uma mensagem (texto ou áudio) para o bot via Telegram.
2. O handler apropriado processa a mensagem:
   - Para áudio: converte para WAV, transcreve para texto e depois processa como texto.
   - Para texto: processa diretamente.
3. A mensagem é classificada usando a API da OpenAI.
4. Dependendo da classificação, o bot pode oferecer um brainstorm.
5. Os dados são armazenados no banco de dados para referência futura.

## Pontos de Extensão

Para adicionar novos recursos ao bot, considere:

1. **Novos Comandos**: Adicione novos handlers em `handlers.py` e registre-os em `cerebro_bot.py`.
2. **Novos Serviços**: Crie novos módulos em `services/` para integrações adicionais.
3. **Novos Tipos de Processamento**: Estenda as capacidades de processamento em módulos dedicados.

## Considerações de Segurança

- As chaves de API são armazenadas em `secrets_cerebro.py` (não versionado).
- O acesso ao bot é restrito a IDs de chat específicos configurados em `MY_CHAT_ID`.
- Arquivos temporários são limpos após o uso para evitar vazamento de dados.
