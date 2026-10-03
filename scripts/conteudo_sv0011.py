#!/usr/bin/env python3
"""Atualiza titulo, bullets, descricao e palavras-chave da familia SV_0011.

Uso:
  python3 scripts/conteudo_sv0011.py preview   # so valida, nao grava
  python3 scripts/conteudo_sv0011.py aplicar   # grava na Amazon
"""
import sys

import listar_produtos as lp
import variacoes_sv0011 as v

TITLE = ("Escorredor de Silicone Retrátil Dobrável Quadrado com Alças, Coador Multiuso para Pia, "
         "Macarrão, Frutas, Legumes e Verduras, 29 x 21,5 cm")

BULLETS = [
    "DOBRÁVEL E COMPACTO: aberto mede cerca de 29 x 21,5 x 8,5 cm e, retraído, fica com apenas 4,5 cm "
    "de altura. Guarda com facilidade em gavetas e armários e é prático para levar em viagens e camping.",
    "MULTIUSO NA COZINHA: escorra macarrão e outras massas, lave frutas, legumes, verduras e arroz ou use "
    "como cesto para servir. Um único utensílio para várias tarefas do dia a dia.",
    "DRENAGEM RÁPIDA: o fundo perfurado deixa a água escoar rapidamente, sem acumular, para que os "
    "alimentos fiquem limpos e prontos em menos tempo.",
    "ALÇAS LATERAIS: as duas alças facilitam segurar o escorredor com firmeza e apoiá-lo sobre a pia ou "
    "dentro de uma bacia, mantendo as mãos longe da água.",
    "LEVE E FÁCIL DE LIMPAR: corpo em silicone flexível com borda e base em polipropileno (PP), sem BPA e "
    "com apenas 147 g. Lave com água e detergente neutro e guarde retraído depois do uso.",
]

DESCRIPTION = (
    "Escorredor de silicone retrátil com formato quadrado e alças laterais, feito para simplificar a rotina "
    "na cozinha e economizar espaço.\n\n"
    "Aberto, serve para escorrer macarrão, lavar frutas, legumes, verduras e arroz ou servir "
    "alimentos. Depois do uso, basta pressionar para retraí-lo: ele fica com apenas 4,5 cm de altura e cabe "
    "em gavetas, armários, mochilas de camping e motorhomes.\n\n"
    "O corpo em silicone flexível, combinado com a borda e a base em polipropileno (PP), deixa o escorredor "
    "leve, firme e livre de BPA. É fácil de lavar com água e detergente neutro, e o fundo perfurado garante "
    "drenagem rápida da água.\n\n"
    "Medidas aproximadas:\n"
    "- Aberto: 29 x 21,5 x 8,5 cm\n"
    "- Retraído: 29 x 21,5 x 4,5 cm\n"
    "- Peso: 147 g\n\n"
    "Conteúdo da embalagem: 1 escorredor de silicone retrátil."
)

# Termos que nao estao no titulo; a Amazon indexa ate ~249 bytes neste campo.
KEYWORDS = ("peneira cesto colapsável sanfonado lavar arroz salada massas utensílio compacto economiza espaço "
            "camping viagem motorhome utilidades domésticas cozinha vasilha bacia hortifrúti organização sem bpa")

SPECIAL_FEATURES = ["Retrátil", "Dobrável", "Livre de BPA", "Alças laterais", "Fácil de limpar"]
SKUS = {"SV_0011": None, "SV_0011_VERMELHO_FBA": "Vermelho", "SV_0011_VERDE_FBA": "Verde"}


def texts(values, mkt):
    return [{"value": val, "language_tag": "pt_BR", "marketplace_id": mkt} for val in values]


def check():
    assert len(TITLE) + len(" - Vermelho") <= 200, len(TITLE)
    assert all(len(b) <= 700 for b in BULLETS)
    assert len(KEYWORDS.encode()) <= 249, len(KEYWORDS.encode())
    title_words = {w.strip(",").lower() for w in TITLE.split()}
    repeated = [w for w in KEYWORDS.lower().split() if w in title_words]
    assert not repeated, repeated


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "preview"
    if mode not in ("preview", "aplicar"):
        sys.exit("Modo deve ser 'preview' ou 'aplicar'")
    check()
    client = lp.Client()
    client.endpoint = lp.ENDPOINTS[0]
    mkt = lp.env("SPAPI_MARKETPLACE_ID")
    print("Modo:", "PRE-VISUALIZACAO (nada e gravado)" if mode == "preview" else "APLICAR")
    for sku, color in SKUS.items():
        title = f"{TITLE} - {color}" if color else TITLE
        attrs = {
            "item_name": texts([title], mkt),
            "bullet_point": texts(BULLETS, mkt),
            "product_description": texts([DESCRIPTION], mkt),
            "generic_keyword": texts([KEYWORDS], mkt),
            "special_feature": texts(SPECIAL_FEATURES, mkt),
            "item_shape": texts(["Quadrado"], mkt),
        }
        patches = [{"op": "replace", "path": f"/attributes/{k}", "value": val} for k, val in attrs.items()]
        resp = v.request(client, "PATCH", sku, {"productType": v.PRODUCT_TYPE, "patches": patches},
                         preview=mode == "preview")
        print(f"\nPATCH {sku}: {resp.get('status')}")
        for issue in resp.get("issues", []):
            print(f"  [{issue.get('severity', '')}] {issue.get('code', '')} {issue.get('message', '')}"
                  f" {issue.get('attributeNames', '')}")


if __name__ == "__main__":
    main()
