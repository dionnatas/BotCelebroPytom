# Revisão da Migração para Supabase

Este documento contém uma revisão completa dos arquivos e scripts criados durante o processo de migração do SQLite para o Supabase, com recomendações sobre quais devem ser mantidos e quais podem ser removidos.

## Arquivos Essenciais (Manter)

Estes arquivos são essenciais para o funcionamento do sistema com o Supabase:

1. **`src/config/supabase_config.py`**
   - Contém as configurações de conexão com o Supabase
   - Importa a chave de serviço do arquivo `secrets_cerebro.py`
   - **Decisão**: Manter

2. **`src/database/supabase_service.py`**
   - Implementa o serviço para interagir com o Supabase
   - Contém todos os métodos necessários para operações CRUD
   - **Decisão**: Manter

3. **`secrets_cerebro.py`**
   - Armazena a chave de serviço do Supabase junto com outras credenciais
   - **Decisão**: Manter (e garantir que esteja no .gitignore)

## Arquivos de Documentação (Manter apenas o mais atualizado)

1. **`MIGRACAO_CONCLUIDA.md`**
   - Documento mais recente com informações sobre a migração concluída
   - **Decisão**: Manter

2. **`README_SUPABASE.md`**
   - Contém informações gerais sobre a integração com o Supabase
   - **Decisão**: Manter

3. **`INSTRUCOES_MIGRACAO.md`** e **`INSTRUCOES_MIGRACAO_ATUALIZADO.md`**
   - Contêm instruções para o processo de migração
   - **Decisão**: Manter apenas o `INSTRUCOES_MIGRACAO_ATUALIZADO.md` e remover o outro

## Scripts de Migração (Podem ser arquivados)

Estes scripts foram usados para a migração inicial e podem ser arquivados (movidos para uma pasta `scripts/arquivados/`):

1. **`scripts/migrar_para_supabase.py`**
   - Script original de migração
   - **Decisão**: Arquivar

2. **`scripts/migrar_para_supabase_direto.py`**
   - Script de migração que usa a chave de serviço diretamente
   - **Decisão**: Arquivar

## Scripts de Criação de Tabelas (Manter para referência)

1. **`scripts/criar_tabelas_supabase.sql`**
   - Script SQL para criar tabelas com políticas de RLS
   - **Decisão**: Manter para referência futura

2. **`scripts/criar_tabelas_supabase_simplificado.sql`**
   - Versão simplificada sem políticas de RLS
   - **Decisão**: Manter para referência futura

## Scripts de Gerenciamento de Políticas (Manter)

1. **`scripts/atualizar_politicas_supabase.py`**
   - Script para atualizar as políticas de segurança no Supabase
   - **Decisão**: Manter para uso futuro

2. **`scripts/atualizar_politicas_supabase.sql`**
   - SQL para definir políticas de segurança
   - **Decisão**: Manter para uso futuro

## Recomendações Adicionais

1. **Criar uma pasta `scripts/arquivados/`**
   - Mover os scripts de migração para esta pasta
   - Isso mantém o histórico sem poluir o diretório principal

2. **Atualizar o `.gitignore`**
   - Adicionar `secrets_cerebro.py` ao `.gitignore` para evitar expor credenciais

3. **Documentação**
   - Remover `INSTRUCOES_MIGRACAO.md` (manter apenas a versão atualizada)
   - Atualizar o README principal do projeto para mencionar o uso do Supabase

4. **Backup**
   - Manter o banco de dados SQLite como backup por um período
   - Considerar implementar backups periódicos do Supabase
