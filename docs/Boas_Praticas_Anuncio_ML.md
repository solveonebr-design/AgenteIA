# Boas Práticas de Anúncios no Mercado Livre

Guia para escrever anúncios da loja SOLVEONE que apareçam bem na busca e convertam em
vendas. Vale para quem escreve o anúncio (o Claude ou uma pessoa).

- Repositório: github.com/solveonebr-design/AgenteIA
- Checagens automáticas: `scripts/meli_qualidade.py`, executadas pelas ações
  `validar_anuncio`, `publicar_anuncio`, `previa_edicao` e `editar_anuncio`
- Versão de 10/10/2026

> As regras marcadas como **BLOQUEIA** impedem a publicação no workflow. **ALERTA** reduz a
> exposição ou a conversão e deve ser corrigido antes de publicar. **DICA** é melhoria
> opcional. O próprio Mercado Livre muda regras com frequência: em caso de conflito, vale o
> que a validação (`POST /items/validate`) e a central de vendedores disserem.

## 1. Como o Mercado Livre decide quem aparece

O ranking da busca combina relevância (o quanto o anúncio corresponde ao que foi buscado) e
desempenho (o quanto ele vende e satisfaz o comprador). Na prática, os fatores que o
vendedor controla são:

| Fator | O que pesa | Onde se resolve |
|---|---|---|
| Relevância | Título com os termos que o comprador digita; categoria correta; ficha técnica completa (usada nos filtros) | Seções 3, 4 e 5 |
| Qualidade da publicação | Fotos boas e em quantidade, ficha técnica, descrição | Seções 5, 6 e 7 |
| Competitividade | Preço em relação a anúncios equivalentes; frete grátis; prazo de entrega (Full e Flex ajudam) | Seção 8 |
| Reputação e histórico | Vendas, avaliações, reclamações, atrasos, cancelamentos | Operação do dia a dia (seção 9) |

## 2. Antes de escrever: pesquisa

1. Rodar a ação `mais_vendidos` com o código da categoria do produto (ex.: `MLB1574` para
   Casa, Móveis e Decoração) e abrir `data/meli_mais_vendidos.csv`.
2. Dos produtos parecidos no top 20, anotar:
   - as palavras que se repetem nos títulos (o que o comprador procura);
   - a faixa de preço;
   - quantas e quais fotos usam (abrir os links);
   - se são de catálogo (tipo `PRODUCT`) ou anúncios livres.
3. Escolher a **categoria mais específica** possível (a folha da árvore, não a categoria
   principal). Categoria errada derruba a relevância e pode exigir atributos que não
   existem no produto.
4. Verificar se o produto existe no **catálogo** do Mercado Livre. Se existir, o anúncio
   vinculado ao catálogo disputa a vitrine do produto (buy box) e costuma ter mais exposição.

## 3. Título

Regras do Mercado Livre e da busca:

- **Até 60 caracteres** (BLOQUEIA acima disso). Usar o espaço: títulos curtos aparecem em
  menos buscas (DICA abaixo de 35).
- Estrutura: **produto + marca + modelo + característica principal** (material, tamanho,
  capacidade, cor, quantidade).
- Escrever como o comprador busca: "Escorredor De Louça", não "Organizador Multiuso Para
  Pia".
- Iniciais maiúsculas; nunca CAIXA ALTA (ALERTA).
- Sem símbolos `! * $ % # @ ?` e sem reticências (ALERTA).
- Sem palavras repetidas (ALERTA).
- **Não usar** (ALERTA): condição (novo, nova), preço, desconto, promoção, oferta,
  liquidação, frete grátis, envio imediato, pronta entrega, garantia, parcelado, sem juros,
  mais vendido, lançamento, imperdível, barato, melhor preço, black friday. Essas
  informações têm campos próprios e o Mercado Livre penaliza ou recusa.
- Variações (cor, tamanho) entram no título só quando cada anúncio é de uma variação.
- Depois que o anúncio tem vendas, **o título não pode mais ser alterado**. Revisar com
  calma antes de publicar.

Exemplos:

