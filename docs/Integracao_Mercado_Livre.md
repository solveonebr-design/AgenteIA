# Integração Mercado Livre

Documentação técnica para recriar ou operar a integração em uma nova sessão do Claude Code.

- Conta: **SOLVEONE** (ID de usuário 3741253547) · Site: Mercado Livre Brasil (MLB)
- Repositório: github.com/solveonebr-design/AgenteIA · branch `main`
- Versão de 10/10/2026

> Este documento não contém credenciais. Elas ficam só nos *secrets* do repositório no
> GitHub. Nunca cole Secret Key, tokens do GitHub ou o `code` de autorização no chat, em
> arquivos do repositório ou em logs.

## 1. Visão geral

A integração usa a API oficial do Mercado Livre (OAuth 2.0). Diferente da Amazon, ela
**roda no GitHub Actions**, e não na sessão do Claude Code. O motivo é que o refresh token
do Mercado Livre é de **uso único**: cada renovação devolve um token novo e invalida o
anterior. Por isso o token não pode ficar fixo em uma variável de ambiente.

O workflow `.github/workflows/meli.yml` é o **único** lugar que renova o token. Logo depois
de renovar, ele grava o novo valor no secret `MELI_REFRESH_TOKEN`.

```
GitHub Actions (secrets MELI_*)
   | POST client_id + client_secret + refresh_token
   v
https://api.mercadolibre.com/oauth/token --> access_token (6 h) + refresh_token NOVO
   |                                                         |
   | Authorization: Bearer <access_token>                    v
   v                                     gh secret set MELI_REFRESH_TOKEN (via GH_PAT_SECRETS)
https://api.mercadolibre.com (users, items, highlights, products...)
   |
   v
data/*.json e data/*.csv  --> commit automático na branch em que o workflow rodou
```

Regra de ouro: **não renove o token em nenhum outro lugar** (sessão do Claude Code, Postman,
computador local). Se renovar fora do workflow, o secret fica com um token já invalidado e
será preciso refazer a autorização (seção 5).

### Dados da conta (não sigilosos)

| Item | Valor |
|---|---|
| Apelido | SOLVEONE |
| ID de usuário | 3741253547 |
| Site | MLB (Brasil) |
| Aplicação no DevCenter | AgenteIAML |
| Client ID (App ID) | 1261516105183743 |
| URI de redirect | https://github.com/solveonebr-design/AgenteIA |

O Client ID não é segredo (aparece no link de autorização). A **Secret Key** é segredo.

## 2. Aplicação no Mercado Livre (DevCenter)

Só é preciso refazer esta seção se a aplicação AgenteIAML for apagada.

1. Acesse https://developers.mercadolivre.com.br/devcenter com a conta da loja e clique em
   **Criar nova aplicação**.
2. **Informações básicas:** Nome `AgenteIAML`, Nome curto `SOLVEONEBR`, Descrição "Integração
   interna da loja SOLVEONEBR para consultar e gerenciar os próprios anúncios, estoque e
   vendas no Mercado Livre de forma automatizada.", Propósito **Negócios**, Usuários
   **1 a 10**. Logotipo opcional.
3. **Configuração e scopes:**
   - URIs de redirect: `https://github.com/solveonebr-design/AgenteIA` (sem barra no final;
     deixe o segundo campo vazio).
   - Fluxos OAuth: **Authorization Code** e **Refresh Token** marcados (Refresh Token é
     obrigatório: sem ele a conexão cai a cada 6 horas). Client Credentials não é usado.
   - PKCE: **desmarcado** (o workflow não envia `code_verifier`).
   - Negócios: **Mercado Livre** (VIS desmarcado).
4. **Permissões:** Leitura e escrita em Usuários, Comunicações, Publicação e sincronização,
   Publicidade, Faturamento, Promoções e Venda e envios; Leitura em Métricas do negócio.
5. **Tópicos e notificações:** deixe tudo desmarcado e a URL de notificações em branco (não
   há servidor recebendo avisos).
6. Salve. Na lista "Minhas aplicações", o Client ID aparece no cartão. A Secret Key fica em
   ⋮ > **Editar**. Não clique em "Renovar/Gerar nova chave" sem necessidade (invalida a
   atual) nem em "Apagar".

Na "Configuração de segurança" do app, **não** ative PKCE nem restrição por IP (os IPs do
GitHub Actions mudam a cada execução). "Aplicativo não certificado" é normal para uso
próprio.

## 3. Token do GitHub (GH_PAT_SECRETS)

