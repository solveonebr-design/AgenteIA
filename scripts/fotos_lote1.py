#!/usr/bin/env python3
"""Galerias de fotos dos anuncios avulsos, na ordem recomendada pela Amazon.

Ordem usada: 1) principal em fundo branco, so o produto; 2) infografico do principal diferencial;
3) medidas/detalhes; 4) produto em uso; 5) ambientacao; por ultimo, embalagem e fotos secundarias.

Uso:
  python3 scripts/fotos_lote1.py preview   # valida, nao grava
  python3 scripts/fotos_lote1.py aplicar   # grava na Amazon
"""
import sys
import urllib.parse

import listar_produtos as lp
import variacoes_sv0011 as v

GH = "https://raw.githubusercontent.com/solveonebr-design/AgenteIA/5f218b8d4d79fc5d28d1bdc2b6f24a38d19452f7/fotos/lote1/"


def amz(*names):
    return ["https://m.media-amazon.com/images/I/" + urllib.parse.quote(n) + ".jpg" for n in names]


NV12_GALLERY = amz("41p+6R5Co9L",   # medidas 13 x 9 cm
                   "41H28dwFbPL",   # pecas desmontadas
                   "61NFPuz9g4L",   # em uso, legumes picados
                   "61X1b2DeNjL",   # ambientacao na cozinha
                   "51lBDn2it-L")   # caixa (por ultimo)

GH2 = "https://raw.githubusercontent.com/solveonebr-design/AgenteIA/1758200a1464c664189d9ec7098d4cf02c92272a/fotos/lote1/"

PLAN = {
    "0001_FBA": [GH2 + "0001_principal.jpg"] + amz("41TiVXpvBWL") + [GH2 + "0001_ambiente.jpg"] + amz(
                    "51djuIOSx1L"),  # principal, medidas, ambiente, estojo na mao (saiu a antiga de 220 px)
    "0003_FBA": amz("51wPxInC5pL",   # principal
                    "51FJ2poDFTL",   # infografico das pontas 6 mm / 1 mm
                    "51yTXQzHxzL",   # aviso: envio somente corpo preto
                    "61Anz47wjRL",   # canetas de corpo preto (as enviadas)
                    "51ZDiYWbJCL",   # em uso
                    "61sCPQ-L24L",   # ambientacao
                    "51nvh8oRC6L", "51Z2-JmOZ1L"),
    "SV_0006_FBA": [GH + "sv0006_principal.jpg"] + amz(
                    "71om4IvgT0L",   # baralho aberto em leque + caixa
                    "71cNah-qWmL",   # resistente a agua
                    "718NNmQdE8L",   # detalhe com gotas
                    "61ZFCQwZ4uL",   # leque na mao + caixa
                    "71f+fk0v25L",   # ambientacao
                    "71AGk8EZiNL",   # verso das cartas
                    "61oQjFy611L"),  # foto original (marmore)
    "0007_FBA": [GH + "0007_principal.jpg"] + amz(
                    "51jgbmohuHL",   # niveis de resistencia
                    "51Vuli81NPL",   # em uso (agachamento)
                    "71BjqJoJGSL",   # colagem de exercicios
                    "51zXXKHvu6L", "516pOtOLYtL"),
    "SV_0008_FBA": [GH + "sv0008_principal.jpg"] + amz(
                    "61C725aqIzL",   # instalado com objetos
                    "6114tl4aVKL",   # dois bancos
                    "61Gxp3MTOZL",   # outro angulo no carro
                    "417OakNuJUL",   # medidas 60 x 40 cm
                    "51sbxQxIS3L"),  # embalagem (por ultimo)
    "SV_0010_FBA": [GH + "sv0010_principal.jpg"] + amz(
                    "61FWXOtxEVL",   # com sapatos
                    "61-ttScjwWL",   # sapatos e bolsas
                    "61S7KePVAVL",   # 4 andares / vendido desmontado
                    "51l0imVJQoL",   # embalagem e detalhe
                    "61fM9J3wVHL"),  # uso alternativo com roupas
    "SV_NV0012_PRETO_FBA": amz("51L15jywL1L") + NV12_GALLERY,
    "SV_NV0012_VERMELHO_FBA": amz("5102BrfoonL") + NV12_GALLERY,
}


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "preview"
    if mode not in ("preview", "aplicar"):
        sys.exit("Modo deve ser 'preview' ou 'aplicar'")
    client = lp.Client()
    client.endpoint = lp.ENDPOINTS[0]
    mkt = lp.env("SPAPI_MARKETPLACE_ID")
    seller = lp.env("SPAPI_SELLER_ID")
    print("Modo:", "PRE-VISUALIZACAO (nada e gravado)" if mode == "preview" else "APLICAR")
    for sku, urls in PLAN.items():
        assert len(urls) == len(set(urls)) <= 9, sku
        cur = client.get(f"/listings/2021-08-01/items/{seller}/{sku}",
                         {"marketplaceIds": mkt, "includedData": "attributes,summaries"})
        ptype, attrs = cur["summaries"][0]["productType"], cur["attributes"]
        want = {k: [{"media_location": u, "marketplace_id": mkt}] for k, u in zip(v.IMAGE_ATTRS, urls)}
        ops = [{"op": "replace", "path": f"/attributes/{k}", "value": val} for k, val in want.items()]
        ops += [{"op": "delete", "path": f"/attributes/{k}", "value": attrs[k]}
                for k in v.IMAGE_ATTRS if k in attrs and k not in want]
        resp = v.request(client, "PATCH", sku, {"productType": ptype, "patches": ops}, preview=mode == "preview")
        print(f"PATCH {sku}: {resp.get('status')} ({len(urls)} fotos)",
              [i.get("message", "")[:160] for i in resp.get("issues", [])])


if __name__ == "__main__":
    main()
