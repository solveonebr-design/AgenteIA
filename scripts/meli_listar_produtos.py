#!/usr/bin/env python3
"""Lista os anuncios da conta no Mercado Livre e grava CSV e JSON.

Uso: python3 meli_listar_produtos.py <pasta_saida>

Le MELI_ACCESS_TOKEN e MELI_USER_ID do ambiente. Este script NAO renova o
token: a renovacao fica so no workflow .github/workflows/meli.yml, porque o
refresh token do Mercado Livre e de uso unico.
"""
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.mercadolibre.com"
CAMPOS = ["id", "title", "status", "price", "currency_id", "available_quantity",
          "sold_quantity", "listing_type_id", "logistic_type", "catalog_listing",
          "category_id", "permalink"]


def env(nome):
    valor = os.environ.get(nome, "").strip()
    if not valor:
        sys.exit(f"Variavel de ambiente ausente: {nome}")
    return valor


TOKEN = env("MELI_ACCESS_TOKEN")


def get(caminho, params=None, tentativas=6):
    url = API + caminho
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}"})
    for i in range(tentativas):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and i < tentativas - 1:
                time.sleep(2 ** i)
                continue
            corpo = e.read().decode(errors="replace")[:300]
            sys.exit(f"HTTP {e.code} em {caminho}: {corpo}")


def ids_dos_anuncios(user_id):
    """Busca paginada com search_type=scan (sem o limite de 1.000 do offset)."""
    ids, scroll = [], None
    while True:
        params = {"search_type": "scan", "limit": 100}
        if scroll:
            params["scroll_id"] = scroll
        resp = get(f"/users/{user_id}/items/search", params)
        lote = resp.get("results", [])
        if not lote:
            return ids
        ids.extend(lote)
        scroll = resp.get("scroll_id")


def detalhes(ids):
    """Multiget de 20 em 20."""
    itens = []
    for i in range(0, len(ids), 20):
        resp = get("/items", {"ids": ",".join(ids[i:i + 20])})
        for r in resp:
            if r.get("code") == 200:
                b = r["body"]
                b["logistic_type"] = (b.get("shipping") or {}).get("logistic_type")
                itens.append({c: b.get(c) for c in CAMPOS})
            else:
                print(f"Aviso: {r.get('body', {}).get('id')} retornou {r.get('code')}")
    return itens


def main():
    saida = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(saida, exist_ok=True)
    user_id = os.environ.get("MELI_USER_ID") or str(get("/users/me")["id"])

    itens = detalhes(ids_dos_anuncios(user_id))
    itens.sort(key=lambda x: (x["status"] or "", x["title"] or ""))

    with open(os.path.join(saida, "meli_produtos.json"), "w", encoding="utf-8") as f:
        json.dump(itens, f, ensure_ascii=False, indent=2)
    with open(os.path.join(saida, "meli_produtos.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writeheader()
        w.writerows(itens)

    por_status = {}
    for it in itens:
        por_status[it["status"]] = por_status.get(it["status"], 0) + 1
    print(f"Total: {len(itens)} anuncios")
    for st, n in sorted(por_status.items()):
        print(f"  {st}: {n}")


if __name__ == "__main__":
    main()