O `GITHUB_TOKEN` padrão do Actions não pode alterar secrets, por isso o workflow usa um
token pessoal.

1. Acesse https://github.com/settings/personal-access-tokens/new (Fine-grained token).
2. Token name: `AgenteIA secrets Mercado Livre`. Resource owner: `solveonebr-design`.
3. Expiration: **Custom**, a data mais distante permitida (até 1 ano). Anote o vencimento.
4. Repository access: **Only select repositories** > `AgenteIA`.
5. Permissions > Repositories > Add permissions > **Secrets: Read and write**. O GitHub
   inclui sozinho Metadata: Read-only. Nada mais; a aba Account fica com 0.
6. **Generate token**, copie o `github_pat_...` (só aparece uma vez) e cadastre como secret
   `GH_PAT_SECRETS` (seção 4).

Quando o token vencer: gere outro igual e atualize o secret `GH_PAT_SECRETS` (lápis ao lado
do nome). Se ele vencer antes de ser trocado, a execução seguinte renova o refresh token mas
não consegue salvá-lo; nesse caso, troque o PAT e refaça a autorização (seção 5).

## 4. Secrets e variável no repositório

GitHub > AgenteIA > **Settings** > Secrets and variables > **Actions**
(link direto: https://github.com/solveonebr-design/AgenteIA/settings/secrets/actions).
Use **Repository secrets** (botão verde *New repository secret*), não "Environment secrets".

| Tipo | Nome (exato) | Conteúdo |
|---|---|---|
| Secret | `MELI_CLIENT_ID` | Client ID (App ID) do DevCenter |
| Secret | `MELI_CLIENT_SECRET` | Secret Key do DevCenter |
| Secret | `GH_PAT_SECRETS` | Token `github_pat_...` da seção 3 |
| Secret | `MELI_REFRESH_TOKEN` | **Não cadastrar à mão**: o workflow cria e atualiza |
| Variable (aba Variables) | `MELI_REDIRECT_URI` | `https://github.com/solveonebr-design/AgenteIA` |

Cuidados:

- No campo *Value* da variável vai **só a URL**, sem `MELI_REDIRECT_URI=` na frente, sem
  espaços e sem barra final. Ela precisa ser idêntica à cadastrada no app.
- Esta página não tem relação com a integração da Amazon. A Amazon usa variáveis `SPAPI_*`
  no ambiente do Claude Code. Não crie nem apague nada com nome `SPAPI_` aqui.

## 5. Autorização (primeira vez ou após `invalid_grant`)

Faça tudo em sequência: o `code` vale cerca de 10 minutos e só pode ser usado uma vez.

1. Abra https://github.com/solveonebr-design/AgenteIA/actions e clique em **Mercado Livre**.
2. Em outra aba, logada no Mercado Livre com a conta da loja, abra:

   ```
   https://auth.mercadolivre.com.br/authorization?response_type=code&client_id=1261516105183743&redirect_uri=https://github.com/solveonebr-design/AgenteIA
   ```

3. Autorize. O navegador volta para a página do repositório; clique na **barra de
   endereço** e copie o trecho depois de `code=` (começa com `TG-`). Exemplo:
   `https://github.com/solveonebr-design/AgenteIA?code=TG-6708a1b2c3d4e5f6-123456789`
   → o code é `TG-6708a1b2c3d4e5f6-123456789`.
4. Em Actions > Mercado Livre > **Run workflow**: branch `main`, ação **`autorizar`**,
   campo code com o `TG-...`. Clique em Run workflow.
5. Em cerca de 1 minuto a execução fica verde. Ela grava `MELI_REFRESH_TOKEN`, testa
   `/users/me` e salva `data/meli_usuario.json` (deve mostrar `"nickname": "SOLVEONE"`).

Se o Client ID mudar (app recriado), troque o número no link do passo 2.

## 6. Ações do workflow

Actions > **Mercado Livre** > Run workflow. Os workflows com `workflow_dispatch` e
`schedule` só aparecem e rodam a partir da branch padrão (`main`).

| Ação | Campos | O que faz | Saída |
|---|---|---|---|
| `teste` | — | Renova o token e chama `/users/me` | `data/meli_usuario.json` |
| `listar` | — | Lista todos os anúncios da conta (`scripts/meli_listar_produtos.py`) | `data/meli_produtos.csv` e `.json` |
| `mais_vendidos` | `categoria` opcional | Top 20 mais vendidos de cada categoria principal; com `categoria` (ex.: `MLB1574`), de cada subcategoria dela (`scripts/meli_mais_vendidos.py`) | `data/meli_mais_vendidos.csv` e `.json` |
| `validar_anuncio` | `arquivo` | Confere o anúncio de `anuncios/<nome>.json` sem publicar (seção 6.1) | `data/meli_anuncio_<nome>_validar.json` |
| `publicar_anuncio` | `arquivo`, `confirmar` = `PUBLICAR` | Valida de novo e publica o anúncio e a descrição (seção 6.1) | `data/meli_anuncio_<nome>_publicar.json` |
| `previa_edicao` | `arquivo` | Mostra "antes → depois" da edição de um anúncio publicado, sem alterar (seção 6.2) | `data/meli_edicao_<nome>_previa.json` |
| `editar_anuncio` | `arquivo`, `confirmar` = `EDITAR` | Salva cópia do estado atual e aplica a edição (seção 6.2) | `data/meli_edicao_<nome>_aplicar.json` e `..._antes_<data>.json` |
| `autorizar` | `code` | Troca um `code` novo por tokens (seção 5) | `data/meli_usuario.json` |

- **Agendamento:** toda segunda-feira às 09:17 UTC roda `teste`, o que renova o token e
  impede que ele expire (validade de 6 meses sem uso).
- **Fila:** `concurrency: meli-token` garante uma execução por vez; duas simultâneas
  gastariam o mesmo refresh token.
- **Commit automático:** os arquivos em `data/` são gravados na branch em que o workflow
  rodou.
- Os CSV usam `;` como separador e vírgula decimal, para abrir direto no Excel.

### 6.1 Criar anúncios

Preparado, mas nenhum anúncio foi publicado até 10/10/2026. O conteúdo (título, ficha
técnica, fotos, descrição, preço) segue **`docs/Boas_Praticas_Anuncio_ML.md`**. Fluxo:

1. Copiar `anuncios/_modelo.json` para `anuncios/<nome>.json` (sem `_` no início; arquivos
   com `_` são modelos e o script recusa) e preencher: `title` (até 60 caracteres),
   `category_id`, `price`, `available_quantity`, `listing_type_id` (`gold_special` =
   Clássico, `gold_pro` = Premium), `shipping`, `attributes` (marca, modelo, SKU, código de
   barras ou `EMPTY_GTIN_REASON`, medidas e peso da embalagem), `fotos` e `descricao`.
2. **Fotos:** URL pública ou caminho de arquivo do repositório (ex.: `fotos/x.jpg`). Os
   arquivos são enviados com `POST /pictures/items/upload`, então o repositório não precisa
   ser público para as fotos. Formatos JPG ou PNG, mínimo 500 px, ideal 1200 px.
3. Rodar a ação **`validar_anuncio`** com `arquivo` = `anuncios/<nome>.json`. O script roda
   as checagens de qualidade (`scripts/meli_qualidade.py`: título, ficha técnica, fotos e
   descrição, com nota de 0 a 100 e itens BLOQUEIA/ALERTA/DICA) e chama
   `POST /items/validate`. Itens BLOQUEIA impedem a publicação. Meta: nota de 85 ou mais.
   Execução verde = válido; vermelha = ver os erros no log e em
   `data/meli_anuncio_<nome>_validar.json`. Corrigir e repetir até ficar válido.
4. Mostrar a proposta ao dono da conta e obter confirmação explícita.
5. Rodar **`publicar_anuncio`** com o mesmo `arquivo` e `confirmar` = `PUBLICAR`
   (sem isso o passo para). O script valida de novo, cria o anúncio (`POST /items`), grava
   a descrição (`POST /items/{id}/description`) e salva ID, status e link em
   `data/meli_anuncio_<nome>_publicar.json`.

Rodar `publicar_anuncio` duas vezes cria **dois anúncios**. Para alterar um anúncio já
publicado, use a edição (seção 6.2).

Possíveis bloqueios na primeira publicação: conta de vendedor incompleta (endereço,
documentos, Mercado Pago) ou categoria que exige vínculo com o catálogo.

### 6.2 Editar anúncios publicados

1. Copiar `anuncios/edicoes/_modelo.json` para `anuncios/edicoes/<nome>.json` e preencher:
   - `item_id` (ex.: `MLB1234567890`) **ou** `anuncio` (nome do arquivo usado na
     publicação; o ID é lido de `data/meli_anuncio_<anuncio>_publicar.json`);
   - `alteracoes`: só o que muda. Campos aceitos: `price`, `available_quantity`, `status`
     (`active`, `paused`, `closed`), `attributes`, `shipping`, `sale_terms`, `title`,
     `condition`, `video_id`;
   - `fotos` (opcional): **substitui todas** as fotos;
   - `descricao` (opcional): substitui a descrição.
2. Rodar **`previa_edicao`** com `arquivo` = `anuncios/edicoes/<nome>.json`. O log mostra o
   anúncio atual, cada mudança no formato `campo: antes -> depois`, problemas (campo não
   editável, título acima de 60 caracteres, nada a mudar) e a nota de qualidade de como o
   anúncio vai ficar depois da edição. Nada é alterado.
3. Mostrar a prévia ao dono da conta e obter confirmação.
4. Rodar **`editar_anuncio`** com o mesmo `arquivo` e `confirmar` = `EDITAR`. O script
   salva uma cópia do estado anterior em `data/meli_edicao_<nome>_antes_<data>.json`
   (para poder desfazer) e aplica com `PUT /items/{id}` e
   `PUT /items/{id}/description`.

Regras do Mercado Livre: `title` e `condition` **só mudam se o anúncio não tiver vendas**
(o script bloqueia antes de enviar). `status` = `closed` **finaliza o anúncio e não dá para
reativar**; para tirar do ar temporariamente use `paused`. Tipo de anúncio
(Clássico/Premium) e categoria não são alterados por esta ação.

Para desfazer uma edição: criar um arquivo de edição com os valores da cópia
`..._antes_<data>.json` e aplicar do mesmo jeito.

### Categorias principais (códigos)

Úteis no campo `categoria` da ação `mais_vendidos`:

| Código | Categoria | Código | Categoria |
|---|---|---|---|
| MLB5672 | Acessórios para Veículos | MLB1000 | Eletrônicos, Áudio e Vídeo |
| MLB271599 | Agro | MLB1276 | Esportes e Fitness |
| MLB1403 | Alimentos e Bebidas | MLB263532 | Ferramentas |
| MLB1071 | Animais | MLB12404 | Festas e Lembrancinhas |
| MLB1367 | Antiguidades e Coleções | MLB1144 | Games |
| MLB1368 | Arte, Papelaria e Armarinho | MLB1499 | Indústria e Comércio |
| MLB1384 | Bebês | MLB1648 | Informática |
| MLB1246 | Beleza e Cuidado Pessoal | MLB1182 | Instrumentos Musicais |
| MLB1132 | Brinquedos e Hobbies | MLB3937 | Joias e Relógios |
| MLB1430 | Calçados, Roupas e Bolsas | MLB1196 | Livros, Revistas e Comics |
| MLB1039 | Câmeras e Acessórios | MLB1168 | Música, Filmes e Seriados |
| MLB1574 | Casa, Móveis e Decoração | MLB264586 | Saúde |
| MLB1051 | Celulares e Telefones | MLB1953 | Mais Categorias |
| MLB1500 | Construção | MLB5726 | Eletrodomésticos |

Carros, Motos e Outros, Imóveis, Ingressos e Serviços não têm ranking de mais vendidos.

## 7. Estrutura do repositório

| Caminho | Função |
|---|---|
| `.github/workflows/meli.yml` | Workflow do Mercado Livre: renovação do token, gravação do secret, ações `teste`, `listar`, `mais_vendidos`, `autorizar` e commit dos resultados |
| `scripts/meli_listar_produtos.py` | Lista os anúncios da conta (`/users/{id}/items/search` com `search_type=scan` + multiget `/items`). Lê `MELI_ACCESS_TOKEN`; não renova token |
| `scripts/meli_anuncio.py` | Valida (`POST /items/validate`) ou publica (`POST /items` + descrição) um anúncio a partir de `anuncios/<nome>.json`; faz upload das fotos locais |
| `scripts/meli_qualidade.py` | Checagens de qualidade (título, ficha técnica, fotos, descrição) e nota 0-100, conforme `docs/Boas_Praticas_Anuncio_ML.md` |
| `scripts/meli_editar_anuncio.py` | Prévia (antes → depois) e aplicação de edições em anúncios publicados (`GET`/`PUT /items/{id}`, `PUT /items/{id}/description`) |
| `anuncios/` | Arquivos dos anúncios; `_modelo.json` é o modelo comentado |
| `anuncios/edicoes/` | Arquivos de edição; `_modelo.json` é o modelo comentado |
| `scripts/meli_mais_vendidos.py` | Top 20 por categoria (`/highlights/MLB/category/{id}`), completando título, preço e link via `/items`, `/products/{id}`, `/products/{id}/items` e `/user-products/{id}`. Lista no log as rotas que falharam |
| `data/` | Saídas: `meli_usuario.json`, `meli_produtos.*`, `meli_mais_vendidos.*` (e os arquivos da Amazon) |
| `docs/Integracao_Mercado_Livre.md` / `.pdf` | Este documento |
| `docs/Boas_Praticas_Anuncio_ML.md` / `.pdf` | Guia de conteúdo dos anúncios (título, ficha técnica, fotos, descrição, preço) |
| `docs/gerar_documentacao_meli.py` | Gera os dois PDFs a partir dos `.md` |
| `.github/workflows/main.yml` | Teste de conexão da **Amazon** (independente desta integração) |

## 8. APIs utilizadas

| Operação | Método e caminho | Uso |
|---|---|---|
| Token | `POST /oauth/token` (`authorization_code` ou `refresh_token`) | Access token (6 h) + refresh token novo |
| Conta | `GET /users/me` | Teste de conexão |
| Anúncios da conta | `GET /users/{id}/items/search?search_type=scan&limit=100&scroll_id=` | IDs de todos os anúncios (sem limite de 1.000) |
| Detalhes | `GET /items?ids=...` (até 20) | Título, preço, estoque, status |
| Categorias | `GET /sites/MLB/categories`, `GET /categories/{id}` | Categorias principais e subcategorias |
| Mais vendidos | `GET /highlights/MLB/category/{id}` | Top 20 da categoria (tipos ITEM, PRODUCT, USER_PRODUCT) |
| Produto de catálogo | `GET /products/{id}`, `GET /products/{id}/items?limit=1` | Nome, foto e preço da oferta vencedora |
| Atributos da categoria | `GET /categories/{id}/attributes` | Atributos obrigatórios (`required`, `catalog_required`) |
| Fotos | `POST /pictures/items/upload` (multipart) | Enviar foto local; devolve o id usado em `pictures` |
| Validação | `POST /items/validate` | Valida o anúncio sem publicar (204 = válido) |
| Publicação | `POST /items`, `POST /items/{id}/description` | Cria o anúncio e a descrição |
| Edição | `GET /items/{id}`, `PUT /items/{id}`, `PUT /items/{id}/description` | Lê o estado atual e aplica as alterações |

Limitação conhecida: a API responde **403** para detalhes de anúncios (`/items/{id}`) e
user products (`/user-products/{id}`) de **outros vendedores**. No ranking de mais vendidos,
esses itens ficam só com posição, código e link (cerca de 130 de 560 em 10/10/2026).

Links montados quando a API não devolve o permalink: produto de catálogo
`https://www.mercadolivre.com.br/p/{id}`, user product
`https://www.mercadolivre.com.br/up/{id}`, anúncio
`https://produto.mercadolivre.com.br/MLB-{número}`.

## 9. Operar pelo Claude Code

A sessão do Claude Code **não** acessa a API do Mercado Livre diretamente (e não deve
renovar o token). Ela opera assim:

1. Dispara o workflow pelas ferramentas do GitHub (`actions_run_trigger`, workflow
   `meli.yml`, inputs `acao` e, se for o caso, `categoria`). Para testar mudanças sem mexer
   na `main`, pode disparar numa branch de trabalho: o workflow usa a versão do arquivo
   daquela branch e grava os resultados nela.
2. Acompanha a execução (`actions_list` / `get_job_logs`).
3. Lê os arquivos gerados em `data/` depois do commit automático.

Na sessão, o ambiente não precisa de variáveis do Mercado Livre nem de liberação de rede
para `api.mercadolibre.com`.

## 10. Recuperação rápida

| Situação | O que fazer |
|---|---|
| Conversa com o Claude apagada | Nada se perde: código, dados e este documento estão no repositório e os secrets no GitHub. Abra uma nova sessão com o prompt da seção 13 |
| Execução vermelha com `invalid_grant` | Refazer a autorização (seção 5) |
| Secret `MELI_REFRESH_TOKEN` apagado | Refazer a autorização (seção 5) |
| `GH_PAT_SECRETS` vencido ou apagado | Gerar novo PAT (seção 3), atualizar o secret e refazer a autorização (seção 5) |
| Secret Key renovada no DevCenter | Atualizar `MELI_CLIENT_SECRET` e rodar `teste`; se falhar, refazer a autorização |
| Aplicação apagada no DevCenter | Recriar (seção 2), atualizar `MELI_CLIENT_ID` e `MELI_CLIENT_SECRET`, trocar o Client ID no link e refazer a autorização |
| Workflow sumiu da aba Actions | Conferir se `.github/workflows/meli.yml` está na `main`. Se o agendamento foi desativado por inatividade (60 dias sem commits em repositório público), reativar em Actions > Mercado Livre > "Enable workflow" |
| Repositório perdido | Recriar o repositório, restaurar os arquivos das seções 7 e 11 e refazer as seções 3 a 5 |

## 11. Solução de problemas

| Sintoma no log | Causa | Ação |
|---|---|---|
| `Falha ao obter token: invalid_grant` (renovação) | Refresh token já usado, revogado ou expirado | Seção 5 |
| `Falha ao obter token: invalid_grant` (autorizar) | Code expirado/usado ou redirect URI diferente | Gerar code novo; conferir `MELI_REDIRECT_URI` |
| `Falha ao obter token: invalid_client` | Client ID ou Secret Key errados | Conferir secrets |
| `Secret ausente: ...` | Secret não cadastrado ou nome digitado diferente | Conferir nomes (seção 4) |
| `HTTP 403` ao gravar o secret | PAT sem "Secrets: Read and write", de outro repositório ou vencido | Seção 3 e depois seção 5 |
| `Informe o code para a acao autorizar` | Campo code vazio | Rodar de novo com o `TG-...` |
| Code ignorado / erro de refresh ao autorizar | Ação ficou em `teste` | Escolher `autorizar` no primeiro campo |
| `Falha HTTP 403 em /items/{id}` ou `/user-products/{id}` | Restrição da API para anúncios de terceiros | Esperado; os itens ficam só com link |
| `Falha HTTP 404 em /highlights/...` | Categoria sem ranking | Esperado |
| 429 | Limite de requisições | Os scripts esperam e tentam de novo (até 6 vezes) |

## 12. Segurança e regras de operação

- Credenciais somente em secrets do GitHub. Nunca imprimir, salvar em arquivo, commitar ou
  colar no chat.
- O workflow mostra só o código de erro do OAuth, mascara tokens e code no log e grava em
  `data/` apenas dados públicos da conta (sem e-mail, telefone ou documento).
- O repositório é **público**: os secrets continuam protegidos, mas tudo em `data/` e no
  código fica visível. Não grave dados pessoais de clientes (pedidos, endereços) em `data/`.
- Gravações no Mercado Livre (`publicar_anuncio` e `editar_anuncio`): sempre rodar antes
  `validar_anuncio` ou `previa_edicao`, mostrar a proposta à dona da conta e só gravar com
  confirmação explícita. O workflow exige `confirmar` = `PUBLICAR` ou `EDITAR`. O Claude
  nunca dispara uma gravação sem essa confirmação na conversa.
- Datas a acompanhar: vencimento do `GH_PAT_SECRETS` (anotado na criação) e execução
  semanal do agendamento.

## 13. Prompt para iniciar uma nova sessão

Copie e cole em uma nova sessão do Claude Code com o repositório
`solveonebr-design/AgenteIA` conectado:

```
Você vai operar a integração da minha conta do Mercado Livre no repositório
solveonebr-design/AgenteIA (branch main). Leia docs/Integracao_Mercado_Livre.md,
docs/Boas_Praticas_Anuncio_ML.md, o workflow .github/workflows/meli.yml e os
scripts scripts/meli_*.py.

Regras:
- A conexão roda SOMENTE pelo workflow "Mercado Livre" do GitHub Actions.
  O refresh token é de uso único: nunca renove o token fora do workflow e
  nunca peça, exiba ou salve credenciais.
- Para consultar dados, dispare o workflow (meli.yml) com a ação adequada,
  acompanhe a execução e leia os arquivos gerados em data/.
- Leitura é livre. Qualquer gravação no Mercado Livre: rode antes
  validar_anuncio (anúncio novo) ou previa_edicao (edição), me mostre o
  resultado e espere minha confirmação antes de rodar publicar_anuncio
  ou editar_anuncio.
- Anúncios: escreva o conteúdo seguindo docs/Boas_Praticas_Anuncio_ML.md
  (seção 12) e só me mostre a proposta com nota de qualidade de 85 ou mais.
- Faça commit e push dos scripts que criar (sem credenciais).

Tarefa: <descreva aqui>
```
