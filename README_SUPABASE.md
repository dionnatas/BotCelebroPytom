# Migração para o Supabase

Este documento descreve o processo de migração do banco de dados local SQLite para o Supabase, um serviço de banco de dados PostgreSQL na nuvem.

## Configuração do Supabase

1. Crie uma conta no [Supabase](https://supabase.com/) e um novo projeto
2. Obtenha as credenciais de acesso (URL e chave anônima) e configure-as no arquivo `src/config/supabase_config.py`
3. Execute o script SQL para criar as tabelas necessárias:
   - Copie o conteúdo do arquivo `scripts/criar_tabelas_supabase.sql`
   - Cole no Editor SQL do Supabase e execute

## Migração de Dados

Para migrar seus dados existentes do SQLite para o Supabase, execute o script de migração:

```bash
python scripts/migrar_para_supabase.py
```

Este script irá:
1. Criar um backup do seu banco de dados SQLite local
2. Ler todas as ideias e brainstorms do banco local
3. Inserir esses dados no Supabase
4. Registrar o progresso e quaisquer erros no log

## Alternando entre SQLite e Supabase

Você pode alternar entre o banco de dados SQLite local e o Supabase modificando a configuração `USE_SUPABASE` no arquivo `src/config/settings.py`:

```python
# Para usar o Supabase
USE_SUPABASE = True

# Para usar o SQLite local
USE_SUPABASE = False
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

## Segurança

O Supabase implementa Row Level Security (RLS), que permite controlar o acesso aos dados com base no usuário autenticado. As políticas configuradas garantem que:

1. Usuários só podem ver suas próprias ideias e brainstorms
2. Superusuários podem ver todas as ideias e brainstorms
3. Usuários só podem apagar suas próprias ideias

## Solução de Problemas

Se encontrar problemas durante a migração ou uso do Supabase:

1. Verifique os logs em `var/logs/cerebro.log`
2. Certifique-se de que as credenciais do Supabase estão corretas
3. Verifique se as tabelas foram criadas corretamente no Supabase
4. Temporariamente, defina `USE_SUPABASE = False` para voltar ao SQLite local

## Limitações

- O Supabase tem limites de uso no plano gratuito (500MB de armazenamento, 100MB de transferência/dia)
- A latência pode ser maior comparada ao banco de dados local
- É necessária conexão com a internet para acessar o banco de dados
