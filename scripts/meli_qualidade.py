#!/usr/bin/env python3
"""Checagens de qualidade de anuncios do Mercado Livre.

Aplica as regras de docs/Boas_Praticas_Anuncio_ML.md. Usado pelas acoes
validar_anuncio/publicar_anuncio (meli_anuncio.py) e previa_edicao/editar_anuncio
(meli_editar_anuncio.py). Nao chama a API: recebe os dados prontos.

Cada checagem devolve itens (nivel, mensagem), com nivel:
  BLOQUEIA = impede publicar/editar (viola regra do Mercado Livre)
  ALERTA   = reduz exposicao ou conversao; corrigir antes de publicar
  DICA     = melhoria opcional
"""
import os
import re
import unicodedata

TITULO_MAX = 60
TITULO_MIN_RECOMENDADO = 35
FOTOS_RECOMENDADAS = 6
FOTO_LADO_MIN = 500
FOTO_LADO_IDEAL = 1200
DESCRICAO_MIN_RECOMENDADA = 300

# Termos que o Mercado Livre nao aceita ou que nao ajudam na busca.
TERMOS_PROIBIDOS_TITULO = [
    "promocao", "promo", "oferta", "desconto", "liquidacao", "queima de estoque",
    "frete gratis", "envio gratis", "frete gratuito", "imperdivel", "barato", "baratissimo",
    "melhor preco", "menor preco", "pronta entrega", "envio imediato", "envio rapido",
    "novo", "nova", "lancamento", "garantia", "parcelado", "sem juros",
    "mais vendido", "black friday",
]
PALAVRAS_LIGACAO = {"de", "da", "do", "das", "dos", "e", "com", "para", "p", "em", "a", "o",
                    "as", "os", "sem", "por", "x", "-", "+", "/"}

RE_LINK = re.compile(r"(https?://|www\.|\b[\w-]+\.(com|net|org)(\.br)?\b)", re.I)
RE_EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b")
RE_TELEFONE = re.compile(r"(\(?\b\d{2}\)?\s?)?\b9?\d{4}[-\s.]?\d{4}\b")
RE_HTML = re.compile(r"<[a-z/][^>]*>", re.I)
TERMOS_CONTATO = ["whatsapp", "whats", "zap", "instagram", "insta", "facebook", "telegram",
                  "ligue", "telefone", "celular para contato", "fora do mercado livre",
                  "compre direto", "nosso site", "e-mail"]

# Atributos que nao sao preenchidos pelo vendedor ou nao aparecem no anuncio.
TAGS_IGNORADAS = {"hidden", "read_only", "fixed", "inferred", "others", "variation_attribute"}


def _sem_acento(txt):
    return "".join(c for c in unicodedata.normalize("NFD", txt.lower())
                   if unicodedata.category(c) != "Mn")


def checar_titulo(titulo):
    itens = []
    if not titulo:
        return [("BLOQUEIA", "titulo vazio")]
    n = len(titulo)
    if n > TITULO_MAX:
        itens.append(("BLOQUEIA", f"titulo com {n} caracteres (maximo {TITULO_MAX})"))
    elif n < TITULO_MIN_RECOMENDADO:
        itens.append(("DICA", f"titulo com {n} caracteres; use ate {TITULO_MAX} com marca, modelo "
                              f"e caracteristica principal para aparecer em mais buscas"))
    base = f" {_sem_acento(titulo)} "
    for termo in TERMOS_PROIBIDOS_TITULO:
        if re.search(rf"(?<![\w]){re.escape(termo)}(?![\w])", base):
            itens.append(("ALERTA", f'titulo contem "{termo}": nao use condicao, preco, frete, '
                                    f"garantia ou termos promocionais no titulo"))
    palavras = [p for p in re.findall(r"[\w]+", _sem_acento(titulo)) if p not in PALAVRAS_LIGACAO]
    repetidas = sorted({p for p in palavras if palavras.count(p) > 1 and len(p) > 2})
    if repetidas:
        itens.append(("ALERTA", f"palavras repetidas no titulo: {', '.join(repetidas)}"))
    letras = [c for c in titulo if c.isalpha()]
    if letras and sum(c.isupper() for c in letras) / len(letras) > 0.6:
        itens.append(("ALERTA", "titulo em CAIXA ALTA; use apenas iniciais maiusculas"))
    if re.search(r"[!*$%#@?]|\.{2,}", titulo):
        itens.append(("ALERTA", "titulo com simbolos (! * $ % # @ ? ...); use so letras, numeros e medidas"))
    return itens


def checar_descricao(texto):
    itens = []
    if not texto or not texto.strip():
        return [("ALERTA", "sem descricao; descreva beneficios, medidas, material, conteudo da "
                           "embalagem e cuidados")]
    if RE_LINK.search(texto):
        itens.append(("BLOQUEIA", "descricao com link ou endereco de site"))
    if RE_EMAIL.search(texto):
        itens.append(("BLOQUEIA", "descricao com e-mail"))
    if RE_TELEFONE.search(re.sub(r"\d+[.,]?\d*\s?(cm|mm|m|kg|g|ml|l|w|v|un|unidades|pecas)\b", "",
                                 _sem_acento(texto))):
        itens.append(("ALERTA", "descricao parece ter numero de telefone; confira"))
    base = _sem_acento(texto)
    for termo in TERMOS_CONTATO:
        if re.search(rf"(?<![\w]){re.escape(termo)}(?![\w])", base):
            itens.append(("BLOQUEIA", f'descricao menciona "{termo}": contato fora do Mercado Livre '
                                      f"nao e permitido"))
    if RE_HTML.search(texto):
        itens.append(("ALERTA", "descricao com HTML; o Mercado Livre aceita so texto simples"))
    if len(texto) < DESCRICAO_MIN_RECOMENDADA:
        itens.append(("DICA", f"descricao curta ({len(texto)} caracteres); detalhe uso, medidas, "
                              f"material e o que vem na embalagem"))
    return itens


