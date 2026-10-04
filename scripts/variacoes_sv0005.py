#!/usr/bin/env python3
"""Pochete esportiva SV_0005: familia de variacoes por cor + conteudo otimizado.

Estrutura:
  SV_0005              pai (sem oferta), tema COLOR
  SV_0005_LARANJA_FBA  filho Laranja, no ASIN existente B0HJJQK5Y9 (substitui o SKU 0005_FBA)
  SV_0005_VERDE_FBA, SV_0005_ROSA_FBA, SV_0005_PRETO_FBA, SV_0005_AZUL_FBA  filhos novos

Uso:
  python3 scripts/variacoes_sv0005.py preview        # valida tudo, nao grava
  python3 scripts/variacoes_sv0005.py aplicar        # grava (nao exclui o SKU antigo)
  python3 scripts/variacoes_sv0005.py fotos-preview  # valida so as galerias
  python3 scripts/variacoes_sv0005.py fotos          # atualiza so as galerias
"""
import copy
import sys

import listar_produtos as lp
import variacoes_sv0011 as v

PRODUCT_TYPE = "WAIST_PACK"
SOURCE_SKU = "0005_FBA"
SOURCE_ASIN = "B0HJJQK5Y9"
PARENT_SKU = "SV_0005"
COLORS = {"Laranja": "SV_0005_LARANJA_FBA", "Verde": "SV_0005_VERDE_FBA", "Rosa": "SV_0005_ROSA_FBA",
          "Preto": "SV_0005_PRETO_FBA", "Azul": "SV_0005_AZUL_FBA"}
EXISTING_ASIN_COLOR = "Laranja"
PRICE = 24.99

GH = "https://raw.githubusercontent.com/solveonebr-design/AgenteIA/198560d45f1550a6bccbb4d2326790abc15e21f7/fotos/sv0005/"
AMZ = "https://m.media-amazon.com/images/I/"
SHARED = [AMZ + "61HhXTrLnIL.jpg",   # corredor + 7 cores empilhadas
          AMZ + "61ViooYTg5L.jpg",   # saida para fone, ziper, faixa refletiva
          AMZ + "61S1idBmVnL.jpg",   # capacidade e medidas
          AMZ + "61lklaXPGeL.jpg",   # neoprene resistente a agua
          AMZ + "61chJqPHQGL.jpg",   # cinto elastico ate 120 cm
          AMZ + "71GrSvNk2iL.jpg"]   # usos: academia, ciclismo, corrida, pet
GH2 = "https://raw.githubusercontent.com/solveonebr-design/AgenteIA/321efd3d33dfcec36e0378f94883628df85674b8/fotos/sv0005/"
# v2: fotos reais por cor (fundo e nome da cor removidos); verde gerado da laranja; preto mantido
MAIN = {"Laranja": GH2 + "laranja_principal_v2.jpg", "Verde": GH2 + "verde_principal_v2.jpg",
        "Rosa": GH2 + "rosa_principal_v2.jpg", "Preto": GH + "preto_principal.jpg",
        "Azul": GH2 + "azul_claro_principal_v2.jpg"}
PHOTOS = {color: [url] + SHARED for color, url in MAIN.items()}

TITLE = ("Pochete Esportiva para Corrida com Porta Celular, Saída para Fone, Faixa Refletiva e Cinto Elástico "
         "Ajustável, Resistente à Água, Caminhada, Academia e Ciclismo")
BULLETS = [
    "RESISTENTE À ÁGUA E AO SUOR: tecido em neoprene que ajuda a proteger celular, chaves e documentos contra "
    "suor e chuva leve durante corridas, caminhadas e treinos ao ar livre.",
    "PORTA-CELULAR COM SAÍDA PARA FONE: compartimento com zíper reforçado que acomoda a maioria dos "
    "smartphones e tem saída para o cabo do fone de ouvido.",
    "CINTO ELÁSTICO AJUSTÁVEL: fivela de encaixe rápido e regulagem para cinturas de até 120 cm, que ajuda a "
    "manter a pochete firme junto ao corpo durante o movimento.",
    "FAIXA REFLETIVA: aumenta a visibilidade em ambientes com pouca luz, trazendo mais segurança para treinos "
    "no início da manhã ou à noite.",
    "LEVE E DISCRETA: pesa apenas 47 g e tem espaço para chaves, documentos, dinheiro e cartões. Ideal para "
    "corrida, caminhada, academia, ciclismo, trilhas e passeios com o pet.",
]
DESCRIPTION = (
    "Pochete esportiva leve e discreta, feita para levar o essencial durante corridas, caminhadas e treinos "
    "sem ocupar as mãos.\n\n"
    "O compartimento principal, com zíper reforçado, acomoda a maioria dos smartphones e tem saída para o cabo "
    "do fone de ouvido. Também há espaço para chaves, documentos, dinheiro e cartões.\n\n"
    "O tecido em neoprene é resistente à água e ajuda a proteger seus itens contra suor e chuva leve. A faixa "
    "refletiva aumenta a visibilidade em locais com pouca luz, e o cinto elástico com fivela de encaixe rápido "
    "se ajusta a cinturas de até 120 cm.\n\n"
    "Especificações:\n"
    "- Material: neoprene, nylon e poliéster\n"
    "- Cinto ajustável: até 120 cm\n"
    "- Peso: 47 g\n"
    "- Tamanho único\n\n"
    "Cuidados: lavar à mão, sem alvejantes ou produtos químicos agressivos. Não lavar em máquina.\n\n"
    "Conteúdo da embalagem: 1 pochete esportiva."
)
# Termos fora do titulo; a Amazon indexa ate ~249 bytes.
KEYWORDS = ("impermeável runner doleira bolsa cintura esporte fitness treino maratona trilha bike "
            "smartphone chaves passeio pet neoprene unissex")
SPECIAL_FEATURES = ["Resistente à água", "Faixa refletiva", "Saída para fone de ouvido", "Cinto ajustável", "Leve"]

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
    assert len(TITLE) + len(" - Laranja") <= 200, len(TITLE)
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
