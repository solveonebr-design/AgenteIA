#!/usr/bin/env python3
"""Forma de gelo SV_0002: familia de variacoes por cor + conteudo otimizado.

Estrutura:
  SV_0002              pai (sem oferta), tema COLOR
  SV_0002_VERDE_FBA    filho Verde, no ASIN existente B0HJKGM3ZY (substitui o SKU 0002N_FBA)
  SV_0002_AZUL_FBA     filho Azul (novo ASIN)
  SV_0002_ROSA_FBA     filho Rosa (novo ASIN)
  SV_0002_AMARELO_FBA  filho Amarelo (novo ASIN)

Uso:
  python3 scripts/variacoes_sv0002.py preview   # so valida, nao grava
  python3 scripts/variacoes_sv0002.py aplicar   # grava na Amazon (nao exclui o SKU antigo)
"""
import copy
import sys

import listar_produtos as lp
import variacoes_sv0011 as v

PRODUCT_TYPE = "ICE_CUBE_TRAY"
SOURCE_SKU = "0002N_FBA"
SOURCE_ASIN = "B0HJKGM3ZY"
PARENT_SKU = "SV_0002"
COLORS = {"Verde": "SV_0002_VERDE_FBA", "Azul": "SV_0002_AZUL_FBA",
          "Rosa": "SV_0002_ROSA_FBA", "Amarelo": "SV_0002_AMARELO_FBA"}
PRICE = 22.99

GH = "https://raw.githubusercontent.com/solveonebr-design/AgenteIA/ca7586d6e211248b33264a2b38bda424ab303fe7/fotos/sv0002/"
AMZ = "https://m.media-amazon.com/images/I/"
ALL_COLORS = AMZ + "41xkBv7yqaL.jpg"      # as 4 cores lado a lado
STACKED = AMZ + "51orBiOrL%2BL.jpg"         # formas empilhadas, 4 cores
PRESS = AMZ + "51Mf5twUy0L.jpg"           # dedo pressionando o fundo (verde)
POP = AMZ + "51NC%2BSBFhcL.jpg"           # cubo saindo da forma (verde)
COLLAGE = AMZ + "61SgohDMfUL.jpg"         # colagem de uso (azul, laranja, frutas)
PHOTOS = {
    "Verde": [AMZ + "41sHyCmWwCL.jpg", GH + "verde_medidas.jpg", PRESS, POP, COLLAGE, ALL_COLORS, STACKED],
    "Azul": [AMZ + "515vMR2pRoL.jpg", GH + "azul_medidas.jpg", COLLAGE, PRESS, POP, ALL_COLORS, STACKED],
    "Rosa": [GH + "rosa_principal.jpg", AMZ + "51zOAim6RGL.jpg", PRESS, POP, COLLAGE, ALL_COLORS, STACKED],
    "Amarelo": [GH + "amarelo_principal.jpg", GH + "amarelo_medidas.jpg", PRESS, POP, COLLAGE, ALL_COLORS, STACKED],
}

TITLE = ("Forma de Gelo com Tampa e Fundo de Silicone Flexível, 14 Cubos, Bandeja Empilhável para Freezer, "
         "Drinks, Sucos e Refrigerantes, 25,4 x 9,8 cm")
BULLETS = [
    "14 CUBOS POR FORMA: cada cavidade produz um cubo de cerca de 3 x 4 x 2,9 cm, tamanho ideal para copos "
    "de água, sucos, refrigerantes, cafés gelados e drinks.",
    "FUNDO DE SILICONE FLEXÍVEL: basta pressionar a base de cada cavidade para soltar o cubo inteiro, sem "
    "torcer a forma e sem quebrar o gelo. Retire só a quantidade que precisar.",
    "TAMPA RÍGIDA: ajuda a proteger o gelo de impurezas e cheiros do freezer e permite empilhar outras "
    "formas por cima, deixando o freezer mais organizado.",
    "FORMATO COMPACTO: com 25,4 x 9,8 x 3 cm, a forma comprida e estreita aproveita bem o espaço do "
    "freezer e cabe em gavetas e prateleiras menores.",
    "VERSÁTIL E FÁCIL DE LIMPAR: além de gelo, serve para congelar sucos, chás, café e pedaços de frutas. "
    "Lave à mão com água morna e detergente neutro.",
]
DESCRIPTION = (
    "Forma de gelo com 14 cavidades, tampa rígida e fundo de silicone flexível, pensada para deixar o "
    "preparo do gelo mais prático no dia a dia.\n\n"
    "Para desenformar, basta pressionar o fundo de silicone de cada cavidade: o cubo sai inteiro, sem "
    "precisar torcer a forma. A tampa ajuda a proteger o gelo de impurezas e cheiros do freezer e permite "
    "empilhar outras formas por cima.\n\n"
    "Além de gelo para água, sucos, refrigerantes e drinks, também pode ser usada para congelar chás, café "
    "e pedaços de frutas.\n\n"
    "Medidas aproximadas:\n"
    "- Forma: 25,4 x 9,8 x 3 cm\n"
    "- Cada cubo: 3 x 4 x 2,9 cm\n\n"
    "Cuidados: lavar à mão com água morna e detergente neutro.\n\n"
    "Conteúdo da embalagem: 1 forma de gelo com tampa."
)
# Termos fora do titulo; a Amazon indexa ate ~249 bytes.
KEYWORDS = ("cubeira forminha molde gelinho cubinhos recipiente congelar porções caipirinha whisky água festa bar "
            "cozinha utensílio prática desenforma fácil")

OFFER_ATTRS = ("purchasable_offer", "list_price", "fulfillment_availability", "skip_offer", "condition_type",
               "merchant_shipping_group")


