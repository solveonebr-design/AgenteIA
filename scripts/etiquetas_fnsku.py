#!/usr/bin/env python3
"""Gera etiquetas FNSKU 60 x 40 mm (uma por pagina), um PDF por SKU, nomeado com o SKU.

Uso:
  python3 scripts/etiquetas_fnsku.py pedido.json saida/
pedido.json: {"quantidades": {"SKU": n, ...}}  (formato salvo pela pagina "Pedido de Etiquetas FNSKU")
Os FNSKUs vem da API de estoque FBA; o nome curto e a cor vem da tabela NOMES abaixo.
"""
import json
import os
import sys

from reportlab.graphics.barcode import code128
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

import listar_produtos as lp

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont("Sans", f"{FONT_DIR}/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("Sans-Bold", f"{FONT_DIR}/DejaVuSans-Bold.ttf"))

W, H = 60 * mm, 40 * mm
MARGIN = 3 * mm

# nome curto impresso na etiqueta (a Amazon pede o titulo, podendo ser abreviado) + cor
NOMES = {
    "0001_FBA": ("Kit Limpador de Ouvido 6 Ferramentas Inox e Estojo", ""),
    "0003_FBA": ("Kit 24 Canetas Marcadoras Ponta Dupla com Estojo", ""),
    "0007_FBA": ("Kit 5 Mini Bands Elásticas de Látex", ""),
    "SV_0002": ("Forma de Gelo 14 Cubos com Tampa e Fundo de Silicone", None),
    "SV_0004": ("Bolsa Térmica Lancheira 6,7 L com Alça de Ombro", None),
    "SV_0005": ("Pochete Esportiva para Corrida com Porta Celular", None),
    "SV_0006_FBA": ("Baralho Dourado 54 Cartas Resistente à Água", ""),
    "SV_0008_FBA": ("Organizador para Banco Traseiro do Carro 60 x 40 cm", ""),
    "SV_0009_FBA": ("Pano Multiuso Descartável Rolo com 50 Panos 25 x 30 cm", ""),
    "SV_0010_FBA": ("Sapateira Desmontável 4 Andares 12 Tubos", "Preto"),
    "SV_0011": ("Escorredor de Silicone Retrátil Quadrado com Alças", None),
    "SV_NV0012": ("Mini Processador Manual 500 ml com Puxador, 3 Lâminas", None),
}
CORES = {"AMARELO": "Amarelo", "AZUL": "Azul", "AZUL2": "Azul", "ROSA": "Rosa", "VERDE": "Verde", "CINZA2": "Cinza",
         "PRETO": "Preto", "LARANJA": "Laranja", "VERMELHO": "Vermelho"}


def nome_cor(sku):
    if sku in NOMES:
        return NOMES[sku]
    base, cor = sku.rsplit("_", 2)[0], sku.rsplit("_", 2)[1]
    return NOMES[base][0], CORES[cor]


def wrap(text, font, size, width, max_lines):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if pdfmetrics.stringWidth(test, font, size) <= width:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while pdfmetrics.stringWidth(lines[-1] + "…", font, size) > width:
            lines[-1] = lines[-1].rsplit(" ", 1)[0]
        lines[-1] += "…"
    return lines


def draw_label(c, fnsku, title, color):
    usable = W - 2 * MARGIN
    bc = code128.Code128(fnsku, barHeight=13 * mm, barWidth=0.33 * mm, quiet=False)
    bw = bc.width
    if bw > usable:  # encolhe as barras se o codigo for longo
        bc = code128.Code128(fnsku, barHeight=13 * mm, barWidth=0.33 * mm * usable / bw, quiet=False)
        bw = bc.width
    top = H - MARGIN
    bc.drawOn(c, (W - bw) / 2, top - 13 * mm)
    c.setFont("Sans-Bold", 9)
    c.drawCentredString(W / 2, top - 13 * mm - 3.6 * mm, fnsku)
    y = top - 13 * mm - 3.6 * mm - 3.4 * mm
    c.setFont("Sans", 6.6)
    full = title + (f" - {color}" if color else "")
    for line in wrap(full, "Sans", 6.6, usable, 3):
        c.drawCentredString(W / 2, y, line)
        y -= 2.8 * mm
    c.setFont("Sans-Bold", 7.5)
    c.drawCentredString(W / 2, MARGIN, "Novo")


def fnskus():
    c = lp.Client()
    c.endpoint = lp.ENDPOINTS[0]
    mkt = lp.env("SPAPI_MARKETPLACE_ID")
    out, token = {}, None
    while True:
        p = {"granularityType": "Marketplace", "granularityId": mkt, "marketplaceIds": mkt}
        if token:
            p["nextToken"] = token
        r = c.get("/fba/inventory/v1/summaries", p)
        for x in r["payload"]["inventorySummaries"]:
            out[x["sellerSku"]] = x.get("fnSku")
        token = (r.get("pagination") or {}).get("nextToken")
        if not token:
            return out


def main():
    pedido = json.load(open(sys.argv[1]))["quantidades"]
    outdir = sys.argv[2] if len(sys.argv) > 2 else "etiquetas"
    os.makedirs(outdir, exist_ok=True)
    codes = fnskus()
    for sku, n in sorted(pedido.items()):
        if not n:
            continue
        fn = codes.get(sku)
        if not fn:
            sys.exit(f"SKU sem FNSKU: {sku}")
        title, color = nome_cor(sku)
        path = os.path.join(outdir, f"{sku}.pdf")
        c = canvas.Canvas(path, pagesize=(W, H))
        c.setTitle(f"Etiquetas {sku} ({fn})")
        for _ in range(int(n)):
            draw_label(c, fn, title, color)
            c.showPage()
        c.save()
        print(f"{sku}.pdf  {n:>3} etiquetas  {fn}  {title}{' - ' + color if color else ''}")


if __name__ == "__main__":
    main()
