# Configuração do GitHub Actions para Deploy Automático

Este documento explica como configurar o GitHub Actions para realizar deploy automático do Bot Cerebro em seu servidor sempre que houver um push para a branch `main`.

## Pré-requisitos

1. Acesso SSH ao servidor onde o Bot Cerebro será executado
2. Permissões para configurar secrets no repositório GitHub
3. Git instalado no servidor

## Configuração dos Secrets

Para que o workflow funcione corretamente, você precisa configurar os seguintes secrets no seu repositório GitHub:

1. Acesse seu repositório no GitHub
2. Vá para **Settings** > **Secrets and variables** > **Actions**
3. Clique em **New repository secret**
4. Adicione os seguintes secrets:

| Nome do Secret | Descrição | Exemplo |
|---------------|-----------|---------|
| `SSH_PRIVATE_KEY` | Chave SSH privada para acessar o servidor | Conteúdo do arquivo `~/.ssh/id_rsa` |
| `SSH_KNOWN_HOSTS` | Fingerprint do servidor para evitar ataques MITM | Saída de `ssh-keyscan -H seu_servidor.com` |
| `DEPLOY_HOST` | Endereço do servidor | `seu_servidor.com` ou `123.456.789.0` |
| `DEPLOY_USER` | Usuário SSH no servidor | `usuario` |
| `DEPLOY_PATH` | Caminho para o diretório do Bot Cerebro no servidor | `/home/usuario/BotCelebroPytom` |

### Como gerar os valores dos secrets

#### SSH_PRIVATE_KEY
```bash
# Exibir a chave privada para copiar
cat ~/.ssh/id_rsa
```

#### SSH_KNOWN_HOSTS
```bash
# Substitua 'seu_servidor.com' pelo endereço do seu servidor
ssh-keyscan -H seu_servidor.com
```

#### Verificar configuração no servidor

Certifique-se de que o diretório do projeto no servidor está configurado corretamente:

```bash
# No servidor
cd /caminho/para/BotCelebroPytom
git remote -v  # Deve apontar para o seu repositório GitHub
```

## Como funciona o deploy automático

1. Quando você faz push para a branch `main`, o workflow é acionado automaticamente
2. O GitHub Actions se conecta ao seu servidor via SSH
3. Faz backup do banco de dados atual
4. Atualiza o código do repositório
5. Atualiza as dependências
6. Reinicia o bot

## Execução manual

Você também pode acionar o workflow manualmente:

1. Acesse seu repositório no GitHub
2. Vá para a aba **Actions**
3. Selecione o workflow **Deploy Bot Cerebro**
4. Clique em **Run workflow**
5. Selecione a branch e clique em **Run workflow**

## Solução de problemas

Se o deploy falhar, verifique:

1. **Logs do GitHub Actions**: Acesse a aba Actions no GitHub para ver os logs detalhados
2. **Permissões SSH**: Verifique se a chave SSH tem permissão para acessar o servidor
3. **Caminhos no servidor**: Confirme se o `DEPLOY_PATH` está correto
4. **Permissões de arquivo**: Certifique-se de que os scripts têm permissão de execução no servidor

Para mais informações, consulte a [documentação oficial do GitHub Actions](https://docs.github.com/pt/actions).
