#!/usr/bin/env python3
"""Gera docs/Integracao_Mercado_Livre.pdf a partir do .md (pip install reportlab).

Uso: python3 docs/gerar_documentacao_meli.py
Converte o subconjunto de Markdown usado no documento: titulos, paragrafos,
listas, citacoes, tabelas e blocos de codigo.
"""
import html
import os
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (KeepTogether, Paragraph, Preformatted, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

AQUI = os.path.dirname(os.path.abspath(__file__))
ORIGEM = os.path.join(AQUI, "Integracao_Mercado_Livre.md")
DESTINO = os.path.join(AQUI, "Integracao_Mercado_Livre.pdf")
RODAPE = "Integração Mercado Livre · AgenteIA"
AZUL = colors.HexColor("#1f4e79")

base = getSampleStyleSheet()
EST = {
    "titulo": ParagraphStyle("titulo", parent=base["Title"], fontSize=22, textColor=AZUL,
                             alignment=TA_CENTER, spaceAfter=10),
    "h2": ParagraphStyle("h2", parent=base["Heading2"], textColor=AZUL, fontSize=14,
                         spaceBefore=12, spaceAfter=6),
    "h3": ParagraphStyle("h3", parent=base["Heading3"], textColor=AZUL, fontSize=11.5,
                         spaceBefore=8, spaceAfter=4),
    "p": ParagraphStyle("p", parent=base["BodyText"], fontSize=9.5, leading=13, spaceAfter=5),
    "li": ParagraphStyle("li", parent=base["BodyText"], fontSize=9.5, leading=13,
                         leftIndent=14, bulletIndent=4, spaceAfter=2),
    "nota": ParagraphStyle("nota", parent=base["BodyText"], fontSize=9.5, leading=13,
                           backColor=colors.HexColor("#fff4e5"), borderPadding=6,
                           borderColor=colors.HexColor("#f0a030"), borderWidth=0.5,
                           spaceBefore=6, spaceAfter=10),
    "cel": ParagraphStyle("cel", parent=base["BodyText"], fontSize=8, leading=10),
    "celh": ParagraphStyle("celh", parent=base["BodyText"], fontSize=8, leading=10,
                           textColor=colors.white, fontName="Helvetica-Bold"),
    "code": ParagraphStyle("code", parent=base["Code"], fontSize=7.5, leading=9.5,
                           backColor=colors.HexColor("#f2f2f2"), borderPadding=6,
                           spaceBefore=4, spaceAfter=8),
}


def inline(txt):
    """Markdown inline -> marcacao do reportlab (trechos em `codigo` ficam literais)."""
    partes = txt.replace("⋮", "...").split("`")
    out = []
    for i, parte in enumerate(partes):
        parte = html.escape(parte, quote=False)
        if i % 2:
            out.append(f'<font face="Courier">{parte}</font>')
            continue
        parte = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", parte)
        parte = re.sub(r"(?<![\w*])\*([^*]+)\*(?![\w*])", r"<i>\1</i>", parte)
        parte = re.sub(r"(https?://[^\s<)]+)", r'<link href="\1" color="#1f4e79">\1</link>', parte)
        out.append(parte)
    return "".join(out)


def tabela(linhas, largura):
    cel = [[c.strip() for c in l.strip().strip("|").split("|")] for l in linhas]
    cel = [cel[0]] + cel[2:]  # remove a linha separadora |---|
    dados = [[Paragraph(inline(c), EST["celh" if i == 0 else "cel"]) for c in lin]
             for i, lin in enumerate(cel)]
    n = len(cel[0])
    pesos = [max(len(lin[j]) if j < len(lin) else 0 for lin in cel) + 6 for j in range(n)]
    larg = [largura * p / sum(pesos) for p in pesos]
    t = Table(dados, colWidths=larg, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b0b7c3")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f8fc")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return [t, Spacer(1, 8)]


def converter(md, largura):
    hist, linhas, i = [], md.splitlines(), 0
    while i < len(linhas):
        l = linhas[i]
        s = l.strip()
        if s.startswith("```"):
            bloco, i = [], i + 1
            while not linhas[i].strip().startswith("```"):
                bloco.append(linhas[i].rstrip()[len(l) - len(l.lstrip()):] if linhas[i].strip() else "")
                i += 1
            hist.append(Preformatted("\n".join(bloco), EST["code"], maxLineLength=110))
        elif s.startswith("# "):
            hist.append(Paragraph(inline(s[2:]), EST["titulo"]))
        elif s.startswith("## "):
            hist.append(Paragraph(inline(s[3:]), EST["h2"]))
        elif s.startswith("### "):
            hist.append(Paragraph(inline(s[4:]), EST["h3"]))
        elif s.startswith("|"):
            bloco = []
            while i < len(linhas) and linhas[i].strip().startswith("|"):
                bloco.append(linhas[i]); i += 1
            hist.extend(tabela(bloco, largura)); continue
        elif s.startswith(">"):
            bloco = []
            while i < len(linhas) and linhas[i].strip().startswith(">"):
                bloco.append(linhas[i].strip().lstrip(">").strip()); i += 1
            hist.append(Paragraph(inline(" ".join(bloco)), EST["nota"])); continue
        elif re.match(r"^(- |\d+\. )", s):
            marca = "•" if s.startswith("- ") else s.split(".")[0] + "."
            texto = re.sub(r"^(- |\d+\. )", "", s)
            ind = len(l) - len(l.lstrip())
            i += 1
            # continuacao da linha do item (texto recuado sem marcador)
            while (i < len(linhas) and linhas[i].strip() and not re.match(r"^\s*(- |\d+\. |\||```|#)", linhas[i])
                   and len(linhas[i]) - len(linhas[i].lstrip()) > ind):
                texto += " " + linhas[i].strip(); i += 1
            est = ParagraphStyle("li2", parent=EST["li"], leftIndent=14 + ind * 4, bulletIndent=4 + ind * 4)
            hist.append(Paragraph(inline(texto), est, bulletText=marca)); continue
        elif s:
            bloco = [s]; i += 1
            while (i < len(linhas) and linhas[i].strip()
                   and not re.match(r"^\s*(- |\d+\. |\||```|#|>)", linhas[i])):
                bloco.append(linhas[i].strip()); i += 1
            hist.append(Paragraph(inline(" ".join(bloco)), EST["p"])); continue
        i += 1
    return hist


def rodape(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(2 * cm, 1.2 * cm, RODAPE)
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Página {doc.page}")
    canvas.restoreState()


def main():
    doc = SimpleDocTemplate(DESTINO, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.8 * cm, bottomMargin=2 * cm,
                            title="Integração Mercado Livre", author="AgenteIA")
    with open(ORIGEM, encoding="utf-8") as f:
        hist = converter(f.read(), doc.width)
    doc.build(hist, onFirstPage=rodape, onLaterPages=rodape)
    print(f"Gerado: {DESTINO}")


if __name__ == "__main__":
    main()