def texts(values, mkt):
    return [{"value": x, "language_tag": "pt_BR", "marketplace_id": mkt} for x in values]


def content(mkt, color=None):
    return {
        "item_name": texts([f"{TITLE} - {color}" if color else TITLE], mkt),
        "bullet_point": texts(BULLETS, mkt),
        "product_description": texts([DESCRIPTION], mkt),
        "generic_keyword": texts([KEYWORDS], mkt),
    }


def images(urls, mkt):
    return {k: [{"media_location": u, "marketplace_id": mkt}] for k, u in zip(v.IMAGE_ATTRS, urls)}


def check():
    assert len(TITLE) + len(" - Amarelo") <= 200, len(TITLE)
    assert len(BULLETS) == 5 and all(len(b) <= 700 for b in BULLETS)
    assert len(KEYWORDS.encode()) <= 249, len(KEYWORDS.encode())
    title_words = {w.strip(",").lower() for w in TITLE.split()}
    repeated = [w for w in KEYWORDS.lower().split() if w in title_words]
    assert not repeated, repeated


def build(source, mkt):
    base = {k: val for k, val in copy.deepcopy(source).items()
            if not k.startswith("main_product_image") and not k.startswith("other_product_image")}
    base.pop("merchant_suggested_asin", None)
    base["is_dishwasher_safe"] = [{"value": False, "marketplace_id": mkt}]  # instrucao: lavar a mao

    parent = {k: val for k, val in base.items() if k not in OFFER_ATTRS and k != "color"}
    parent.update(content(mkt))
    parent.update(images(PHOTOS["Verde"], mkt))
    parent["parentage_level"] = [{"value": "parent", "marketplace_id": mkt}]
    parent["variation_theme"] = [{"name": "COLOR"}]
    steps = [(PARENT_SKU, "LISTING_PRODUCT_ONLY", parent)]

    for color, sku in COLORS.items():
        a = copy.deepcopy(base)
        a.update(content(mkt, color))
        a.update(images(PHOTOS[color], mkt))
        a["color"] = [{"value": color, "standardized_values": [color], "language_tag": "pt_BR", "marketplace_id": mkt}]
        a["parentage_level"] = [{"value": "child", "marketplace_id": mkt}]
        a["child_parent_sku_relationship"] = [
            {"child_relationship_type": "variation", "parent_sku": PARENT_SKU, "marketplace_id": mkt}]
        a["variation_theme"] = [{"name": "COLOR"}]
        a["fulfillment_availability"] = [{"fulfillment_channel_code": "AMAZON_NA"}]
        a["list_price"] = [{"currency": "BRL", "value_with_tax": PRICE, "marketplace_id": mkt}]
        a["purchasable_offer"] = [{"currency": "BRL", "audience": "ALL", "marketplace_id": mkt,
                                   "our_price": [{"schedule": [{"value_with_tax": PRICE}]}]}]
        if color == "Verde":
            a["merchant_suggested_asin"] = [{"value": SOURCE_ASIN, "marketplace_id": mkt}]
        steps.append((sku, "LISTING", a))
    return steps


def update_photos(client, seller, mkt, preview):
    """Substitui a galeria de cada anuncio pela lista de PHOTOS (pai usa a do Verde)."""
    plan = {PARENT_SKU: PHOTOS["Verde"], **{sku: PHOTOS[color] for color, sku in COLORS.items()}}
    print("Fotos:", "PRE-VISUALIZACAO (nada e gravado)" if preview else "APLICAR")
    for sku, urls in plan.items():
        cur = client.get(f"/listings/2021-08-01/items/{seller}/{sku}",
                         {"marketplaceIds": mkt, "includedData": "attributes"})["attributes"]
        want = images(urls, mkt)
        ops = [{"op": "replace", "path": f"/attributes/{k}", "value": val} for k, val in want.items()]
        ops += [{"op": "delete", "path": f"/attributes/{k}", "value": cur[k]}
                for k in v.IMAGE_ATTRS if k in cur and k not in want]
        resp = v.request(client, "PATCH", sku, {"productType": PRODUCT_TYPE, "patches": ops}, preview=preview)
        print(f"PATCH {sku}: {resp.get('status')} ({len(urls)} fotos)",
              [i.get("message") for i in resp.get("issues", [])])


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "preview"
    if mode not in ("preview", "aplicar", "fotos-preview", "fotos"):
        sys.exit("Modo deve ser 'preview', 'aplicar', 'fotos-preview' ou 'fotos'")
    check()
    client = lp.Client()
    client.endpoint = lp.ENDPOINTS[0]
    mkt = lp.env("SPAPI_MARKETPLACE_ID")
    seller = lp.env("SPAPI_SELLER_ID")
    if mode.startswith("fotos"):
        return update_photos(client, seller, mkt, preview=mode == "fotos-preview")
    source = client.get(f"/listings/2021-08-01/items/{seller}/{SOURCE_SKU}",
                        {"marketplaceIds": mkt, "includedData": "attributes"})["attributes"]
    print("Modo:", "PRE-VISUALIZACAO (nada e gravado)" if mode == "preview" else "APLICAR")
    for sku, req, attrs in build(source, mkt):
        resp = v.request(client, "PUT", sku, {"productType": PRODUCT_TYPE, "requirements": req, "attributes": attrs},
                         preview=mode == "preview")
        print(f"\nPUT {sku}: {resp.get('status')}")
        for issue in resp.get("issues", []):
            print(f"  [{issue.get('severity', '')}] {issue.get('code', '')} {issue.get('message', '')}"
                  f" {issue.get('attributeNames', '')}")


if __name__ == "__main__":
    main()
