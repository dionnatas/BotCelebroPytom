# Documentação do Supabase no Bot Cerebro

Este documento consolida todas as informações relacionadas à integração do Bot Cerebro com o Supabase, incluindo configuração, migração e uso.

## Índice
1. [Visão Geral](#visão-geral)
2. [Configuração do Supabase](#configuração-do-supabase)
3. [Migração de Dados](#migração-de-dados)
4. [Estrutura das Tabelas](#estrutura-das-tabelas)
5. [Alternando entre SQLite e Supabase](#alternando-entre-sqlite-e-supabase)
6. [Políticas de Segurança](#políticas-de-segurança)
7. [Arquivos e Scripts Relacionados](#arquivos-e-scripts-relacionados)
8. [Solução de Problemas](#solução-de-problemas)

## Visão Geral

O Bot Cerebro suporta dois tipos de armazenamento de dados:
- **SQLite**: Banco de dados local, ideal para desenvolvimento e uso pessoal
- **Supabase**: Banco de dados PostgreSQL na nuvem, ideal para produção e acesso multi-usuário

A migração para o Supabase foi concluída com sucesso, permitindo maior escalabilidade e acesso remoto aos dados.

## Configuração do Supabase

### Pré-requisitos
1. Crie uma conta no [Supabase](https://supabase.com/) e um novo projeto
2. Obtenha as credenciais de acesso (URL e chaves)

### Configuração das Credenciais
Adicione suas credenciais do Supabase ao arquivo `secrets_cerebro.py`:

```python
# Credenciais do Supabase
SUPABASE_URL = "https://seu-projeto.supabase.co"
SUPABASE_KEY = "sua-chave-anônima"
SUPABASE_SERVICE_KEY = "sua-chave-de-serviço"  # Opcional, para operações administrativas
```

### Criação das Tabelas
Para criar as tabelas necessárias no Supabase:

1. Acesse o Editor SQL no painel do Supabase
2. Execute o script `scripts/criar_tabelas_supabase.sql` ou `scripts/criar_tabelas_supabase_simplificado.sql`

## Migração de Dados

A migração do SQLite para o Supabase já foi concluída, mas caso precise migrar novamente:

### Usando a Chave de Serviço (Recomendado)
```bash
python scripts/configurar_service_key.py  # Configure a chave de serviço
python scripts/migrar_para_supabase_direto.py  # Execute a migração
```

### Usando a Chave Anônima (Alternativa)
```bash
python scripts/migrar_para_supabase.py
```

## Estrutura das Tabelas

### Tabela `ideias`

| Coluna      | Tipo                    | Descrição                           |
|-------------|-------------------------|-------------------------------------|
| id          | BIGINT (Primary Key)    | Identificador único da ideia        |
| conteudo    | TEXT                    | Conteúdo da ideia                   |
| chat_id     | BIGINT                  | ID do chat do Telegram do usuário   |
| tipo        | TEXT                    | Tipo da mensagem (ideia, questão)   |
| resumo      | TEXT                    | Resumo ou categoria da ideia        |
| created_at  | TIMESTAMP WITH TIMEZONE | Data e hora de criação              |

### Tabela `brainstorms`

| Coluna      | Tipo                    | Descrição                           |
|-------------|-------------------------|-------------------------------------|
| id          | BIGINT (Primary Key)    | Identificador único do brainstorm   |
| ideia_id    | BIGINT (Foreign Key)    | Referência à ideia relacionada      |
| conteudo    | TEXT                    | Conteúdo do brainstorm              |
| created_at  | TIMESTAMP WITH TIMEZONE | Data e hora de criação              |

## Alternando entre SQLite e Supabase

Para alternar entre o SQLite e o Supabase, edite o arquivo `src/config/settings.py`:

```python
# Para usar o Supabase
USE_SUPABASE = True

# Para usar o SQLite local
USE_SUPABASE = False
```

## Políticas de Segurança

O Supabase utiliza Row Level Security (RLS) para controlar o acesso aos dados. Por padrão, a migração foi feita com o RLS desativado para simplificar o processo.

Para implementar políticas de segurança mais rigorosas:
1. Acesse o Editor SQL no painel do Supabase
2. Execute o script `scripts/atualizar_politicas_supabase.sql`

## Arquivos e Scripts Relacionados

### Arquivos de Configuração
- `src/config/settings.py`: Configuração para alternar entre SQLite e Supabase
- `src/config/supabase_config.py`: Configurações de conexão com o Supabase
- `secrets_cerebro.py`: Armazena as credenciais do Supabase

### Serviços e Repositórios
- `src/database/supabase_service.py`: Serviço para interagir com o Supabase
- `src/database/idea_repository.py`: Repositório para ideias (suporta SQLite e Supabase)
- `src/database/brainstorm_repository.py`: Repositório para brainstorms (suporta SQLite e Supabase)

### Scripts SQL
- `scripts/criar_tabelas_supabase.sql`: Cria tabelas com políticas de segurança
- `scripts/criar_tabelas_supabase_simplificado.sql`: Cria tabelas sem políticas de segurança
- `scripts/atualizar_politicas_supabase.sql`: Atualiza as políticas de segurança

### Scripts de Migração
- `scripts/configurar_service_key.py`: Configura a chave de serviço do Supabase
- `scripts/migrar_para_supabase_direto.py`: Script de migração usando a chave de serviço
- `scripts/migrar_para_supabase.py`: Script de migração usando a chave anônima

## Solução de Problemas

### Problemas de Conexão
- Verifique se as credenciais do Supabase estão corretas em `secrets_cerebro.py`
- Certifique-se de que o projeto no Supabase está ativo
- Verifique sua conexão com a internet

### Problemas de Permissão
- Verifique se o RLS está configurado corretamente
- Se estiver usando a chave anônima, certifique-se de que as políticas permitem as operações necessárias
- Para operações administrativas, use a chave de serviço

### Erros na Migração
- Verifique os logs para identificar o problema específico
- Certifique-se de que as tabelas foram criadas corretamente no Supabase
- Verifique se há conflitos de tipos de dados entre SQLite e PostgreSQL
