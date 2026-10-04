#!/usr/bin/env python3
"""Bolsa termica lancheira SV_0004: familia de variacoes por cor + conteudo otimizado.

Estrutura:
  SV_0004              pai (sem oferta), tema COLOR
  SV_0004_PRETO_FBA    filho Preto, no ASIN existente B0HJJJLPPQ (substitui o SKU 0004_FBA)
  SV_0004_CINZA2_FBA, SV_0004_AZUL2_FBA  filhos novos (SV_0004_CINZA_FBA e SV_0004_AZUL_FBA ficaram
                       presos ao ASIN do preto na Amazon e nao podem ser reutilizados)

Uso:
  python3 scripts/variacoes_sv0004.py preview        # valida tudo, nao grava
  python3 scripts/variacoes_sv0004.py aplicar        # grava (nao exclui o SKU antigo)
  python3 scripts/variacoes_sv0004.py fotos-preview  # valida so as galerias
  python3 scripts/variacoes_sv0004.py fotos          # atualiza so as galerias
"""
import copy
import sys

import listar_produtos as lp
import variacoes_sv0011 as v

PRODUCT_TYPE = "MEAL_HOLDER"
SOURCE_SKU = "0004_FBA"
SOURCE_ASIN = "B0HJJJLPPQ"
PARENT_SKU = "SV_0004"
COLORS = {"Preto": "SV_0004_PRETO_FBA", "Cinza": "SV_0004_CINZA2_FBA", "Azul": "SV_0004_AZUL2_FBA"}
EXISTING_ASIN_COLOR = "Preto"
PRICE = 32.99

GH = "https://raw.githubusercontent.com/solveonebr-design/AgenteIA/35b2fc84be0169b347ab6527b93d723afb274dea/fotos/sv0004/"
AMZ = "https://m.media-amazon.com/images/I/"
TRIO = AMZ + "51yLmPzdMzL.jpg"           # as 3 cores lado a lado
DIM_GRAY = AMZ + "517Lp-dWfHL.jpg"       # medidas (cinza)
DIM_BLACK = AMZ + "61t3GnpQHiL.jpg"      # medidas (preta) + uso
OPEN_BOXES = AMZ + "61UX6udOWHL.jpg"     # aberta com 2 potes
OPEN_INSIDE = AMZ + "61q7c0PWjjL.jpg"    # interior termico
SCENE = AMZ + "51GY7x7VuNL.jpg"          # preta e cinza na cozinha
GRAY_HAND = AMZ + "613xCOK8BXL.jpg"      # cinza na mao
BLUE_SCENE = AMZ + "71FOMak7wqL.jpg"     # azul no ambiente
PHOTOS = {
    "Preto": [AMZ + "71v0LkBl48L.jpg", DIM_BLACK, OPEN_BOXES, OPEN_INSIDE, SCENE, TRIO],
    "Cinza": [GH + "cinza_principal.jpg", DIM_GRAY, GRAY_HAND, OPEN_BOXES, OPEN_INSIDE, SCENE, TRIO],
    "Azul": [GH + "azul_principal.jpg", BLUE_SCENE, OPEN_BOXES, OPEN_INSIDE, DIM_BLACK, TRIO],
}

TITLE = ("Bolsa Térmica Lancheira 6,7 Litros com Alça de Ombro Ajustável e Zíper Duplo, para Marmita, Trabalho, "
         "Escola e Passeios, Isolamento Térmico, 22 x 16 x 19 cm")
