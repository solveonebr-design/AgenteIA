#!/usr/bin/env python3
"""Conteudo otimizado dos anuncios avulsos (sem variacoes novas).

Uso:
  python3 scripts/conteudo_lote1.py preview   # valida, nao grava
  python3 scripts/conteudo_lote1.py aplicar   # grava na Amazon
"""
import sys

import listar_produtos as lp
import variacoes_sv0011 as v

NV12_TITLE = ("Mini Processador de Alimentos Manual com Puxador, Triturador e Picador 500 ml com 3 Lâminas em Aço "
              "Inox, para Alho, Cebola, Temperos e Legumes")
NV12 = {
    "bullets": [
        "3 LÂMINAS EM AÇO INOX: lâminas afiadas que picam e trituram alho, cebola, ervas, legumes, frutas e "
        "castanhas em poucos movimentos.",
        "MANUAL, SEM ENERGIA: basta puxar a cordinha da tampa para girar as lâminas. Não precisa de tomada nem "
        "pilha e pode ser usado em qualquer lugar.",
        "TIGELA TRANSPARENTE DE 500 ML: permite acompanhar o ponto do corte e preparar porções de temperos, "
        "molhos, vinagretes e saladas.",
        "COMPACTO: mede cerca de 13 x 13 x 9 cm e pesa 251 g, ocupando pouco espaço na bancada e no armário.",
        "FÁCIL DE LIMPAR: desmonta em poucas peças. Lave à mão, sem esponja abrasiva, e manuseie as lâminas com "
        "cuidado.",
    ],
    "description": (
        "Mini processador manual que agiliza o preparo do dia a dia: coloque os alimentos na tigela, tampe e "
        "puxe a cordinha algumas vezes. Quanto mais puxadas, mais fino fica o corte.\n\n"
        "As 3 lâminas em aço inoxidável picam alho, cebola, ervas, legumes, frutas e castanhas, e a tigela "
        "transparente de 500 ml permite acompanhar o ponto. Por ser manual, não precisa de energia elétrica.\n\n"
        "Especificações:\n"
        "- Capacidade: 500 ml\n"
        "- Lâminas: 3, em aço inoxidável\n"
        "- Material: plástico ABS e aço inoxidável\n"
        "- Medidas: 13 x 13 x 9 cm\n"
        "- Peso: 251 g\n\n"
        "Cuidados: lavar à mão, não usar lava-louças nem esponjas abrasivas, secar bem antes de guardar.\n\n"
        "Conteúdo da embalagem: 1 tigela transparente, 1 tampa com puxador, 1 conjunto de lâminas e 1 eixo central."
    ),
    "keywords": ("cortador salsinha cebolinha nozes castanhas salada molho vinagrete guacamole tritura pica corta "
                 "cozinha utensílio prático rápido"),
    "features": ["Manual", "3 lâminas em aço inox", "Tigela transparente", "Compacto"],
}

