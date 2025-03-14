# Instruções para Migração para o Supabase

Este documento contém instruções detalhadas para migrar o banco de dados do Bot Cerebro do SQLite local para o Supabase.

## Pré-requisitos

1. Conta no Supabase (gratuita ou paga)
2. Projeto criado no Supabase
3. URL e chaves de API do projeto (anônima e de serviço)

## Etapas para Migração

### 1. Configurar a Chave de Serviço

A chave de serviço é necessária para operações administrativas como criação de tabelas e migração de dados. Ela permite contornar as políticas de segurança (RLS).

```bash
# Execute o script de configuração da chave de serviço
python3 scripts/configurar_service_key.py
```

Siga as instruções na tela para configurar a chave de serviço como variável de ambiente.

### 2. Criar as Tabelas no Supabase

Existem duas opções para criar as tabelas:

#### Opção 1: Usando o SQL Editor no Supabase (Recomendado para Desenvolvimento)

1. Acesse o painel do Supabase
2. Vá para SQL Editor
3. Cole o conteúdo do arquivo `scripts/criar_tabelas_supabase_simplificado.sql`
4. Execute o script

Esta opção desativa as políticas de segurança (RLS) para facilitar o desenvolvimento e testes.

#### Opção 2: Usando o SQL Editor no Supabase (Recomendado para Produção)

1. Acesse o painel do Supabase
2. Vá para SQL Editor
3. Cole o conteúdo do arquivo `scripts/criar_tabelas_supabase.sql`
4. Execute o script

Esta opção implementa políticas de segurança (RLS) para controlar o acesso aos dados.

### 3. Migrar os Dados

Após criar as tabelas, execute o script de migração:

```bash
python3 scripts/migrar_para_supabase.py
```

Este script:
- Cria um backup do banco de dados SQLite
- Lê todas as ideias e brainstorms do SQLite
- Insere os dados no Supabase

### 4. Verificar a Migração

Para verificar se a migração foi bem-sucedida:

1. Acesse o painel do Supabase
2. Vá para Table Editor
3. Verifique se as tabelas `ideias` e `brainstorms` contêm os dados migrados

### 5. Configurar o Bot para Usar o Supabase

Edite o arquivo `src/config/settings.py` e defina:

```python
USE_SUPABASE = True
```

Isso fará com que o bot use o Supabase em vez do SQLite local.

## Solução de Problemas

### Erro de Política de Segurança (RLS)

Se você encontrar erros relacionados a políticas de segurança:

1. Verifique se está usando a chave de serviço correta
2. Considere usar o script simplificado que desativa as políticas de segurança
3. Verifique as políticas RLS no painel do Supabase (Database > Policies)

### Erro de Conexão

Se você encontrar erros de conexão:

1. Verifique se as URLs e chaves em `src/config/supabase_config.py` estão corretas
2. Verifique se o projeto no Supabase está ativo
3. Verifique se o IP do seu servidor não está bloqueado no Supabase

## Reversão

Se precisar reverter para o SQLite:

1. Edite o arquivo `src/config/settings.py` e defina:

```python
USE_SUPABASE = False
```

2. O bot voltará a usar o banco de dados SQLite local.

## Próximos Passos

Após a migração bem-sucedida:

1. Teste todas as funcionalidades do bot para garantir que estão funcionando corretamente
2. Considere implementar autenticação de usuários usando o Supabase Auth
3. Explore recursos adicionais do Supabase como Realtime e Storage
