#!/usr/bin/env python3
"""Gera docs/Integracao_Amazon_SP-API.pdf (requer: pip install reportlab)."""
import os
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (PageBreak, Paragraph, Preformatted, SimpleDocTemplate, Spacer,
                                Table, TableStyle)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont("Sans", f"{FONT_DIR}/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("Sans-Bold", f"{FONT_DIR}/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Mono", f"{FONT_DIR}/DejaVuSansMono.ttf"))
pdfmetrics.registerFontFamily("Sans", normal="Sans", bold="Sans-Bold", italic="Sans", boldItalic="Sans-Bold")

ACCENT = colors.HexColor("#1F4E79")
LIGHT = colors.HexColor("#EAF1F8")
CODE_BG = colors.HexColor("#F4F4F4")
WARN_BG = colors.HexColor("#FFF4E5")

base = getSampleStyleSheet()
S = {
    "title": ParagraphStyle("title", fontName="Sans-Bold", fontSize=22, leading=28, textColor=ACCENT,
                            alignment=TA_CENTER, spaceAfter=8),
    "subtitle": ParagraphStyle("subtitle", fontName="Sans", fontSize=11, leading=15, alignment=TA_CENTER,
                               textColor=colors.HexColor("#555555")),
    "h1": ParagraphStyle("h1", fontName="Sans-Bold", fontSize=15, leading=19, textColor=ACCENT,
                         spaceBefore=14, spaceAfter=6),
    "h2": ParagraphStyle("h2", fontName="Sans-Bold", fontSize=11.5, leading=15, textColor=ACCENT,
                         spaceBefore=9, spaceAfter=4),
    "body": ParagraphStyle("body", fontName="Sans", fontSize=9.5, leading=13.5, spaceAfter=5),
    "bullet": ParagraphStyle("bullet", fontName="Sans", fontSize=9.5, leading=13.5, leftIndent=14,
                             bulletIndent=4, spaceAfter=2),
    "cell": ParagraphStyle("cell", fontName="Sans", fontSize=8.3, leading=11),
    "cellb": ParagraphStyle("cellb", fontName="Sans-Bold", fontSize=8.3, leading=11, textColor=colors.white),
    "code": ParagraphStyle("code", fontName="Mono", fontSize=7.8, leading=10.2),
    "note": ParagraphStyle("note", fontName="Sans", fontSize=9, leading=12.5),
}

story = []


def md(text):
    """Escapa o texto e converte **negrito** e `codigo`."""
    out, bold, code = [], False, False
    for i, part in enumerate(text.replace("`", "\x00").split("**")):
        if i:
            bold = not bold
            out.append("<b>" if bold else "</b>")
        pieces = part.split("\x00")
        for j, p in enumerate(pieces):
            if j:
                code = not code
                out.append('<font name="Mono" size="8.5">' if code else "</font>")
            out.append(escape(p))
    return "".join(out)


def h1(t): story.append(Paragraph(escape(t), S["h1"]))
def h2(t): story.append(Paragraph(escape(t), S["h2"]))
def p(t): story.append(Paragraph(md(t), S["body"]))


def bullets(items):
    for it in items:
        num, _, rest = it.partition(". ")
        if num.isdigit():
            story.append(Paragraph(md(rest), S["bullet"], bulletText=f"{num}."))
        else:
            story.append(Paragraph(md(it), S["bullet"], bulletText="•"))
    story.append(Spacer(1, 3))


def code(text):
    t = Table([[Preformatted(text.strip("\n"), S["code"])]], colWidths=[17 * cm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
                           ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
                           ("LEFTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 5),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    story.append(t)
    story.append(Spacer(1, 6))


def note(text, bg=WARN_BG):
    t = Table([[Paragraph(md(text), S["note"])]], colWidths=[17 * cm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), bg),
                           ("LINEBEFORE", (0, 0), (0, -1), 3, colors.HexColor("#E08A00") if bg == WARN_BG else ACCENT),
                           ("LEFTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story.append(t)
    story.append(Spacer(1, 6))


def table(header, rows, widths):
    data = [[Paragraph(escape(h), S["cellb"]) for h in header]]
    data += [[Paragraph(md(str(c)), S["cell"]) for c in r] for r in rows]
    t = Table(data, colWidths=[w * cm for w in widths], repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), ACCENT),
                           ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
                           ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#BBBBBB")),
                           ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4)]))
    story.append(t)
    story.append(Spacer(1, 8))


