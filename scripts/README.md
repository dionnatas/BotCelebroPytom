# Scripts do Bot Cerebro

Este diretório contém scripts para gerenciar, configurar e manter o Bot Cerebro.

## Estrutura de Diretórios

- `scripts/` - Scripts principais para operação do bot
- `scripts/arquivados/` - Scripts mantidos apenas para referência
- `scripts/arquivados/migracao/` - Scripts relacionados à migração para o Supabase (concluída)
- `scripts/legacy/` - Versões antigas dos scripts principais

## Scripts de Gerenciamento do Bot

| Script | Descrição |
|--------|-----------|
| `run_background.sh` | Inicia o bot em segundo plano |
| `stop_bot.sh` | Para o bot em execução |
| `status_bot.sh` | Verifica o status do bot |
| `restart_bot.sh` | Reinicia o bot |
| `status_bot_termux.sh` | Verifica o status do bot no ambiente Termux |

## Scripts de Configuração

| Script | Descrição |
|--------|-----------|
| `setup_bot.sh` | Configura o ambiente em sistemas Linux/macOS |
| `setup_termux.sh` | Configura o ambiente no Android/Termux |

## Scripts para Supabase

| Script | Descrição |
|--------|-----------|
| `atualizar_politicas_supabase.sql` | Define políticas de acesso no Supabase |
| `criar_tabelas_supabase.sql` | Cria as tabelas necessárias no Supabase |
| `criar_tabelas_supabase_simplificado.sql` | Versão simplificada para criar tabelas no Supabase |
| `configurar_service_key.py` | Configura a chave de serviço do Supabase |

## Scripts de Manutenção

| Script | Descrição |
|--------|-----------|
| `fix_audio.py` | Corrige problemas relacionados ao processamento de áudio |
| `fix_termux_audio.py` | Corrige problemas de áudio específicos do Termux |
| `update_cerebro.py` | Atualiza o bot para a versão mais recente |

## Scripts Arquivados

Os scripts na pasta `arquivados/` são mantidos apenas para referência e não são necessários para a operação normal do bot. Isso inclui:

- Scripts de migração para o Supabase (a migração já foi concluída)
- Scripts de correção específicos que não são mais necessários
- Versões antigas de scripts que foram substituídos

## Uso Recomendado

Para operação normal do bot:

1. **Configuração inicial**: `./scripts/setup_bot.sh` (ou `./scripts/setup_termux.sh` no Android)
2. **Iniciar o bot**: `./scripts/run_background.sh`
3. **Verificar status**: `./scripts/status_bot.sh`
4. **Parar o bot**: `./scripts/stop_bot.sh`
5. **Reiniciar o bot**: `./scripts/restart_bot.sh`
