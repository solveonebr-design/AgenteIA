#!/usr/bin/env python3
"""Baixa as etiquetas FNSKU oficiais da Amazon (mesmo layout do Seller Central > Imprimir etiquetas de produtos),
impressao termica, um PDF por SKU nomeado com o SKU.

Uso:
  python3 scripts/etiquetas_amazon.py pedido.json saida/ [largura_mm altura_mm] [--duplas espaco_mm]
pedido.json: {"quantidades": {"SKU": n, ...}}  (formato salvo pela pagina "Pedido de Etiquetas FNSKU")
--duplas: gera tambem SKU_duplas.pdf com 2 etiquetas lado a lado por pagina, para rolo de 2 colunas
(ex.: 50 30 --duplas 2 -> pagina de 102 x 30 mm).
API: Fulfillment Inbound 2024-03-20, createMarketplaceItemLabels (labelType THERMAL_PRINTING).
"""
import json
import os
import sys
import time
import urllib.request

import listar_produtos as lp

MM = 72 / 25.4


def duplas(path, width, height, gap):
    """Monta 2 etiquetas por pagina (rolo de 2 colunas); a ultima fica sozinha se o total for impar."""
    import pymupdf
    src = pymupdf.open(path)
    out = pymupdf.open()
    w, h, g = width * MM, height * MM, gap * MM
    for i in range(0, len(src), 2):
        page = out.new_page(width=2 * w + g, height=h)
        page.show_pdf_page(pymupdf.Rect(0, 0, w, h), src, i)
        if i + 1 < len(src):
            page.show_pdf_page(pymupdf.Rect(w + g, 0, 2 * w + g, h), src, i + 1)
    dest = path[:-4] + "_duplas.pdf"
    out.save(dest)
    return dest


def main():
    args = sys.argv[1:]
    gap = None
    if "--duplas" in args:
        i = args.index("--duplas")
        gap = float(args[i + 1])
        del args[i:i + 2]
    pedido = json.load(open(args[0]))["quantidades"]
    outdir = args[1] if len(args) > 1 else "etiquetas"
    width = float(args[2]) if len(args) > 2 else 60
    height = float(args[3]) if len(args) > 3 else 40
    os.makedirs(outdir, exist_ok=True)
    client = lp.Client()
    client.endpoint = lp.ENDPOINTS[0]
    mkt = lp.env("SPAPI_MARKETPLACE_ID")
    for sku, n in sorted(pedido.items()):
        if not n:
            continue
        body = {"marketplaceId": mkt, "mskuQuantities": [{"msku": sku, "quantity": int(n)}],
                "labelType": "THERMAL_PRINTING", "width": width, "height": height, "localeCode": "pt_BR"}
        resp = client.post("/inbound/fba/2024-03-20/items/labels", body)
        uri = resp["documentDownloads"][0]["uri"]
        path = os.path.join(outdir, f"{sku}.pdf")
        with urllib.request.urlopen(uri, timeout=60) as r, open(path, "wb") as f:
            f.write(r.read())
        print(f"{sku}.pdf  {n:>3} etiquetas")
        if gap is not None:
            print("  ", os.path.basename(duplas(path, width, height, gap)))
        time.sleep(1)  # limite de requisicoes da API


if __name__ == "__main__":
    main()
