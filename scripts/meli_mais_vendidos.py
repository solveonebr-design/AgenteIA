#!/usr/bin/env python3
"""Top 20 mais vendidos do Mercado Livre por categoria.

Uso: python3 meli_mais_vendidos.py <pasta_saida> [categoria]

Sem categoria: percorre todas as categorias principais do Brasil (MLB).
Com categoria (ex.: MLB1574): percorre as subcategorias dela.

Le MELI_ACCESS_TOKEN do ambiente. Somente leitura. Nao renova o token
(a renovacao fica so no workflow .github/workflows/meli.yml).
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
SITE = "MLB"
CAMPOS = ["categoria_id", "categoria", "posicao", "tipo", "id", "titulo",
          "preco", "moeda", "link", "imagem"]

TOKEN = os.environ.get("MELI_ACCESS_TOKEN", "").strip()
if not TOKEN:
    sys.exit("Variavel de ambiente ausente: MELI_ACCESS_TOKEN")


def get(caminho, params=None, tentativas=6):
    """GET com nova tentativa em 429/5xx. Devolve None em 403/404."""
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
            if e.code in (403, 404):
                return None
            corpo = e.read().decode(errors="replace")[:300]
            sys.exit(f"HTTP {e.code} em {caminho}: {corpo}")


def categorias(raiz):
    if raiz:
        cat = get(f"/categories/{raiz}") or {}
        return cat.get("children_categories") or [{"id": raiz, "name": cat.get("name", raiz)}]
    return get(f"/sites/{SITE}/categories") or []


def detalhes_itens(ids):
    """Multiget de anuncios (ITEM), 20 por chamada."""
    out = {}
    for i in range(0, len(ids), 20):
        resp = get("/items", {"ids": ",".join(ids[i:i + 20]),
                              "attributes": "id,title,price,currency_id,permalink,thumbnail"}) or []
        for r in resp:
            if r.get("code") == 200:
                b = r["body"]
                out[b["id"]] = {"titulo": b.get("title"), "preco": b.get("price"),
                                "moeda": b.get("currency_id"), "link": b.get("permalink"),
                                "imagem": b.get("thumbnail")}
    return out


def detalhes_produto(pid):
    """Produto de catalogo (PRODUCT): preco do ganhador da buy box."""
    b = get(f"/products/{pid}")
    if not b:
        return {}
    win = b.get("buy_box_winner") or {}
    fotos = b.get("pictures") or [{}]
    return {"titulo": b.get("name"), "preco": win.get("price"),
            "moeda": win.get("currency_id"), "link": b.get("permalink"),
            "imagem": fotos[0].get("url")}


def main():
    saida = sys.argv[1] if len(sys.argv) > 1 else "."
    raiz = sys.argv[2].strip() if len(sys.argv) > 2 else ""
    os.makedirs(saida, exist_ok=True)

    linhas, sem_ranking = [], []
    for cat in categorias(raiz):
        dest = get(f"/highlights/{SITE}/category/{cat['id']}")
        conteudo = (dest or {}).get("content") or []
        if not conteudo:
            sem_ranking.append(cat["name"])
            continue
        itens = detalhes_itens([c["id"] for c in conteudo if c.get("type") == "ITEM"])
        for c in sorted(conteudo, key=lambda c: c.get("position", 0)):
            info = itens.get(c["id"]) if c.get("type") == "ITEM" else None
            if info is None and c.get("type") == "PRODUCT":
                info = detalhes_produto(c["id"])
            linhas.append({"categoria_id": cat["id"], "categoria": cat["name"],
                           "posicao": c.get("position"), "tipo": c.get("type"),
                           "id": c["id"], **(info or {})})
        print(f"{cat['name']}: {len(conteudo)}")

    with open(os.path.join(saida, "meli_mais_vendidos.json"), "w", encoding="utf-8") as f:
        json.dump(linhas, f, ensure_ascii=False, indent=2)
    # utf-8-sig para o Excel abrir os acentos corretamente
    with open(os.path.join(saida, "meli_mais_vendidos.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS, delimiter=";")
        w.writeheader()
        for l in linhas:
            # preco com virgula decimal, como o Excel em portugues espera
            preco = l.get("preco")
            w.writerow({**l, "preco": "" if preco is None else str(preco).replace(".", ",")})

    print(f"Total: {len(linhas)} produtos em {len({l['categoria_id'] for l in linhas})} categorias")
    if sem_ranking:
        print("Sem ranking: " + ", ".join(sem_ranking))


if __name__ == "__main__":
    main()
