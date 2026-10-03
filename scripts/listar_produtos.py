#!/usr/bin/env python3
"""Lista os produtos publicados (anuncios) da conta na Amazon via SP-API.

Somente leitura. As credenciais vem exclusivamente das variaveis de ambiente:
  SPAPI_CLIENT_ID, SPAPI_CLIENT_SECRET, SPAPI_REFRESH_TOKEN, SPAPI_SELLER_ID
  SPAPI_MARKETPLACE_ID (opcional, padrao Brasil)
  SPAPI_ENDPOINT (opcional; se ausente testa NA, EU e FE nesta ordem)

Gera produtos_publicados.csv e produtos_publicados.json no diretorio de saida
(argumento 1, padrao "data").
"""
import csv
import gzip
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

LWA_URL = "https://api.amazon.com/auth/o2/token"
ENDPOINTS = [
    "https://sellingpartnerapi-na.amazon.com",
    "https://sellingpartnerapi-eu.amazon.com",
    "https://sellingpartnerapi-fe.amazon.com",
]
SEARCH_LIMIT = 1000
CSV_COLUMNS = ["sku", "asin", "titulo", "tipo_produto", "status", "preco", "moeda", "criado_em", "atualizado_em"]


class ApiError(Exception):
    def __init__(self, status, body):
        super().__init__(f"HTTP {status}: {body}")
        self.status = status
        self.body = body


def env(name, default=None):
    value = os.environ.get(name, default)
    if not value:
        sys.exit(f"Variavel de ambiente ausente: {name}")
    return value


def http(method, url, headers=None, data=None, retries=6):
    for attempt in range(retries):
        req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            if e.code == 429 and attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            raise ApiError(e.code, body) from None


class Client:
    def __init__(self):
        self.client_id = env("SPAPI_CLIENT_ID")
        self.client_secret = env("SPAPI_CLIENT_SECRET")
        self.refresh_token = env("SPAPI_REFRESH_TOKEN")
        self.token = None
        self.token_at = 0
        self.endpoint = os.environ.get("SPAPI_ENDPOINT")

    def access_token(self):
        if self.token and time.time() - self.token_at < 50 * 60:
            return self.token
        data = urllib.parse.urlencode({
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }).encode()
        try:
            resp = json.loads(http("POST", LWA_URL, {"Content-Type": "application/x-www-form-urlencoded"}, data))
        except ApiError as e:
            try:
                err = json.loads(e.body)
                msg = f"{err.get('error')}: {err.get('error_description')}"
            except ValueError:
                msg = f"HTTP {e.status}"
            sys.exit(f"Falha no token LWA ({msg})")
        self.token = resp["access_token"]
        self.token_at = time.time()
        return self.token

    def get(self, path, params=None):
        url = self.endpoint + path
        if params:
            url += "?" + urllib.parse.urlencode(params, doseq=True)
        return json.loads(http("GET", url, {"x-amz-access-token": self.access_token()}))

    def post(self, path, body):
        headers = {"x-amz-access-token": self.access_token(), "Content-Type": "application/json"}
        return json.loads(http("POST", self.endpoint + path, headers, json.dumps(body).encode()))


def search_listings(client, seller_id, marketplace_id):
    path = f"/listings/2021-08-01/items/{urllib.parse.quote(seller_id)}"
    base = {"marketplaceIds": marketplace_id, "includedData": "summaries,offers", "pageSize": 20}
    items, token = [], None
    while True:
        params = dict(base, pageToken=token) if token else base
        resp = client.get(path, params)
        items.extend(resp.get("items", []))
        token = (resp.get("pagination") or {}).get("nextToken")
        if not token:
            return items, resp.get("numberOfResults")


def pick_endpoint(client, seller_id, marketplace_id):
    """Descobre o endpoint da regiao certa tentando NA, EU e FE."""
    candidates = [client.endpoint] if client.endpoint else ENDPOINTS
    last = None
    for endpoint in candidates:
        client.endpoint = endpoint
        try:
            return search_listings(client, seller_id, marketplace_id)
        except ApiError as e:
            last = e
            if e.status == 403 and "denied" not in e.body.lower():
                continue
            raise
    raise last


def report_rows(client, marketplace_id):
    """Plano alternativo (> 1000 anuncios): relatorio GET_MERCHANT_LISTINGS_ALL_DATA."""
    report_id = client.post("/reports/2021-06-30/reports", {
        "reportType": "GET_MERCHANT_LISTINGS_ALL_DATA",
        "marketplaceIds": [marketplace_id],
    })["reportId"]
    while True:
        report = client.get(f"/reports/2021-06-30/reports/{report_id}")
        status = report["processingStatus"]
        if status == "DONE":
            break
        if status in ("CANCELLED", "FATAL"):
            sys.exit(f"Relatorio terminou com status {status}")
        time.sleep(15)
    doc = client.get(f"/reports/2021-06-30/documents/{report['reportDocumentId']}")
    raw = http("GET", doc["url"])
    if doc.get("compressionAlgorithm") == "GZIP":
        raw = gzip.decompress(raw)
    text = raw.decode("utf-8", "replace")
    return list(csv.DictReader(text.splitlines(), delimiter="\t"))


def item_to_row(item):
    summary = (item.get("summaries") or [{}])[0]
    price = ((item.get("offers") or [{}])[0].get("price")) or {}
    return {
        "sku": item.get("sku", ""),
        "asin": summary.get("asin", ""),
        "titulo": summary.get("itemName", ""),
        "tipo_produto": summary.get("productType", ""),
        "status": "|".join(summary.get("status") or []),
        "preco": price.get("amount", ""),
        "moeda": price.get("currencyCode", ""),
        "criado_em": summary.get("createdDate", ""),
        "atualizado_em": summary.get("lastUpdatedDate", ""),
    }


def report_to_row(r):
    return {
        "sku": r.get("seller-sku", ""),
        "asin": r.get("asin1", ""),
        "titulo": r.get("item-name", ""),
        "tipo_produto": "",
        "status": r.get("status", ""),
        "preco": r.get("price", ""),
        "moeda": "BRL" if r.get("price") else "",
        "criado_em": r.get("open-date", ""),
        "atualizado_em": "",
    }


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "data"
    seller_id = env("SPAPI_SELLER_ID")
    marketplace_id = env("SPAPI_MARKETPLACE_ID", "A2Q3Y263D00KWC")
    client = Client()

    try:
        items, total = pick_endpoint(client, seller_id, marketplace_id)
        if len(items) >= SEARCH_LIMIT or (total or 0) > SEARCH_LIMIT:
            raw = report_rows(client, marketplace_id)
            rows, full = [report_to_row(r) for r in raw], raw
        else:
            rows, full = [item_to_row(i) for i in items], items
    except ApiError as e:
        sys.exit(f"Erro da Amazon (endpoint {client.endpoint}): HTTP {e.status} {e.body}")

    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "produtos_publicados.json"), "w", encoding="utf-8") as f:
        json.dump(full, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, "produtos_publicados.csv"), "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    buyable = sum(1 for r in rows if "BUYABLE" in r["status"].split("|"))
    discoverable = sum(1 for r in rows if r["status"] == "DISCOVERABLE")
    print(f"Endpoint: {client.endpoint}")
    print(f"Total de anuncios: {len(rows)}")
    print(f"BUYABLE (a venda): {buyable}")
    print(f"Somente DISCOVERABLE: {discoverable}")


if __name__ == "__main__":
    main()
