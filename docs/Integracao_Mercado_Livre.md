# Integração Mercado Livre

Conexão com a API do Mercado Livre feita **pelo GitHub Actions**
(`.github/workflows/meli.yml`). Este documento não contém credenciais.

## Por que pelo GitHub Actions

No Mercado Livre o access token vale 6 horas e o **refresh token é de uso único**:
cada renovação devolve um refresh token novo e invalida o anterior. Por isso o
token não pode ficar fixo numa variável de ambiente, como acontece com a Amazon.

O workflow é o **único** lugar que renova o token. Logo depois de renovar, ele
grava o novo valor no secret `MELI_REFRESH_TOKEN`. Não renove o token em nenhum
outro lugar (sessão do Claude Code, computador local, Postman), porque o secret
ficaria com um token já invalidado.

```
GitHub Actions (secrets MELI_*)
   | POST client_id + client_secret + refresh_token
   v
https://api.mercadolibre.com/oauth/token --> access_token (6 h) + refresh_token NOVO
   |                                                         |
   | Authorization: Bearer                                   v
   v                                     gh secret set MELI_REFRESH_TOKEN
https://api.mercadolibre.com (users, items...)
```

## 1. Criar o app no Mercado Livre

1. Acesse https://developers.mercadolivre.com.br/devcenter com a conta da loja.
2. Crie uma aplicação. Em **URI de redirect**, cadastre uma URL HTTPS sua, por
   exemplo `https://github.com/solveonebr-design/AgenteIA`. Ela só serve para
   mostrar o `code` na barra de endereço; não precisa de servidor.
3. Deixe **PKCE desativado** (o workflow não envia `code_verifier`).
4. Escopos: leitura e escrita (`read`, `write`) e `offline_access`, que é o que
   gera o refresh token.
5. Anote o **App ID** e a **Secret Key**.

## 2. Token do GitHub para gravar o secret

O `GITHUB_TOKEN` padrão do Actions não pode alterar secrets. Crie um
**fine-grained personal access token** em GitHub > Settings > Developer settings
> Personal access tokens > Fine-grained tokens:

- Repository access: somente `solveonebr-design/AgenteIA`
- Permissions > Repository > **Secrets: Read and write** (nada mais)
- Validade: a maior que você aceitar; anote a data para renovar.

## 3. Cadastrar no repositório

GitHub > AgenteIA > Settings > Secrets and variables > Actions.

| Tipo     | Nome                 | Conteúdo                                   |
|----------|----------------------|--------------------------------------------|
| Secret   | `MELI_CLIENT_ID`     | App ID                                     |
| Secret   | `MELI_CLIENT_SECRET` | Secret Key                                 |
| Secret   | `GH_PAT_SECRETS`     | Token do passo 2                           |
| Secret   | `MELI_REFRESH_TOKEN` | Deixe sem cadastrar: o workflow cria       |
| Variable | `MELI_REDIRECT_URI`  | A mesma URI cadastrada no app, idêntica    |

## 4. Primeira autorização

1. Abra no navegador, logado na conta da loja (troque `APP_ID` e a URI):

   ```
   https://auth.mercadolivre.com.br/authorization?response_type=code&client_id=APP_ID&redirect_uri=https://github.com/solveonebr-design/AgenteIA
   ```

2. Autorize. O navegador vai para a URI com `?code=TG-...` no endereço.
3. Em até ~10 minutos: Actions > **Mercado Livre** > Run workflow >
   ação `autorizar`, cole o `code` e execute.
4. O workflow troca o code por tokens, grava `MELI_REFRESH_TOKEN`, testa
   `/users/me` e salva `data/meli_usuario.json`.

O `code` é de uso único e só funciona junto com a Secret Key, por isso não há
risco em colá-lo no formulário do workflow. Mesmo assim ele é mascarado no log.

## 5. Uso

| Ação        | O que faz                                                        | Saída                                   |
|-------------|------------------------------------------------------------------|-----------------------------------------|
| `teste`     | Renova o token e chama `/users/me`                               | `data/meli_usuario.json`                |
| `listar`    | Renova o token e lista todos os anúncios (`scripts/meli_listar_produtos.py`) | `data/meli_produtos.csv` e `.json` |
| `mais_vendidos` | Top 20 mais vendidos de cada categoria principal (`scripts/meli_mais_vendidos.py`). Com `categoria` preenchida (ex.: `MLB1574`), percorre as subcategorias dela | `data/meli_mais_vendidos.csv` e `.json` |
| `autorizar` | Troca um `code` novo por tokens (primeira vez ou após `invalid_grant`) | `data/meli_usuario.json`          |

- **Agendamento:** toda segunda-feira às 09:17 UTC roda `teste`, o que renova o
  token e impede que ele expire (validade de 6 meses).
- **Fila:** `concurrency: meli-token` garante uma execução por vez; duas
  simultâneas gastariam o mesmo refresh token.
- **De uma sessão do Claude Code:** peça para disparar o workflow (ação
  `listar`, por exemplo) e ler os arquivos em `data/` depois do commit
  automático.
- Workflows com `workflow_dispatch` e `schedule` só aparecem e rodam a partir da
  **branch padrão** (`main`). O arquivo precisa estar mesclado em `main`.

## 6. Solução de problemas

| Sintoma                                   | Causa                                           | Ação                                         |
|-------------------------------------------|-------------------------------------------------|----------------------------------------------|
| `invalid_grant` na renovação              | Token já usado, revogado ou expirado            | Refazer a seção 4                            |
| `invalid_grant` em `autorizar`            | Code expirado/usado ou redirect URI diferente   | Gerar code novo; conferir `MELI_REDIRECT_URI`|
| `invalid_client`                          | App ID ou Secret Key errados                    | Conferir secrets                             |
| `Secret ausente: GH_PAT_SECRETS`          | Token do passo 2 não cadastrado                 | Cadastrar e refazer a seção 4 (o refresh já foi gasto) |
| `HTTP 403` ao gravar o secret             | PAT sem "Secrets: Read and write" ou vencido    | Gerar novo PAT e refazer a seção 4           |
| 429                                       | Limite de requisições                           | O script espera e tenta de novo (até 6 vezes)|
| Agendamento parou                         | GitHub desativa cron após 60 dias sem atividade em repositório público | Reativar em Actions          |

## 7. Segurança

- Credenciais só em secrets do GitHub. Nunca colar no chat, em arquivos ou logs.
- O workflow imprime apenas o código do erro do OAuth e grava em `data/` só
  dados públicos da conta (sem e-mail, telefone ou documento).
- Gravações em anúncios (criar, alterar preço/estoque, excluir) ainda não estão
  implementadas. Quando forem, seguir o mesmo fluxo da Amazon: validar antes
  com `POST /items/validate`, mostrar a proposta e só aplicar com confirmação.