| Ruim | Bom |
|---|---|
| `PROMOÇÃO Escorredor NOVO Frete Grátis!!!` | `Escorredor De Louça Dobrável Silicone Retrátil Verde` |
| `Garrafa` | `Garrafa Térmica Inox 500ml Parede Dupla Tampa Rosca Preta` |
| `Kit kit organizador organizador cozinha` | `Kit 10 Potes Herméticos Vidro 640ml Tampa Com Trava` |

## 4. Categoria e catálogo

- Usar a categoria sugerida pelo preditor do Mercado Livre e conferir se faz sentido.
- A categoria define a ficha técnica e as regras. Trocar de categoria depois é trabalhoso.
- Se a categoria exigir catálogo (`catalog_required`), o anúncio precisa ser vinculado a um
  produto do catálogo.

## 5. Ficha técnica (atributos)

A ficha técnica é o que alimenta os filtros da busca (cor, material, capacidade,
voltagem...). Anúncio sem o atributo não aparece quando o comprador filtra por ele.

- Preencher **todos** os atributos obrigatórios (BLOQUEIA) e o máximo possível dos
  opcionais. Meta: **100%**; abaixo de 80% é ALERTA.
- Valores reais e consistentes com o título, as fotos e a descrição.
- **Marca:** a marca real; sem marca, usar "Genérico" ou "Sem marca", conforme a categoria
  aceitar.
- **Código de barras (GTIN/EAN):** informar se existir. Se não existir, usar o motivo
  (`EMPTY_GTIN_REASON`) aceito pela categoria.
- **SKU do vendedor** (`SELLER_SKU`): sempre preencher, igual ao controle interno e ao SKU
  da Amazon quando for o mesmo produto.
- **Embalagem:** medidas e peso **com a embalagem**, corretos. Valores errados geram frete
  errado e cobrança de diferença.

## 6. Fotos

| Regra | Nível |
|---|---|
| Pelo menos 1 foto | BLOQUEIA |
| JPG ou PNG; WebP não é aceito | BLOQUEIA |
| Mínimo 500 px no maior lado | BLOQUEIA |
| Pelo menos 6 fotos | ALERTA |
| 1200 px ou mais (ativa o zoom) | DICA |

Boas práticas (não checadas automaticamente; conferir a olho):

- **Foto principal:** fundo branco puro, produto inteiro, centralizado, ocupando a maior
  parte da imagem; sem textos, logos, bordas, marcas d'água ou montagens.
- Fotos seguintes: outros ângulos, detalhes (material, acabamento), produto em uso,
  medidas com referência de tamanho, o que vem na embalagem, variações de cor.
- Mostrar exatamente o que será entregue. Itens que não acompanham o produto não devem
  aparecer sem aviso.
- Fotos próprias. Não copiar fotos de outros vendedores.

## 7. Descrição

- **Texto simples** (o Mercado Livre não aceita HTML; ALERTA).
- **Proibido** (BLOQUEIA): links, sites, e-mails e qualquer forma de contato ou venda fora
  do Mercado Livre (WhatsApp, Instagram, Telegram, telefone, "compre direto").
- Telefone ou sequência parecida com telefone: ALERTA (conferir).
- Pelo menos 300 caracteres (DICA abaixo disso).
- Não repetir palavras-chave artificialmente: a descrição não melhora o ranking da busca
  como o título e a ficha técnica; ela serve para convencer e evitar dúvidas e devoluções.

Estrutura recomendada:

```
[Frase de abertura com o principal benefício]

BENEFÍCIOS
- Benefício 1 (o que resolve para o comprador)
- Benefício 2
- Benefício 3

ESPECIFICAÇÕES
- Material:
- Medidas (A x L x P):
- Peso:
- Capacidade / voltagem / cor:

CONTEÚDO DA EMBALAGEM
- 1 unidade de ...

COMO USAR E CUIDADOS
- ...

PERGUNTAS FREQUENTES
- Pode ir à lava-louças? ...
```

Só incluir afirmações confirmadas pela dona da conta (ex.: livre de BPA, vai ao micro-ondas,
voltagem). Afirmações falsas geram devoluções e reclamações, que derrubam a reputação.