# ---------------------------------------------------------------- capa
story += [Spacer(1, 5 * cm),
          Paragraph("Integração Amazon SP-API", S["title"]),
          Paragraph("Documentação técnica para recriar a integração em uma nova sessão do Claude Code", S["subtitle"]),
          Spacer(1, 1.2 * cm),
          Paragraph("Conta: SOLVEONEBR · Marketplace: Amazon.com.br", S["subtitle"]),
          Paragraph("Repositório: github.com/solveonebr-design/AgenteIA · branch claude/amazon-env-variables-skaova",
                    S["subtitle"]),
          Paragraph("Versão de 03/10/2026", S["subtitle"]),
          Spacer(1, 2 * cm)]
note("**Este documento não contém credenciais.** A sessão se conecta à Amazon exclusivamente pelas variáveis de "
     "ambiente cadastradas no ambiente de nuvem do Claude Code. Nunca cole client secret ou refresh token no chat, "
     "em arquivos do repositório ou em logs.", LIGHT)
story.append(PageBreak())

# ---------------------------------------------------------------- 1
h1("1. Visão geral")
p("A integração usa a **Selling Partner API (SP-API)** da Amazon, em produção, com um app privado "
  "(autorização própria). Uma sessão do Claude Code na nuvem executa scripts Python que leem as credenciais "
  "das variáveis de ambiente, trocam o refresh token por um access token no Login with Amazon (LWA) e chamam "
  "a SP-API no endpoint da América do Norte.")
code("""
 Ambiente de nuvem do Claude Code
   variáveis SPAPI_*  (cadastradas em Editar ambiente)
          |
          v
 scripts Python (repositório AgenteIA)
          |  POST client_id + client_secret + refresh_token
          v
 https://api.amazon.com/auth/o2/token  --> access_token (válido ~1 h)
          |  header x-amz-access-token
          v
 https://sellingpartnerapi-na.amazon.com  (Listings, Definitions, FBA Inventory, Reports)
""")
p("Não há assinatura AWS SigV4: apenas o access token do LWA é necessário. As variáveis "
  "`AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` que existem no ambiente **não** são usadas pela integração.")

h2("Dados da conta (não sigilosos)")
table(["Item", "Valor"], [
    ["Loja", "SOLVEONEBR"],
    ["Seller ID", "`A2JG52T2T5UGKK`"],
    ["Marketplace", "Brasil, `A2Q3Y263D00KWC` (Amazon.com.br, BRL, pt_BR)"],
    ["Região / endpoint", "NA, `https://sellingpartnerapi-na.amazon.com` (confirmado)"],
    ["Tipo de app", "Produção, autorização própria (private)"],
], [4, 13])

# ---------------------------------------------------------------- 2
h1("2. Configuração do ambiente no Claude Code")
p("Abra o menu do ambiente na barra de título da sessão e clique em **Editar**. Toda a configuração abaixo "
  "fica no **mesmo** ambiente; cada sessão usa um único ambiente.")
h2("2.1 Variáveis de ambiente (campo \"Variáveis de ambiente\")")
p("Uma por linha, no formato `NOME=valor`. Use o campo de variáveis de ambiente, **não** \"Credenciais de "
  "API\": as credenciais de API ficam ocultas da sessão, e o pedido de token do LWA precisa enviar o client "
  "secret e o refresh token no corpo da requisição.")
table(["Variável", "Conteúdo", "Onde obter"], [
    ["`SPAPI_CLIENT_ID`", "Client ID do app LWA (começa com amzn1.application-oa2-client.)",
     "Seller Central > Apps e serviços > Desenvolver apps > credenciais LWA"],
    ["`SPAPI_CLIENT_SECRET`", "Client secret do app LWA (amzn1.oa2-cs.v1.)", "Mesmo local do client ID"],
    ["`SPAPI_REFRESH_TOKEN`", "Refresh token da autorização própria (Atzr|...)",
     "Desenvolver apps > Autorizar app (gera um novo token a cada autorização)"],
    ["`SPAPI_SELLER_ID`", "`A2JG52T2T5UGKK`", "Seller Central > Configurações > Informações da conta"],
    ["`SPAPI_MARKETPLACE_ID`", "`A2Q3Y263D00KWC`", "Fixo para o Brasil"],
    ["`SPAPI_ENDPOINT` (opcional)", "`https://sellingpartnerapi-na.amazon.com`",
     "Se ausente, o script testa NA, EU e FE"],
], [4.2, 6.3, 6.5])
note("**Atenção aos nomes.** Os scripts leem exatamente os nomes acima. Um nome digitado diferente (ex.: "
     "`SP_API_CLIENT_ID`, com um sublinhado a mais, erro que já ocorreu e foi corrigido) resulta em "
     "\"Variavel de ambiente ausente\". Confira com o comando da seção 3.")
