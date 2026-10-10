#!/usr/bin/env python3
"""Valida ou publica um anuncio no Mercado Livre a partir de um arquivo JSON.

Uso:
  python3 meli_anuncio.py validar  anuncios/<nome>.json <pasta_saida>
  python3 meli_anuncio.py publicar anuncios/<nome>.json <pasta_saida>

validar  = checagens de qualidade (meli_qualidade.py: titulo, ficha tecnica, fotos,
           descricao) e POST /items/validate (nao publica nada).
publicar = valida de novo e, se estiver valido, cria o anuncio (POST /items) e a
           descricao (POST /items/{id}/description).

Formato do arquivo: ver anuncios/_modelo.json. Fotos podem ser URLs publicas ou
caminhos de arquivos do repositorio (ex.: fotos/sv0011_verde_1.jpg), que sao
enviados com POST /pictures/items/upload.

Le MELI_ACCESS_TOKEN do ambiente. Nao renova o token (so o workflow renova).
"""
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request
import uuid

import meli_qualidade

API = "https://api.mercadolibre.com"
TOKEN = os.environ.get("MELI_ACCESS_TOKEN", "").strip()
if not TOKEN:
    sys.exit("Variavel de ambiente ausente: MELI_ACCESS_TOKEN")

# Campos do arquivo que nao vao no corpo do POST /items.
CAMPOS_LOCAIS = {"descricao", "fotos", "_comentario"}


def chamar(metodo, caminho, corpo=None, cabecalhos=None, tentativas=6):
    """Devolve (codigo HTTP, resposta). Nova tentativa em 429/5xx."""
    dados = None
    cab = {"Authorization": f"Bearer {TOKEN}"}
    if isinstance(corpo, (dict, list)):
        dados = json.dumps(corpo).encode()
        cab["Content-Type"] = "application/json"
    elif corpo is not None:
        dados = corpo
    cab.update(cabecalhos or {})
    req = urllib.request.Request(API + caminho, data=dados, headers=cab, method=metodo)
    for i in range(tentativas):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                txt = r.read().decode()
                return r.status, json.loads(txt) if txt else {}
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and i < tentativas - 1:
                time.sleep(2 ** i)
                continue
            txt = e.read().decode(errors="replace")
            try:
                return e.code, json.loads(txt)
            except ValueError:
                return e.code, {"message": txt[:500]}


def enviar_foto(caminho):
    """Upload de arquivo local; devolve o id da foto no Mercado Livre."""
    limite = "----meli" + uuid.uuid4().hex
    tipo = mimetypes.guess_type(caminho)[0] or "image/jpeg"
    with open(caminho, "rb") as f:
        conteudo = f.read()
    corpo = (f"--{limite}\r\nContent-Disposition: form-data; name=\"file\"; "
             f"filename=\"{os.path.basename(caminho)}\"\r\nContent-Type: {tipo}\r\n\r\n").encode()
    corpo += conteudo + f"\r\n--{limite}--\r\n".encode()
    codigo, resp = chamar("POST", "/pictures/items/upload", corpo,
                          {"Content-Type": f"multipart/form-data; boundary={limite}"})
    if codigo not in (200, 201) or "id" not in resp:
        sys.exit(f"Falha ao enviar a foto {caminho}: HTTP {codigo} {resp.get('message', '')}")
    return resp["id"]


def montar_corpo(anuncio):
    corpo = {k: v for k, v in anuncio.items() if k not in CAMPOS_LOCAIS}
    fotos = []
    for foto in anuncio.get("fotos", []):
        if foto.startswith(("http://", "https://")):
            fotos.append({"source": foto})
        elif not os.path.exists(foto):
            sys.exit(f"Foto nao encontrada no repositorio: {foto}")
        else:
            # O upload so guarda a imagem no Mercado Livre; nao publica nada.
            fotos.append({"id": enviar_foto(foto)})
    if fotos:
        corpo["pictures"] = fotos
    return corpo


def atributos_categoria(categoria):
    """Ficha tecnica da categoria (GET /categories/{id}/attributes) ou None."""
    if not categoria:
        return None
    codigo, attrs = chamar("GET", f"/categories/{categoria}/attributes")
    return attrs if codigo == 200 else None


def validar(corpo):
    codigo, resp = chamar("POST", "/items/validate", corpo)
    if codigo == 204:
        return True, []
    erros = [f"[{c.get('type', 'erro')}] {c.get('code', '')}: {c.get('message', '')}"
             for c in resp.get("cause", [])]
    return False, erros or [f"HTTP {codigo}: {resp.get('message', resp)}"]


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("validar", "publicar"):
        sys.exit(__doc__)
    modo, arquivo = sys.argv[1], sys.argv[2]
    saida = sys.argv[3] if len(sys.argv) > 3 else "."
    if os.path.basename(arquivo).startswith("_"):
        sys.exit("Arquivos que comecam com _ sao modelos e nao podem ser usados.")
    with open(arquivo, encoding="utf-8") as f:
        anuncio = json.load(f)
    nome = os.path.splitext(os.path.basename(arquivo))[0]
    resultado = {"arquivo": arquivo, "modo": modo,
                 "data": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())}

    titulo = anuncio.get("title", "")
    print(f"Titulo ({len(titulo)}/60): {titulo}")
    if not anuncio.get("category_id"):
        sys.exit("Informe category_id (categoria) no arquivo do anuncio")

    # Checagens de qualidade (docs/Boas_Praticas_Anuncio_ML.md), antes de enviar fotos.
    avaliacao = meli_qualidade.avaliar(anuncio, atributos_categoria(anuncio["category_id"]))
    meli_qualidade.imprimir(avaliacao)
    resultado["qualidade"] = {"nota": avaliacao["nota"],
                              "ficha_tecnica_pct": avaliacao["ficha_tecnica_pct"],
                              "itens": [f"[{n}] {m}" for n, m in avaliacao["itens"]]}

    corpo = montar_corpo(anuncio)
    ok, erros = validar(corpo)
    resultado["valido"] = ok
    resultado["erros_validacao"] = erros
    print("Validacao: VALIDO" if ok else "Validacao: INVALIDO")
    for e in erros:
        print("  " + e)

    if avaliacao["bloqueia"]:
        print("Bloqueado pelas checagens de qualidade (itens [BLOQUEIA] acima)")
        ok = False
        resultado["valido"] = False

    if modo == "publicar":
        if not ok:
            resultado["publicado"] = False
        else:
            codigo, item = chamar("POST", "/items", corpo)
            if codigo not in (200, 201):
                resultado["publicado"] = False
                resultado["erro_publicacao"] = item
                print(f"Falha ao publicar: HTTP {codigo} {item.get('message', '')}")
            else:
                resultado.update({"publicado": True, "id": item.get("id"),
                                  "status": item.get("status"), "link": item.get("permalink")})
                print(f"Publicado: {item.get('id')} ({item.get('status')}) {item.get('permalink')}")
                if anuncio.get("descricao"):
                    cd, rd = chamar("POST", f"/items/{item['id']}/description",
                                    {"plain_text": anuncio["descricao"]})
                    resultado["descricao_ok"] = cd in (200, 201)
                    if cd not in (200, 201):
                        print(f"Aviso: descricao nao gravada (HTTP {cd} {rd.get('message', '')})")

    os.makedirs(saida, exist_ok=True)
    destino = os.path.join(saida, f"meli_anuncio_{nome}_{modo}.json")
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    print(f"Resultado salvo em {destino}")
    if not ok or (modo == "publicar" and not resultado.get("publicado")):
        sys.exit(1)


if __name__ == "__main__":
    main()