BULLETS = [
    "ISOLAMENTO TÉRMICO: forro interno aluminizado que ajuda a manter a temperatura de refeições, lanches e "
    "bebidas durante o deslocamento.",
    "ESPAÇO PARA 2 MARMITAS: capacidade de 6,7 litros e medidas de 22 x 16 x 19 cm, com espaço para potes "
    "empilhados, frutas, talheres e uma garrafinha.",
    "DUAS FORMAS DE CARREGAR: alça superior de mão e alça transversal ajustável com mosquetões, para levar na "
    "mão ou no ombro com mais conforto.",
    "ABERTURA AMPLA COM ZÍPER DUPLO: a tampa com zíper de dois cursores abre por completo e facilita colocar e "
    "retirar os potes.",
    "LEVE E FÁCIL DE LIMPAR: tecido em poliéster com apenas 168 g. Limpe com pano macio e úmido. Ideal para "
    "trabalho, escola, faculdade, academia, passeios e viagens.",
]
DESCRIPTION = (
    "Bolsa térmica lancheira com forro aluminizado, pensada para levar refeições, lanches e bebidas no dia a "
    "dia com praticidade.\n\n"
    "Com 6,7 litros de capacidade, acomoda até 2 marmitas empilhadas, além de frutas, talheres e uma "
    "garrafinha. A tampa com zíper duplo abre por completo, o que facilita organizar os potes.\n\n"
    "Pode ser carregada pela alça superior ou pela alça transversal ajustável, presa por mosquetões. O tecido "
    "em poliéster é leve e fácil de limpar.\n\n"
    "Especificações:\n"
    "- Medidas: 22 x 16 x 19 cm\n"
    "- Capacidade: 6,7 litros\n"
    "- Material: poliéster com forro térmico aluminizado\n"
    "- Peso: 168 g\n\n"
    "Cuidados: limpar com pano macio e úmido. Não lavar em máquina, não usar alvejantes, não passar a ferro e "
    "secar à sombra.\n\n"
    "Conteúdo da embalagem: 1 bolsa térmica com alça de ombro."
)
# Termos fora do titulo; a Amazon indexa ate ~249 bytes.
KEYWORDS = ("marmiteira lancheirinha almoço comida fitness academia faculdade escritório piquenique "
            "viagem feminina masculina adulto cooler porta")
SPECIAL_FEATURES = ["Isolado termicamente", "Alça de ombro ajustável", "Zíper duplo", "Leve"]

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
        "special_feature": texts(SPECIAL_FEATURES, mkt),
    }


def images(urls, mkt):
    return {k: [{"media_location": u, "marketplace_id": mkt}] for k, u in zip(v.IMAGE_ATTRS, urls)}


def check():
    assert len(TITLE) + len(" - Preto") <= 200, len(TITLE)
    assert len(BULLETS) == 5 and all(len(b) <= 700 for b in BULLETS)
    assert len(KEYWORDS.encode()) <= 249, len(KEYWORDS.encode())
    title_words = {w.strip(",").lower() for w in TITLE.split()}
    repeated = [w for w in KEYWORDS.lower().split() if w in title_words]
    assert not repeated, repeated
    for color, urls in PHOTOS.items():
        assert len(urls) == len(set(urls)) <= 9, color


def build(source, mkt):
    base = {k: val for k, val in copy.deepcopy(source).items()
            if not k.startswith("main_product_image") and not k.startswith("other_product_image")}
    base.pop("merchant_suggested_asin", None)

    parent = {k: val for k, val in base.items() if k not in OFFER_ATTRS and k != "color"}
    parent.update(content(mkt))
    parent.update(images(PHOTOS[EXISTING_ASIN_COLOR], mkt))
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
        if color == EXISTING_ASIN_COLOR:
            a["merchant_suggested_asin"] = [{"value": SOURCE_ASIN, "marketplace_id": mkt}]
        else:
            # numero de peca/modelo proprio por cor: com o mesmo "0004" a Amazon casou as cores no ASIN do preto
            ref = f"0004-{color.upper()}"
            a["part_number"] = [{"value": ref, "marketplace_id": mkt}]
            a["model_number"] = [{"value": ref, "marketplace_id": mkt}]
        steps.append((sku, "LISTING", a))
    return steps


def update_photos(client, seller, mkt, preview):
    """Substitui a galeria de cada anuncio pela lista de PHOTOS."""
    plan = {PARENT_SKU: PHOTOS[EXISTING_ASIN_COLOR], **{sku: PHOTOS[color] for color, sku in COLORS.items()}}
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