h2("2.2 Acesso à rede")
p("O nível \"Confiável\" **bloqueia** a Amazon (o proxy responde 403 ao CONNECT). Use \"Completo\" ou "
  "\"Personalizado\" mantendo a lista padrão de gerenciadores de pacotes e adicionando:")
bullets(["`api.amazon.com` (token LWA)", "`sellingpartnerapi-na.amazon.com`, `sellingpartnerapi-eu.amazon.com`, "
         "`sellingpartnerapi-fe.amazon.com`", "`*.amazonaws.com` (download de relatórios e esquemas de "
         "categoria)", "`raw.githubusercontent.com` (verificação das fotos hospedadas no GitHub)"])
h2("2.3 Repositório e sessão nova")
bullets(["Conecte o repositório `solveonebr-design/AgenteIA` à sessão e use a branch "
         "`claude/amazon-env-variables-skaova` (todo o código está nela).",
         "Alterações em variáveis ou rede só valem para **sessões novas**: salve o ambiente e abra outra sessão.",
         "Dependências: Python 3 (biblioteca padrão) para os scripts; `pillow` só para tratar fotos "
         "(`pip install pillow`); `reportlab` só para regenerar este PDF."])

# ---------------------------------------------------------------- 3
h1("3. Verificação inicial (primeiros comandos de uma nova sessão)")
p("Confere se as variáveis existem **sem exibir os valores**:")
code("""
for v in SPAPI_CLIENT_ID SPAPI_CLIENT_SECRET SPAPI_REFRESH_TOKEN \\
         SPAPI_SELLER_ID SPAPI_MARKETPLACE_ID; do
  [ -n "${!v}" ] && echo "$v: ok" || echo "$v: AUSENTE"
done
env | cut -d= -f1 | grep -iE 'spapi|sp_api'      # só nomes, para achar erros de digitação
""")
p("Confere a rede (qualquer código HTTP, mesmo 403, significa que o host é alcançável; `000` com erro 56 "
  "significa bloqueio do proxy):")
code("""
curl -sS -o /dev/null -w "%{http_code}\\n" https://api.amazon.com/
curl -sS "$HTTPS_PROXY/__agentproxy/status" | grep -A3 recentRelayFailures
""")
p("Teste completo (somente leitura): gera a lista de anúncios em `data/`.")
code("""
cd scripts
python3 listar_produtos.py ../data
""")

# ---------------------------------------------------------------- 4
h1("4. Estrutura do repositório")
table(["Caminho", "Função"], [
    ["`scripts/listar_produtos.py`", "Base da integração: cliente LWA com renovação do token, função `http` com "
     "nova tentativa em 429, busca paginada de anúncios, detecção de região, plano alternativo pela Reports API "
     "(> 1.000 anúncios). Gera `produtos_publicados.csv` e `.json`."],
    ["`scripts/variacoes_sv0011.py`", "Cria a família de variações por cor do SV_0011 (pai + filhos). Modos "
     "`preview` e `aplicar`; recebe um JSON de fotos por cor. Função `request()` reutilizável para PUT/PATCH."],
    ["`scripts/conteudo_sv0011.py`", "Título, bullets, descrição, palavras-chave e características otimizados "
     "da família SV_0011, com checagem de limites. Modos `preview` e `aplicar`."],
    ["`data/`", "Saídas: `marketplace_participations.json` (teste via GitHub Actions) e "
     "`produtos_publicados.csv/.json` (retrato de 03/10/2026, já com a família SV_0011)."],
    ["`fotos/`", "Fotos em JPG usadas nos anúncios e `sv0011_fotos.json` (URLs por cor)."],
    ["`.github/workflows/main.yml`", "Teste de conexão alternativo no GitHub Actions usando *secrets* do "
     "repositório (independe do ambiente do Claude Code)."],
    ["`docs/`", "Este documento e o gerador `gerar_documentacao.py`."],
], [4.6, 12.4])

