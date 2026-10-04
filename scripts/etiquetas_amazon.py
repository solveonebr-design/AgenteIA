#!/usr/bin/env python3
"""Baixa as etiquetas FNSKU oficiais da Amazon (mesmo layout do Seller Central > Imprimir etiquetas de produtos),
impressao termica, um PDF por SKU nomeado com o SKU.

Uso:
  python3 scripts/etiquetas_amazon.py pedido.json saida/ [largura_mm altura_mm]
pedido.json: {"quantidades": {"SKU": n, ...}}  (formato salvo pela pagina "Pedido de Etiquetas FNSKU")
API: Fulfillment Inbound 2024-03-20, createMarketplaceItemLabels (labelType THERMAL_PRINTING).
"""
import json
import os
import sys
import time
import urllib.request

import listar_produtos as lp


def main():
    pedido = json.load(open(sys.argv[1]))["quantidades"]
    outdir = sys.argv[2] if len(sys.argv) > 2 else "etiquetas"
    width = float(sys.argv[3]) if len(sys.argv) > 3 else 60
    height = float(sys.argv[4]) if len(sys.argv) > 4 else 40
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
        time.sleep(1)  # limite de requisicoes da API


if __name__ == "__main__":
    main()