ITEMS = {
    "0001_FBA": {
        "title": ("Kit Limpador de Ouvido 7 Peças: 6 Ferramentas em Aço Inox e Estojo, Removedor de Cera "
                  "Reutilizável para Higiene Pessoal, Compacto para Viagem"),
        "bullets": [
            "KIT COM 7 PEÇAS: 6 ferramentas com pontas em formatos variados para a higiene da parte externa do "
            "ouvido, mais 1 estojo.",
            "AÇO INOXIDÁVEL REUTILIZÁVEL: peças metálicas que podem ser higienizadas e usadas novamente, uma "
            "alternativa às hastes descartáveis.",
            "ESTOJO ORGANIZADOR: mantém as 6 ferramentas reunidas e protegidas, facilitando guardar em casa ou levar "
            "na bolsa e na mala.",
            "COMPACTO E LEVE: o kit pesa cerca de 30 g e cabe em qualquer nécessaire, ideal para viagens.",
            "USE COM CUIDADO: faça movimentos suaves apenas na entrada do canal auditivo e higienize as peças com "
            "álcool após cada uso. Em caso de dor ou desconforto, procure um médico.",
        ],
        "description": (
            "Kit com 7 peças: 6 ferramentas em aço inoxidável para a higiene da parte externa do ouvido e 1 estojo "
            "organizador.\n\n"
            "As pontas em formatos variados atendem a diferentes necessidades, e o material metálico permite "
            "higienizar e reutilizar as peças. O estojo mantém tudo reunido e protegido, o que facilita guardar "
            "e transportar.\n\n"
            "Modo de uso: utilize com movimentos suaves apenas na entrada do canal auditivo. Não introduza as "
            "peças profundamente. Higienize com álcool antes e depois do uso. Mantenha fora do alcance de "
            "crianças.\n\n"
            "Conteúdo da embalagem: 6 ferramentas em aço inox e 1 estojo."
        ),
        "keywords": ("cureta auricular cerume orelha higienização limpeza auditiva espiral ferramenta "
                     "nécessaire cuidados"),
    },
    "0003_FBA": {
        "title": ("Kit 24 Canetas Marcadoras Permanentes Ponta Dupla Coloridas com Estojo, Marcador Artístico "
                  "para Desenho, Lettering, Mangá, Artesanato e Escola"),
        "bullets": [
            "24 CORES: kit com 24 canetas em cores variadas para desenhos, ilustrações, lettering e trabalhos "
            "criativos.",
            "PONTA DUPLA: cada caneta tem duas pontas, uma para traços finos e detalhes e outra para preencher "
            "áreas maiores.",
            "TINTA PERMANENTE: marcadores permanentes para desenhos e marcações duradouras em papel.",
            "ESTOJO ORGANIZADOR: as 24 canetas ficam organizadas no estojo, o que facilita guardar, transportar e "
            "encontrar cada cor.",
            "PARA TODAS AS IDADES: ideal para estudantes, artistas e iniciantes em desenho, mangá, bullet journal, "
            "artesanato e trabalhos escolares.",
        ],
        "description": (
            "Kit com 24 canetas marcadoras permanentes de ponta dupla, para quem gosta de desenhar, colorir e "
            "criar.\n\n"
            "Cada caneta tem uma ponta para traços finos e outra para preenchimento, permitindo alternar entre "
            "contornos, detalhes e áreas maiores com a mesma cor. A variedade de 24 cores ajuda a combinar tons e "
            "destacar detalhes.\n\n"
            "Ideal para desenho, ilustração, lettering, mangá, bullet journal, artesanato e trabalhos escolares.\n\n"
            "Importante: as imagens mostram canetas com corpo branco e com corpo preto. O kit enviado tem as canetas "
            "com corpo preto, com tinta nas 24 cores.\n\n"
            "Conteúdo da embalagem: 24 canetas de ponta dupla com corpo preto e 1 estojo organizador."
        ),
        "keywords": ("marcadores pincel colorir ilustração caderno bullet journal sketch arte presente papelaria "
                     "material escolar estudante"),
        "features": ["Ponta dupla", "24 cores", "Estojo organizador"],
    },
    "SV_0006_FBA": {
        "title": ("Baralho Dourado Resistente à Água e Anti-Rasgo com 54 Cartas, Estilo Nota de Dólar, para Poker, "
                  "Truco, Buraco e Jogos de Cartas"),
        "bullets": [
            "VISUAL DOURADO ESTILO DÓLAR: cartas com acabamento dourado e arte inspirada em cédulas de dólar, que "
            "chamam a atenção na mesa.",
            "RESISTENTE À ÁGUA: suporta respingos e umidade e é fácil de limpar com um pano, ideal para jogar na "
            "piscina, na praia ou em festas.",
            "ANTI-RASGO: cartas mais resistentes ao manuseio e ao embaralhamento, para quem joga com frequência.",
            "BARALHO COMPLETO: 54 cartas para poker, truco, buraco, blackjack, pife, paciência e outros jogos.",
            "ÓTIMO PARA PRESENTEAR: o visual diferenciado faz do baralho um presente criativo para quem gosta de "
            "jogos de cartas.",
        ],
        "description": (
            "Baralho dourado com 54 cartas e arte inspirada em cédulas de dólar, que deixa qualquer partida mais "
            "divertida.\n\n"
            "As cartas são resistentes à água e ao rasgo, o que facilita a limpeza e aumenta a durabilidade no uso "
            "frequente. Ideal para poker, truco, buraco, blackjack, pife, paciência e outros jogos.\n\n"
            "Conteúdo da embalagem: 1 baralho com 54 cartas."
        ),
        "keywords": ("deck cassino blackjack paciência pife festa coleção presente dinheiro notas luxo piscina "
                     "praia diversão"),
        "features": ["Resistente à água", "Anti-rasgo", "54 cartas"],
        "extra": {"included_components": ["54 cartas"]},
    },
    "0007_FBA": {
        "title": ("Kit 5 Mini Bands Elásticas com Diferentes Níveis de Resistência, Faixas de Látex para Glúteos, "
                  "Pernas, Fisioterapia, Pilates e Treino em Casa"),
        "bullets": [
            "5 NÍVEIS DE RESISTÊNCIA: kit com 5 mini bands de intensidades diferentes para evoluir o treino aos "
            "poucos, do leve ao mais forte.",
            "GLÚTEOS, PERNAS E BRAÇOS: ideais para agachamentos, abdução de quadril, elevação pélvica, ativação de "
            "glúteos e exercícios de membros superiores.",
            "EM CASA, NA ACADEMIA OU EM VIAGEM: leves e compactas, cabem na bolsa ou na mochila e permitem treinar "
            "em qualquer lugar.",
            "PILATES, YOGA E FISIOTERAPIA: também úteis em alongamento, mobilidade, treinos funcionais e "
            "reabilitação com orientação profissional.",
            "LÁTEX FLEXÍVEL: faixas elásticas em látex. Não recomendado para pessoas com alergia a látex.",
        ],
        "description": (
            "Kit com 5 mini bands elásticas de látex, com níveis de resistência diferentes, para complementar "
            "treinos de força, mobilidade e condicionamento.\n\n"
            "Use nos exercícios de glúteos, pernas e braços, em pilates, yoga, alongamento ou fisioterapia. Por "
            "serem leves e compactas, cabem na bolsa e acompanham você em casa, na academia ou em viagens.\n\n"
            "Atenção: produto de látex, não indicado para pessoas alérgicas. Verifique as faixas antes do uso.\n\n"
            "Conteúdo da embalagem: 5 mini bands elásticas."
        ),
        "keywords": ("miniband elástico faixa academia fitness agachamento abdutor quadril bumbum funcional "
                     "alongamento mobilidade crossfit"),
        "features": ["5 níveis de resistência", "Portátil", "Látex"],
    },
    "SV_0008_FBA": {
        "title": ("Organizador para Banco Traseiro do Carro com Compartimentos, Porta Objetos Multiuso para "
                  "Brinquedos, Garrafas, Livros e Viagens, 60 x 40 cm"),
        "bullets": [
            "MAIS ORGANIZAÇÃO NO CARRO: compartimentos para guardar brinquedos, livros, garrafas, lenços e "
            "acessórios, mantendo tudo no lugar.",
            "APROVEITA O ENCOSTO: é instalado no encosto do banco dianteiro e usa um espaço que normalmente fica "
            "vazio.",
            "TUDO À MÃO NO BANCO DE TRÁS: os objetos ficam visíveis e fáceis de alcançar, ótimo para crianças em "
            "viagens e no trajeto diário.",
            "TAMANHO AMPLO: mede cerca de 60 x 40 cm, com espaço para os itens do dia a dia de toda a família.",
            "PROTEGE O ENCOSTO: ajuda a reduzir marcas de pés e sujeira no banco, além de diminuir objetos soltos "
            "no assoalho.",
        ],
        "description": (
            "Organizador para o encosto do banco dianteiro que deixa o carro mais arrumado e mantém os objetos ao "
            "alcance de quem viaja no banco de trás.\n\n"
            "Os compartimentos acomodam brinquedos, livros, garrafas, lenços e acessórios, reduzindo objetos "
            "soltos no banco e no assoalho. Ideal para famílias com crianças, viagens e uso diário.\n\n"
            "Especificações:\n"
            "- Medidas aproximadas: 60 x 40 cm\n"
            "- Peso: 170 g\n\n"
            "Conteúdo da embalagem: 1 organizador para banco de carro."
        ),
        "keywords": ("automotivo veicular encosto infantil criança bolsa treco acessório passeio estrada "
                     "família"),
        "features": ["Multiuso", "Vários compartimentos", "Instalação no encosto do banco"],
    },
    "SV_0009_FBA": {
        "title": ("Pano Multiuso Descartável em Rolo com 50 Panos de 25 x 30 cm, Picotado e de Alta Absorção, "
                  "para Limpeza de Cozinha, Banheiro e Bancadas"),
        "bullets": [
            "ROLO COM 50 PANOS: panos picotados, prontos para destacar um por vez conforme a necessidade.",
            "TAMANHO 25 X 30 CM: área generosa para limpar, secar e enxugar pias, mesas, bancadas, louças e "
            "superfícies.",
            "ALTA ABSORÇÃO: tecido não tecido de viscose e polipropileno com textura que absorve líquidos e "
            "remove a sujeira com facilidade.",
            "RESISTENTE À UMIDADE: suporta o uso com água e produtos de limpeza sem se desfazer facilmente.",
            "MAIS HIGIENE NA ROTINA: substitui panos de prato e esponjas que acumulam bactérias, sem precisar "
            "lavar. Para uso doméstico ou profissional.",
        ],
        "description": (
            "Pano multiuso descartável em rolo com 50 panos picotados de 25 x 30 cm, prático para a limpeza do dia "
            "a dia.\n\n"
            "Feito em não tecido de viscose e polipropileno, tem textura que absorve bem os líquidos e resiste ao "
            "uso com água e produtos de limpeza. Use na cozinha, no banheiro, em mesas, bancadas, louças e "
            "superfícies em geral.\n\n"
            "Por ser descartável, dispensa lavagem e ajuda a manter a higiene, evitando o acúmulo de sujeira dos "
            "panos tradicionais.\n\n"
            "Conteúdo da embalagem: 1 rolo com 50 panos."
        ),
        "keywords": ("esponja tipo profissional doméstica lava louça secar enxugar higienizar não tecido "
                     "viscose restaurante"),
        "features": ["Descartável", "Picotado", "Alta absorção", "Não tecido"],
    },
    "SV_0010_FBA": {
        "title": ("Sapateira Organizador de Sapatos Desmontável 4 Andares com 12 Tubos, para 8 a 12 Pares, "
                  "Montagem sem Ferramentas, para Quarto, Closet e Entrada - Preto"),
        "bullets": [
            "4 ANDARES PARA 8 A 12 PARES: acomoda de 8 a 12 pares de sapatos, tênis e chinelos, dependendo do "
            "tamanho e do modelo.",
            "MONTAGEM SEM FERRAMENTAS: basta encaixar os 12 tubos horizontais nas hastes laterais. Desmonta com a "
            "mesma facilidade para limpar, mudar de lugar ou guardar.",
            "COMPACTA: mede cerca de 53 x 18,5 x 56 cm e é estreita, cabendo em quartos, closets, corredores, "
            "entradas e lavanderias.",
            "ESTRUTURA DE METAL: laterais com pintura preta e tubos prateados, com visual moderno que combina com "
            "diversos ambientes.",
            "CALÇADOS À VISTA: os andares abertos deixam os pares visíveis, facilitam a ventilação e ajudam a "
            "manter o chão livre.",
        ],
        "description": (
            "Sapateira desmontável com 4 andares e 12 tubos para organizar de 8 a 12 pares de calçados e liberar "
            "espaço no chão.\n\n"
            "A montagem é feita por encaixe, sem ferramentas: os tubos horizontais encaixam nas hastes laterais "
            "pretas, formando as 4 prateleiras. Estreita, cabe em quartos, closets, corredores, entradas e "
            "lavanderias.\n\n"
            "Especificações:\n"
            "- Medidas: 53 x 18,5 x 56 cm\n"
            "- Andares: 4\n"
            "- Tubos: 12\n"
            "- Capacidade: 8 a 12 pares\n"
            "- Peso: 330 g\n\n"
            "Conteúdo da embalagem: 1 estrutura, 12 tubos horizontais, 4 pés de apoio e manual de instruções."
        ),
        "keywords": ("sapato tênis chinelo calçado porta estante prateleira rack corredor lavanderia apartamento "
                     "organização"),
        "features": ["Desmontável", "4 andares", "Montagem sem ferramentas", "Estrutura de metal"],
    },
    "SV_NV0012_FBA": dict(NV12, title=NV12_TITLE),
    "SV_NV0012_PRETO_FBA": dict(NV12, title=NV12_TITLE + " - Preto", color="Preto"),
    "SV_NV0012_VERMELHO_FBA": dict(NV12, title=NV12_TITLE + " - Vermelho", color="Vermelho"),
}