# ---------------------------------------------------------------- 5
h1("5. Autenticação (LWA)")
code("""
POST https://api.amazon.com/auth/o2/token
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token&refresh_token=$SPAPI_REFRESH_TOKEN
&client_id=$SPAPI_CLIENT_ID&client_secret=$SPAPI_CLIENT_SECRET
""")
bullets(["A resposta traz `access_token` (validade ~1 h). O `Client` em `listar_produtos.py` o renova após 50 min.",
         "Todas as chamadas seguintes levam o cabeçalho `x-amz-access-token: <access_token>`.",
         "Erros `invalid_grant`/`invalid_client`: refresh token incompleto/revogado ou client ID/secret trocados. "
         "O script mostra só o código do erro, nunca as credenciais."])

# ---------------------------------------------------------------- 6
h1("6. APIs utilizadas")
table(["Operação", "Método e caminho", "Uso"], [
    ["Participações", "GET /sellers/v1/marketplaceParticipations", "Teste de conexão (workflow do GitHub)"],
    ["searchListingsItems", "GET /listings/2021-08-01/items/{sellerId}?marketplaceIds&includedData="
     "summaries,offers&pageSize=20&pageToken", "Listar anúncios. Máx. 1.000 resultados; pageToken expira em 24 h"],
    ["getListingsItem", "GET /listings/2021-08-01/items/{sellerId}/{sku}?includedData=summaries,attributes,"
     "issues,offers,relationships", "Ler atributos completos de um SKU"],
    ["putListingsItem", "PUT /listings/2021-08-01/items/{sellerId}/{sku}", "Criar anúncio (pai, filho ou "
     "SKU novo em ASIN existente via `merchant_suggested_asin`)"],
    ["patchListingsItem", "PATCH /listings/2021-08-01/items/{sellerId}/{sku}", "Alterar atributos específicos"],
    ["deleteListingsItem", "DELETE /listings/2021-08-01/items/{sellerId}/{sku}", "Excluir SKU (irreversível)"],
    ["Pré-visualização", "`mode=VALIDATION_PREVIEW` em PUT/PATCH", "Valida sem gravar. Usar SEMPRE antes de aplicar"],
    ["Definição de categoria", "GET /definitions/2020-09-01/productTypes/{tipo}?requirements=LISTING&locale=pt_BR",
     "Limites, campos obrigatórios e temas de variação (o JSON Schema vem de um link em `schema.link.resource`)"],
    ["Estoque FBA", "GET /fba/inventory/v1/summaries?granularityType=Marketplace&details=true&sellerSkus=",
     "Conferir estoque antes de excluir/trocar SKU"],
    ["Relatórios", "POST/GET /reports/2021-06-30/reports, GET /documents/{id}", "Plano B para > 1.000 "
     "anúncios (GET_MERCHANT_LISTINGS_ALL_DATA)"],
], [3.3, 7.2, 6.5])
p("Roles do app necessárias: **Product Listing** (leitura e escrita de anúncios), **Inventory and Order "
  "Tracking** (estoque) e acesso a relatórios. Se uma chamada retornar 403 \"Access to requested resource is "
  "denied\" com token válido, falta a role: adicione-a no app e gere um novo refresh token.")

# ---------------------------------------------------------------- 7
h1("7. Procedimentos")
h2("7.1 Listar produtos publicados")
code("cd scripts && python3 listar_produtos.py ../data")
p("Saída: total, quantos `BUYABLE` (à venda) e quantos só `DISCOVERABLE` (no catálogo, sem compra — "
  "normalmente falta de estoque FBA).")
h2("7.2 Fluxo seguro para qualquer alteração")
bullets(["1. Ler o estado atual do SKU (getListingsItem com `attributes`) e salvar uma cópia em arquivo temporário.",
         "2. Consultar a definição da categoria para limites e campos obrigatórios.",
         "3. Montar o corpo e rodar com `mode=VALIDATION_PREVIEW` até todos retornarem `VALID`.",
         "4. Mostrar a proposta ao dono da conta e obter confirmação explícita.",
         "5. Aplicar. A resposta `ACCEPTED` é assíncrona: consultar o SKU a cada 30 s até ter ASIN e `issues` vazio.",
         "6. Fazer commit do script/configuração usada (sem credenciais) e push na branch."])
