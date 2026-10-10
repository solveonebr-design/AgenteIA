#!/usr/bin/env python3
"""Edita um anuncio ja publicado no Mercado Livre a partir de um arquivo JSON.

Uso:
  python3 meli_editar_anuncio.py previa anuncios/edicoes/<nome>.json <pasta_saida>
  python3 meli_editar_anuncio.py aplicar anuncios/edicoes/<nome>.json <pasta_saida>

previa  = le o anuncio atual e mostra "antes -> depois" de cada
          campo, apontando o que o Mercado Livre nao deixa mudar. Nao altera nada.
aplicar = faz a mesma checagem, salva a copia do estado atual e aplica com
          PUT /items/{id} (e PUT /items/{id}/description se houver descricao).

Formato do arquivo: ver anuncios/edicoes/_modelo.json. O anuncio e indicado por
"item_id" (ex.: MLB1234567890) ou por "anuncio" (nome do arquivo usado na
publicacao; o ID e lido de data/meli_anuncio_<anuncio>_publicar.json).

Le MELI_ACCESS_TOKEN do ambiente. Nao renova o token (so o workflow renova).
"""
import json
import os
import sys
import time

from meli_anuncio import chamar, enviar_foto

# Campos que o PUT /items aceita alterar. title e condition so sem vendas.
PERMITIDOS = {"title", "price", "available_quantity", "status", "attributes", "shipping",
              "sale_terms", "condition", "video_id"}
SO_SEM_VENDAS = {"title", "condition"}
STATUS = {"active", "paused", "closed"}


def item_id(edicao, raiz_dados):
    if edicao.get("item_id"):
        return edicao["item_id"]
    nome = edicao.get("anuncio")
    if not nome:
        sys.exit('Informe "item_id" ou "anuncio" no arquivo de edicao')
    caminho = os.path.join(raiz_dados, f"meli_anuncio_{nome}_publicar.json")
    if not os.path.exists(caminho):
        sys.exit(f"Nao achei {caminho}; informe o item_id diretamente")
    with open(caminho, encoding="utf-8") as f:
        iid = json.load(f).get("id")
    if not iid:
        sys.exit(f"{caminho} nao tem o ID do anuncio (a publicacao falhou?)")
    return iid


def resumo_atributos(lista):
    return {a.get("id"): a.get("value_name") or a.get("value_id") for a in lista or []}


