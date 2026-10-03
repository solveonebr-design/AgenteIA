#!/usr/bin/env python3
"""Cria as variacoes de cor (Vermelho/Verde) do Escorredor de Silicone SV_0011.

Estrutura:
  SV_0011              pai (sem oferta), tema de variacao COLOR
  SV_0011_VERMELHO_FBA filho Vermelho (ASIN B0HJT25LB3, substituiu o SKU SV_0011_FBA)
  SV_0011_VERDE_FBA    filho Verde (novo, copia os atributos do Vermelho)

Uso:
  python3 scripts/variacoes_sv0011.py preview [fotos.json]   # so valida, nao grava
  python3 scripts/variacoes_sv0011.py aplicar [fotos.json]   # grava na Amazon

fotos.json (opcional): {"Vermelho": ["url principal", "url 2", ...], "Verde": [...]}
Sem o arquivo, as cores usam as fotos atuais do SV_0011_VERMELHO_FBA.
"""
import copy
import json
import sys
import urllib.parse

import listar_produtos as lp

PRODUCT_TYPE = "DRYING_RACK"
PARENT_SKU = "SV_0011"
SOURCE_SKU = "SV_0011_VERMELHO_FBA"
CHILDREN = {"Vermelho": SOURCE_SKU, "Verde": "SV_0011_VERDE_FBA"}
OFFER_ATTRS = ("purchasable_offer", "list_price", "fulfillment_availability", "skip_offer", "condition_type")
IMAGE_ATTRS = ["main_product_image_locator"] + [f"other_product_image_locator_{i}" for i in range(1, 9)]


def request(client, method, sku, body, preview):
    seller = lp.env("SPAPI_SELLER_ID")
    params = {"marketplaceIds": lp.env("SPAPI_MARKETPLACE_ID"), "includedData": "issues"}
    if preview:
        params["mode"] = "VALIDATION_PREVIEW"
    url = (f"{client.endpoint}/listings/2021-08-01/items/{urllib.parse.quote(seller)}/"
           f"{urllib.parse.quote(sku)}?{urllib.parse.urlencode(params)}")
    headers = {"x-amz-access-token": client.access_token(), "Content-Type": "application/json"}
    try:
        return json.loads(lp.http(method, url, headers, json.dumps(body).encode()))
    except lp.ApiError as e:
        return {"status": f"HTTP {e.status}", "issues": [{"message": e.body}]}


def mkt_value(value, mkt, lang=True):
    v = {"value": value, "marketplace_id": mkt}
    if lang:
        v["language_tag"] = "pt_BR"
    return [v]


def image_attrs(urls, mkt):
    return {name: [{"media_location": url, "marketplace_id": mkt}] for name, url in zip(IMAGE_ATTRS, urls)}


def child_attrs(base, color, mkt, images):
    a = copy.deepcopy(base)
    a["color"] = mkt_value(color, mkt)
    a["item_name"] = mkt_value(f"{base['item_name'][0]['value']} - {color}", mkt)
    a["parentage_level"] = mkt_value("child", mkt, lang=False)
    a["child_parent_sku_relationship"] = [
        {"child_relationship_type": "variation", "parent_sku": PARENT_SKU, "marketplace_id": mkt}]
    a["variation_theme"] = [{"name": "COLOR"}]
    if images:
        for name in IMAGE_ATTRS:
            a.pop(name, None)
        a.update(image_attrs(images, mkt))
    return a


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "preview"
    if mode not in ("preview", "aplicar"):
        sys.exit("Modo deve ser 'preview' ou 'aplicar'")
    preview = mode == "preview"
    photos = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else {}

    client = lp.Client()
    client.endpoint = lp.ENDPOINTS[0]
    mkt = lp.env("SPAPI_MARKETPLACE_ID")
    seller = lp.env("SPAPI_SELLER_ID")
    source = client.get(f"/listings/2021-08-01/items/{seller}/{SOURCE_SKU}",
                        {"marketplaceIds": mkt, "includedData": "attributes"})["attributes"]

    parent = {k: v for k, v in copy.deepcopy(source).items() if k not in OFFER_ATTRS and k != "color"}
    parent["parentage_level"] = mkt_value("parent", mkt, lang=False)
    parent["variation_theme"] = [{"name": "COLOR"}]
    if photos.get("Vermelho"):
        for name in IMAGE_ATTRS:
            parent.pop(name, None)
        parent.update(image_attrs(photos["Vermelho"], mkt))

    red = child_attrs(source, "Vermelho", mkt, photos.get("Vermelho"))
    patches = [{"op": "replace", "path": f"/attributes/{k}", "value": red[k]}
               for k in ("color", "item_name", "parentage_level", "child_parent_sku_relationship", "variation_theme",
                         "external_testing_certification", "power_source_type")]
    if photos.get("Vermelho"):
        old = [n for n in IMAGE_ATTRS if n in source and n not in red]
        patches += [{"op": "delete", "path": f"/attributes/{n}", "value": source[n]} for n in old]
        patches += [{"op": "replace", "path": f"/attributes/{n}", "value": red[n]} for n in IMAGE_ATTRS if n in red]

    steps = [
        ("PUT", PARENT_SKU, {"productType": PRODUCT_TYPE, "requirements": "LISTING_PRODUCT_ONLY", "attributes": parent}),
        ("PATCH", SOURCE_SKU, {"productType": PRODUCT_TYPE, "patches": patches}),
        ("PUT", CHILDREN["Verde"], {"productType": PRODUCT_TYPE, "requirements": "LISTING",
                                    "attributes": child_attrs(source, "Verde", mkt, photos.get("Verde"))}),
    ]
    print("Modo:", "PRE-VISUALIZACAO (nada e gravado)" if preview else "APLICAR")
    for method, sku, body in steps:
        resp = request(client, method, sku, body, preview)
        print(f"\n{method} {sku}: {resp.get('status')}")
        for issue in resp.get("issues", []):
            print(f"  [{issue.get('severity', '')}] {issue.get('code', '')} {issue.get('message', '')}"
                  f" {issue.get('attributeNames', '')}")


if __name__ == "__main__":
    main()