h2("7.3 Criar variações por cor")
code("""
python3 variacoes_sv0011.py preview ../fotos/sv0011_fotos.json
python3 variacoes_sv0011.py aplicar ../fotos/sv0011_fotos.json
""")
bullets(["Pai: PUT com `requirements=LISTING_PRODUCT_ONLY`, `parentage_level=parent`, `variation_theme=COLOR`, "
         "sem atributos de oferta (preço, fulfillment, condição) e sem cor.",
         "Filhos: `parentage_level=child`, `child_parent_sku_relationship` {variation, parent_sku}, "
         "`variation_theme=COLOR`, `color` com uma única cor e título terminando em \"- Cor\".",
         "O título do pai não leva cor; só os filhos."])
h2("7.4 Trocar o SKU de um anúncio existente")
p("A Amazon **não permite renomear SKU**. Procedimento usado (SV_0011_FBA para SV_0011_VERMELHO_FBA):")
bullets(["1. Verificar estoque FBA do SKU antigo (precisa ser zero e sem envio a caminho).",
         "2. PUT do SKU novo copiando os atributos do antigo + `merchant_suggested_asin` com o mesmo ASIN.",
         "3. Aguardar o SKU novo aparecer ligado ao ASIN (levou ~4 min).",
         "4. Só então DELETE do SKU antigo (com confirmação do dono)."])
h2("7.5 Atualizar conteúdo do anúncio")
code("python3 conteudo_sv0011.py preview    # depois: aplicar")
bullets(["Título até 200 caracteres, sem palavra repetida mais de 2 vezes, sem termos promocionais.",
         "5 bullets sem emojis, cada um iniciando com o benefício em maiúsculas.",
         "Palavras-chave ocultas: até ~249 bytes indexados, sem repetir palavras do título, sem marcas.",
         "Só incluir afirmações confirmadas pelo dono (ex.: livre de BPA, lava-louças, água fervente)."])
h2("7.6 Fotos")
bullets(["A API só aceita **URL pública** (`main_product_image_locator`, `other_product_image_locator_1..8`).",
         "Formatos aceitos: JPG, PNG, TIFF, GIF. **WebP não**. Atenção: alguns sites (ex.: utimix.com) entregam "
         "WebP mesmo com extensão .png.",
         "Mínimo 500 px no maior lado; 1000 px ou mais ativa o zoom. Foto principal com fundo branco puro.",
         "Fluxo usado: converter com Pillow, salvar em `fotos/`, commit, usar a URL "
         "`https://raw.githubusercontent.com/solveonebr-design/AgenteIA/<commit>/fotos/<arquivo>.jpg` "
         "(fixar o hash do commit). Exige repositório **público**; após a Amazon importar, pode voltar a privado."])

# ---------------------------------------------------------------- 8
h1("8. Estado da conta em 03/10/2026")
p("18 anúncios no Brasil; apenas `0001_FBA` (Limpador de Ouvidos, R$ 14,90) estava `BUYABLE`. Os demais "
  "estavam só `DISCOVERABLE`, sem estoque FBA. Família criada nesta sessão:")
table(["SKU", "ASIN", "Papel", "Cor", "Preço"], [
    ["`SV_0011`", "B0HLW62M4F", "Pai (tema COLOR)", "—", "—"],
    ["`SV_0011_VERMELHO_FBA`", "B0HJT25LB3", "Filho (ASIN original)", "Vermelho", "R$ 25,99"],
    ["`SV_0011_VERDE_FBA`", "B0HLWD82J6", "Filho (novo)", "Verde", "R$ 25,99"],
], [4.6, 2.8, 4, 2.4, 3.2])
bullets(["`SV_0011_FBA` foi excluído (substituído por `SV_0011_VERMELHO_FBA`).",
         "Categoria `DRYING_RACK`, marca \"Genérico\", isenção de código de barras (sem EAN), canal `AMAZON_NA` (FBA).",
         "Conteúdo otimizado aplicado aos 3 SKUs. Pendências: estoque FBA das duas cores, fotos maiores (verde "
         "só tem uma foto, ampliada de 323 para 600 px)."])
note("**Pegadinha do PATCH em preview:** ao validar um PATCH no SKU vermelho, a Amazon acusou "
     "`external_testing_certification` e `power_source_type` como obrigatórios, embora já preenchidos "
     "(\"Não aplicável\"). Solução: reenviar esses dois atributos no próprio PATCH.")