def comparar(atual, alteracoes):
    """Devolve (linhas de diferenca, problemas que impedem a edicao)."""
    linhas, problemas = [], []
    vendidos = atual.get("sold_quantity") or 0
    for campo, novo in alteracoes.items():
        if campo not in PERMITIDOS:
            problemas.append(f"{campo}: campo nao editavel por esta acao")
            continue
        if campo in SO_SEM_VENDAS and vendidos > 0:
            problemas.append(f"{campo}: o anuncio ja tem {vendidos} venda(s) e o Mercado Livre "
                             f"nao permite mudar este campo")
            continue
        if campo == "status" and novo not in STATUS:
            problemas.append(f"status: use active, paused ou closed (recebi {novo})")
            continue
        if campo == "status" and novo == "closed":
            linhas.append("status: ATENCAO, closed finaliza o anuncio e nao da para reativar")
        if campo == "attributes":
            antes = resumo_atributos(atual.get("attributes"))
            for aid, valor in resumo_atributos(novo).items():
                if antes.get(aid) != valor:
                    linhas.append(f"atributo {aid}: {antes.get(aid)!r} -> {valor!r}")
            continue
        antes = atual.get(campo)
        if antes != novo:
            linhas.append(f"{campo}: {antes!r} -> {novo!r}")
    return linhas, problemas


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("previa", "aplicar"):
        sys.exit(__doc__)
    modo, arquivo = sys.argv[1], sys.argv[2]
    saida = sys.argv[3] if len(sys.argv) > 3 else "."
    if os.path.basename(arquivo).startswith("_"):
        sys.exit("Arquivos que comecam com _ sao modelos e nao podem ser usados.")
    with open(arquivo, encoding="utf-8") as f:
        edicao = json.load(f)
    nome = os.path.splitext(os.path.basename(arquivo))[0]
    iid = item_id(edicao, saida)

    codigo, atual = chamar("GET", f"/items/{iid}")
    if codigo != 200:
        sys.exit(f"Nao consegui ler o anuncio {iid}: HTTP {codigo} {atual.get('message', '')}")
    print(f"Anuncio {iid}: {atual.get('title')} ({atual.get('status')}, "
          f"{atual.get('sold_quantity') or 0} vendas) {atual.get('permalink')}")

    alteracoes = dict(edicao.get("alteracoes") or {})
    linhas, problemas = comparar(atual, alteracoes)
    if "title" in alteracoes and len(alteracoes["title"]) > 60:
        problemas.append(f"title com {len(alteracoes['title'])} caracteres (maximo 60)")
    if edicao.get("fotos"):
        linhas.append(f"fotos: {len(atual.get('pictures') or [])} atuais -> "
                      f"{len(edicao['fotos'])} novas (substitui todas)")
    if edicao.get("descricao"):
        linhas.append("descricao: sera substituida")
    if not linhas and not problemas:
        problemas.append("nenhuma alteracao em relacao ao anuncio atual")

    print("Alteracoes:" if linhas else "Alteracoes: nenhuma")
    for l in linhas:
        print("  " + l)
    for p in problemas:
        print("Problema: " + p)

    os.makedirs(saida, exist_ok=True)
    copia = None
    if modo == "aplicar":
        # Copia do estado atual, para poder desfazer.
        carimbo = time.strftime("%Y%m%d_%H%M%S", time.gmtime())
        copia = os.path.join(saida, f"meli_edicao_{nome}_antes_{carimbo}.json")
        with open(copia, "w", encoding="utf-8") as f:
            json.dump({k: atual.get(k) for k in ("id", "title", "price", "available_quantity", "status",
                                                 "condition", "attributes", "shipping", "sale_terms",
                                                 "pictures", "permalink", "sold_quantity")},
                      f, ensure_ascii=False, indent=2)

    resultado = {"arquivo": arquivo, "modo": modo, "item_id": iid, "alteracoes": linhas,
                 "problemas": problemas, "copia_antes": copia,
                 "data": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())}

    if modo == "aplicar" and not problemas:
        corpo = alteracoes
        if edicao.get("fotos"):
            fotos = []
            for foto in edicao["fotos"]:
                if foto.startswith(("http://", "https://")):
                    fotos.append({"source": foto})
                elif os.path.exists(foto):
                    fotos.append({"id": enviar_foto(foto)})
                else:
                    sys.exit(f"Foto nao encontrada no repositorio: {foto}")
            corpo["pictures"] = fotos
        if corpo:
            codigo, resp = chamar("PUT", f"/items/{iid}", corpo)
            resultado["aplicado"] = codigo == 200
            if codigo != 200:
                causas = [c.get("message") for c in resp.get("cause", [])] or [resp.get("message")]
                resultado["erro"] = causas
                print(f"Falha ao editar: HTTP {codigo} " + "; ".join(str(c) for c in causas))
            else:
                print(f"Editado: {resp.get('id')} ({resp.get('status')}) preco {resp.get('price')} "
                      f"estoque {resp.get('available_quantity')}")
        if edicao.get("descricao") and resultado.get("aplicado", True):
            cd, rd = chamar("PUT", f"/items/{iid}/description", {"plain_text": edicao["descricao"]})
            resultado["descricao_ok"] = cd in (200, 201)
            if cd not in (200, 201):
                print(f"Aviso: descricao nao gravada (HTTP {cd} {rd.get('message', '')})")
            resultado.setdefault("aplicado", resultado["descricao_ok"])

    destino = os.path.join(saida, f"meli_edicao_{nome}_{modo}.json")
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    if copia:
        print(f"Copia do estado anterior: {copia}")
    print(f"Resultado salvo em {destino}")
    if problemas or (modo == "aplicar" and not resultado.get("aplicado")):
        sys.exit(1)


if __name__ == "__main__":
    main()