def _dimensoes(caminho):
    try:
        from PIL import Image
    except ImportError:
        return None
    try:
        with Image.open(caminho) as im:
            return im.size, im.format
    except Exception:
        return None


def checar_fotos(fotos):
    itens = []
    n = len(fotos or [])
    if n == 0:
        return [("BLOQUEIA", "anuncio sem fotos")]
    if n < FOTOS_RECOMENDADAS:
        itens.append(("ALERTA", f"{n} foto(s); use pelo menos {FOTOS_RECOMENDADAS} (principal com "
                                f"fundo branco, detalhes, medidas, uso, embalagem)"))
    for i, foto in enumerate(fotos):
        if foto.startswith(("http://", "https://")):
            if foto.lower().split("?")[0].endswith(".webp"):
                itens.append(("BLOQUEIA", f"foto {i + 1} em WebP; use JPG ou PNG"))
            continue
        if not os.path.exists(foto):
            continue
        info = _dimensoes(foto)
        if not info:
            continue
        (larg, alt), formato = info
        if formato not in ("JPEG", "PNG"):
            itens.append(("BLOQUEIA", f"foto {i + 1} ({foto}) em {formato}; use JPG ou PNG"))
        lado = max(larg, alt)
        if lado < FOTO_LADO_MIN:
            itens.append(("BLOQUEIA", f"foto {i + 1} ({foto}) com {larg}x{alt} px; minimo "
                                      f"{FOTO_LADO_MIN} px no maior lado"))
        elif lado < FOTO_LADO_IDEAL:
            itens.append(("DICA", f"foto {i + 1} ({foto}) com {larg}x{alt} px; {FOTO_LADO_IDEAL} px "
                                  f"ou mais ativa o zoom"))
    return itens


def atributos_relevantes(attrs_categoria):
    """Atributos da categoria que o vendedor deve preencher."""
    out = []
    for a in attrs_categoria or []:
        tags = a.get("tags") or {}
        if any(tags.get(t) for t in TAGS_IGNORADAS):
            continue
        out.append(a)
    return out


def checar_atributos(attributes, attrs_categoria):
    """Devolve (itens, percentual preenchido)."""
    if attrs_categoria is None:
        return [("ALERTA", "nao consegui ler a ficha tecnica da categoria")], None
    relevantes = atributos_relevantes(attrs_categoria)
    preenchidos = {a.get("id") for a in attributes or []
                   if a.get("value_name") or a.get("value_id") or a.get("values")}
    itens = []
    obrig = [a for a in relevantes if (a.get("tags") or {}).get("required")
             or (a.get("tags") or {}).get("catalog_required")]
    for a in obrig:
        if a["id"] not in preenchidos:
            itens.append(("BLOQUEIA", f"atributo obrigatorio faltando: {a['id']} ({a.get('name')})"))
    if not relevantes:
        return itens, 100
    feitos = sum(1 for a in relevantes if a["id"] in preenchidos)
    pct = round(100 * feitos / len(relevantes))
    if pct < 100:
        faltam = [f"{a['id']} ({a.get('name')})" for a in relevantes
                  if a["id"] not in preenchidos and a not in obrig]
        nivel = "ALERTA" if pct < 80 else "DICA"
        itens.append((nivel, f"ficha tecnica {pct}% preenchida ({feitos}/{len(relevantes)}); "
                             f"faltam: {', '.join(faltam[:15])}" + (" ..." if len(faltam) > 15 else "")))
    return itens, pct


def nota(titulo_itens, desc_itens, fotos, pct_atributos):
    """Nota 0-100: titulo 25, ficha tecnica 35, fotos 25, descricao 15."""
    def pts(itens, peso):
        if any(n == "BLOQUEIA" for n, _ in itens):
            return 0
        perda = sum(0.3 if n == "ALERTA" else 0.1 for n, _ in itens)
        return peso * max(0.0, 1 - perda)
    total = pts(titulo_itens, 25) + pts(desc_itens, 15)
    total += 35 * (pct_atributos or 0) / 100
    total += 25 * min(len(fotos or []), FOTOS_RECOMENDADAS) / FOTOS_RECOMENDADAS
    return round(total)


def avaliar(anuncio, attrs_categoria):
    """Avalia um anuncio completo (formato de anuncios/*.json).

    Devolve dict com nota, itens [(nivel, mensagem)] e se ha bloqueio.
    """
    t = checar_titulo(anuncio.get("title", ""))
    d = checar_descricao(anuncio.get("descricao", ""))
    f = checar_fotos(anuncio.get("fotos", []))
    a, pct = checar_atributos(anuncio.get("attributes", []), attrs_categoria)
    itens = t + a + f + d
    return {"nota": nota(t, d, anuncio.get("fotos", []), pct),
            "ficha_tecnica_pct": pct,
            "itens": itens,
            "bloqueia": any(n == "BLOQUEIA" for n, _ in itens)}


def imprimir(avaliacao):
    print(f"Qualidade: {avaliacao['nota']}/100"
          + (f" (ficha tecnica {avaliacao['ficha_tecnica_pct']}%)"
             if avaliacao.get("ficha_tecnica_pct") is not None else ""))
    ordem = {"BLOQUEIA": 0, "ALERTA": 1, "DICA": 2}
    for nivel, msg in sorted(avaliacao["itens"], key=lambda x: ordem[x[0]]):
        print(f"  [{nivel}] {msg}")
    if not avaliacao["itens"]:
        print("  Nenhum problema encontrado")