# ---------------------------------------------------------------- 9
h1("9. Solução de problemas")
table(["Sintoma", "Causa", "Ação"], [
    ["`Variavel de ambiente ausente: X`", "Variável não cadastrada, nome errado ou sessão antiga",
     "Conferir nomes (seção 3), corrigir no ambiente e abrir sessão nova"],
    ["`Tunnel connection failed: 403` / curl erro 56", "Rede do ambiente bloqueia o host", "Ajustar Acesso à rede (2.2)"],
    ["`invalid_grant` / `invalid_client`", "Refresh token revogado/incompleto, client ID ou secret errados",
     "Reautorizar o app no Seller Central e atualizar as variáveis"],
    ["403 \"token revoked, malformed or invalid\"", "Região errada ou credencial de sandbox", "Testar NA, EU, FE"],
    ["403 \"Access ... denied\" com token válido", "App sem a role necessária", "Adicionar role e gerar novo refresh token"],
    ["429", "Limite de requisições", "O script espera e tenta de novo (até 6 vezes)"],
    ["400 com pageToken", "Token de página expirado ou parâmetros alterados", "Recomeçar a paginação"],
    ["PUT/PATCH `INVALID`", "Campo obrigatório/limite da categoria", "Ler `issues[].attributeNames` e a definição da categoria"],
    ["`ACCEPTED` mas sem mudança", "Processamento assíncrono", "Consultar o SKU por alguns minutos"],
    ["Foto não aparece", "WebP, < 500 px, URL privada ou fora do ar", "Ver 7.6"],
], [4.6, 5.6, 6.8])

# ---------------------------------------------------------------- 10
h1("10. Segurança e regras de operação")
bullets(["Credenciais **somente** em variáveis de ambiente. Nunca imprimir, registrar, salvar em arquivo, "
         "commitar ou enviar a terceiros. Para checar, mostre apenas se existem (ok/ausente).",
         "Antes de tornar o repositório público, procure credenciais no histórico: "
         "`git log --all -p | grep -cE 'Atzr\\||amzn1\\.oa2-cs|amzn1\\.application-oa2-client'` (deve dar 0).",
         "Padrão é **somente leitura**. Gravações (PUT/PATCH/DELETE) só com pedido explícito do dono, "
         "pré-visualização `VALID` e confirmação. DELETE é irreversível: confirmar estoque zero antes.",
         "Nunca usar Feeds para alterar preço/estoque em massa sem autorização específica.",
         "Ao trocar credenciais (rotação), basta atualizar as variáveis no ambiente e abrir nova sessão; "
         "nenhum arquivo do repositório muda."])

# ---------------------------------------------------------------- 11
h1("11. Prompt para iniciar uma nova sessão")
p("Copie e cole na nova sessão (com o ambiente configurado conforme a seção 2):")
code("""
Você vai operar a integração da minha conta Amazon (SP-API) no repositório
solveonebr-design/AgenteIA, branch claude/amazon-env-variables-skaova.
Leia docs/Integracao_Amazon_SP-API.pdf e os scripts em scripts/.

Regras:
- Conecte-se SOMENTE pelas variáveis de ambiente SPAPI_* do ambiente do
  Claude Code. Nunca exiba nem salve credenciais.
- Primeiro verifique se as variáveis existem (sem mostrar valores) e se
  api.amazon.com está acessível; depois rode scripts/listar_produtos.py.
- Leitura é livre. Qualquer gravação na Amazon: rode antes em
  VALIDATION_PREVIEW, me mostre o resultado e espere minha confirmação.
- Faça commit e push dos scripts/configurações que criar (sem credenciais).

Tarefa: <descreva aqui>
""")


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Sans", 7.5)
    canvas.setFillColor(colors.HexColor("#777777"))
    canvas.drawString(2 * cm, 1.2 * cm, "Integração Amazon SP-API · AgenteIA")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Página {doc.page}")
    canvas.restoreState()


out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Integracao_Amazon_SP-API.pdf")
doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm,
                        bottomMargin=2 * cm, title="Integração Amazon SP-API", author="AgenteIA",
                        subject="Documentação técnica para recriar a integração SP-API")
doc.build(story, onFirstPage=lambda c, d: None, onLaterPages=footer)
print(out)