def texts(values, mkt):
    return [{"value": x, "language_tag": "pt_BR", "marketplace_id": mkt} for x in values]


def check():
    for sku, it in ITEMS.items():
        assert len(it["title"]) <= 200, (sku, len(it["title"]))
        assert len(it["bullets"]) == 5 and all(len(b) <= 700 for b in it["bullets"]), sku
        assert len(it["keywords"].encode()) <= 249, (sku, len(it["keywords"].encode()))
        title_words = {w.strip(",").lower() for w in it["title"].split()}
        repeated = [w for w in it["keywords"].lower().split() if w in title_words]
        assert not repeated, (sku, repeated)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "preview"
    if mode not in ("preview", "aplicar"):
        sys.exit("Modo deve ser 'preview' ou 'aplicar'")
    check()
    client = lp.Client()
    client.endpoint = lp.ENDPOINTS[0]
    mkt = lp.env("SPAPI_MARKETPLACE_ID")
    seller = lp.env("SPAPI_SELLER_ID")
    print("Modo:", "PRE-VISUALIZACAO (nada e gravado)" if mode == "preview" else "APLICAR")
    for sku, it in ITEMS.items():
        ptype = client.get(f"/listings/2021-08-01/items/{seller}/{sku}",
                           {"marketplaceIds": mkt, "includedData": "summaries"})["summaries"][0]["productType"]
        attrs = {
            "item_name": texts([it["title"]], mkt),
            "bullet_point": texts(it["bullets"], mkt),
            "product_description": texts([it["description"]], mkt),
            "generic_keyword": texts([it["keywords"]], mkt),
        }
        if it.get("features"):  # algumas categorias nao tem este campo
            attrs["special_feature"] = texts(it["features"], mkt)
        if it.get("color"):
            attrs["color"] = [{"value": it["color"], "language_tag": "pt_BR", "marketplace_id": mkt}]
        for k, vals in it.get("extra", {}).items():
            attrs[k] = texts(vals, mkt)
        patches = [{"op": "replace", "path": f"/attributes/{k}", "value": val} for k, val in attrs.items()]
        resp = v.request(client, "PATCH", sku, {"productType": ptype, "patches": patches}, preview=mode == "preview")
        print(f"\nPATCH {sku} ({ptype}): {resp.get('status')}")
        for issue in resp.get("issues", []):
            print(f"  [{issue.get('severity', '')}] {issue.get('code', '')} {issue.get('message', '')[:220]}"
                  f" {issue.get('attributeNames', '')}")


if __name__ == "__main__":
    main()