## 8. Preço, frete e tipo de anúncio

- **Preço:** comparar com os equivalentes do `mais_vendidos`. Não precisa ser o menor, mas
  muito acima dos concorrentes reduz a exposição. Considerar a tarifa do tipo de anúncio e
  o custo do frete no cálculo da margem.
- **Tipo de anúncio:** `gold_special` (Clássico) tem tarifa menor; `gold_pro` (Premium) tem
  tarifa maior e oferece parcelamento sem juros ao comprador, com mais exposição em várias
  categorias. Começar pelo Clássico e testar o Premium nos produtos que vendem.
- **Frete:** frete grátis e prazo curto pesam na escolha do comprador e no ranking. Acima do
  valor mínimo definido pelo Mercado Livre, o frete grátis é obrigatório no Mercado Envios.
- **Full** (estoque no centro de distribuição do Mercado Livre): entrega mais rápida e selo
  Full, com bom efeito na conversão. Avaliar para produtos com giro.
- **Estoque:** manter `available_quantity` maior que zero; anúncio sem estoque é pausado e
  perde posição.

## 9. Depois de publicar

- Responder perguntas rápido (o tempo de resposta conta).
- Despachar no prazo; evitar cancelamentos (afetam a reputação).
- Acompanhar visitas e conversão. Pouca visita: revisar título, categoria e ficha técnica.
  Visita sem venda: revisar preço, fotos, frete e descrição.
- Usar a ação `previa_edicao` para conferir a nota de qualidade antes de cada edição.

## 10. Checklist antes de publicar

- [ ] Categoria mais específica e correta; catálogo verificado
- [ ] Título com até 60 caracteres, na estrutura produto + marca + modelo + característica
- [ ] Sem termos proibidos, símbolos ou CAIXA ALTA no título
- [ ] Ficha técnica 100% (ou o máximo possível), com medidas e peso da embalagem corretos
- [ ] SKU preenchido; GTIN ou motivo de ausência
- [ ] 6 fotos ou mais, JPG/PNG, 1200 px, principal com fundo branco
- [ ] Descrição em texto simples, sem contatos, com especificações e conteúdo da embalagem
- [ ] Preço comparado com os mais vendidos da categoria
- [ ] `validar_anuncio` verde, com nota de qualidade de 85 ou mais
- [ ] Proposta aprovada pela dona da conta antes de `publicar_anuncio`

## 11. Nota de qualidade (como é calculada)

A ação `validar_anuncio` mostra `Qualidade: N/100`, calculada por `meli_qualidade.py`:

| Parte | Peso | Como pontua |
|---|---|---|
| Título | 25 | Integral sem problemas; perde 30% por ALERTA e 10% por DICA; zero se BLOQUEIA |
| Ficha técnica | 35 | Proporcional ao percentual preenchido |
| Fotos | 25 | Proporcional ao número de fotos, até 6 |
| Descrição | 15 | Mesma regra do título |

É uma nota interna para comparar versões do anúncio, não a nota oficial do Mercado Livre.
Meta: **85 ou mais** antes de publicar.

## 12. Instruções para o Claude ao criar um anúncio

1. Pedir à dona da conta: produto, preço, estoque, tipo de anúncio, forma de envio e o que
   é confirmado sobre o produto (material, medidas, peso, voltagem, o que vem na embalagem).
2. Se o produto já é vendido na Amazon, reaproveitar título, bullets, descrição e fotos do
   repositório (`scripts/conteudo_*.py`, `fotos/`), adaptando para estas regras.
3. Rodar `mais_vendidos` na categoria e usar como referência de termos, preço e fotos.
4. Montar `anuncios/<nome>.json` a partir de `anuncios/_modelo.json`, seguindo este guia.
5. Rodar `validar_anuncio` e corrigir até ficar verde e com nota de 85 ou mais.
6. Mostrar à dona da conta: título, preço, categoria, ficha técnica, fotos, descrição, nota e
   alertas restantes. **Publicar só com confirmação explícita.**
