# Documentação Técnica — Auditoria de Logs/BU/RDV das Urnas (2º Turno 2026 · 25/10/2026)

Auditoria consolidada com resultado por cidade, filtro por zona/seção e análise do impacto da prorrogação do horário de votação (separando a fila normal das 17h dos votos registrados após as 18h de Brasília).

## Contexto

- O ministro Cristiano Zanin (STF) prorrogou a votação do 2º turno até as 19h em razão de falhas no transporte público. Como mais de 80% das urnas já haviam sido encerradas às 17h, a decisão foi restrita às **seções que ainda estavam abertas** naquele momento. Fonte:
  https://agenciabrasil.ebc.com.br/justica/noticia/2026-10/horario-de-votacao-ampliado-sera-apenas-onde-urnas-nao-foram-fechadas
- A campanha de Flávio Bolsonaro também protocolou pedido de prorrogação até as 19h alegando fortes chuvas em estados do Sul e Sudeste:
  https://agenciabrasil.ebc.com.br/politica/noticia/2026-10/campanha-de-flavio-pede-votacao-ate-19h-por-chuvas-em-alguns-estados
- Como os pacotes consolidados (`arqurnatot`) só são publicados pelo TSE semanas após o pleito, a coleta foi realizada baixando diretamente os arquivos individuais de cada seção no endpoint oficial de resultados.

## Fonte dos dados

```
https://resultados.tse.jus.br/oficial/ele2026/arquivo-urna/3221/
  config/<uf>/<uf>-p003221-cs.json                              # lista de municípios/zonas/seções da UF
  dados/<uf>/<mun>/<zona>/<secao>/p003221-<uf>-m<mun>-z<zona>-s<secao>-aux.json   # hashes + nomes dos arquivos
  dados/<uf>/<mun>/<zona>/<secao>/<hash>/<arquivo>              # bu.dat, rdv.dat, vota.vsc, log.jez
```
Pleito `3221` corresponde ao 2º turno (a eleição presidencial do 2º turno é `6258`, e a do 1º turno é `6257`).

## Estrutura em disco

```
dados/<uf>_<mun>/
  <zona>/<secao>/aux.json
  <zona>/<secao>/<hash>/o03221<uf><mun><zona><secao>-{bu.dat,rdv.dat,vota.vsc,log.jez}
  manifest.csv     # zona;secao;st_secao;hash;st_hash;dr;hr;tp;arquivo;status;bytes
  secoes.json      # métricas por seção (gerado por extrair_secoes.py) ← entrada do gerador do dashboard
```
- `bu.dat`: Boletim de Urna, ASN.1/BER. Especificação em `spec/bu.asn1`.
- `rdv.dat`: Registro Digital do Voto, ASN.1. Especificação em `spec/rdv.asn1`. Os votos ficam **embaralhados e sem carimbo de horário** para preservar o sigilo constitucional do voto.
- `log.jez`: arquivo comprimido contendo `logd.dat` (TSV ISO-8859-1: `data hora \t nível \t id_urna \t módulo \t mensagem \t hash`) e, nas seções com substituição de urna, arquivos `.jez` internos com os logs da urna substituída. Contém eventos do 1º turno (`04/10/2026`) e do 2º turno (`25/10/2026`), filtrados pela data.
- `vota.vsc`: assinatura digital da seção.

## `secoes.json` — schema

```json
{"uf": "ba", "offset_bsb_h": 0, "secoes": [ {
  "zona": "0005", "secao": "0123", "st": "Totalizada", "n_urnas": 1,
  "local": 1295,
  "aptos": 380, "comparecimento": 320,
  "votos": {"13": 200, "22": 110, "branco": 4, "nulo": 6},
  "abertura": "08:00:01", "encerramento": "19:00:36",
  "rdv_votos": 320,
  "votos_2t": 320,
  "votos_hora": {"8": 40, "9": 38, "17": 2, "18": 1},
  "votos_pos17": 3, "habilit_pos17": 3,
  "ultimo_voto": "18:12:44", "encerrar": "19:00:13",
  "votos_1t": 310, "votos_1t_pos17": 12
} ] }
```
O fuso horário soma `offset_bsb_h` ao horário local registrado na urna (MT=`+1`, BA/SP/MG/PR/SC/RS=`0`).

## Resultados verificados nas principais capitais e nos 15 municípios

**São Paulo (`sp_71072`):** 26.683 seções (2.058 locais). Comparecimento de 7.284.071 de 9.145.969 aptos (79,64%). Lula (13) obteve 3.864.354 votos (55,50%) e Flávio (22) obteve 3.097.923 (44,50%) (nulos 216.904, brancos 104.890; margem de 766.431 votos).
- **1.661 seções (6,2%, em 224 locais) encerraram às 18:00 ou depois.** Principais zonas: 0381 Parelheiros (262 seções), 0001 Bela Vista (141), 0253 Tatuapé (132), 0422 Lauzane Paulista (104), 0280 Capela do Socorro (98), 0350 Sapopemba (97) e 0020 Valo Velho (90).
- Essas 1.661 seções registraram **1.495 votos depois das 17h** (17h: 889, 18h: 601, 19h: 5 → **606 votos pós-18h**, equivalentes a **0,0083% do comparecimento**), com no máximo 23 votos pós-17h em uma seção.
- Em **739 das 1.661 seções abertas (44,5%)**, o último voto ocorreu antes das 17h (0 votos pós-17h).
- As 25.022 seções que fecharam antes das 18h receberam **2.997 votos na faixa das 17h** (fila normal).
- No 1º turno (mesmas urnas), São Paulo teve **26.366 votos depois das 17h**, contra **4.492** no 2º turno.
- Votos por hora em São Paulo (Brasília, após leitura de logs aninhados):
  `8h: 1.027.897 · 9h: 945.968 · 10h: 995.265 · 11h: 1.006.083 · 12h: 952.854 · 13h: 782.738 · 14h: 620.689 · 15h: 548.061 · 16h: 400.024 · 17h: 3.886 · 18h: 601 · 19h: 5` (Soma = **7.284.071**, 100% igual ao BU).

**Salvador (`ba_38490`):** 5.124 seções. Comparecimento de 1.647.069 de 1.955.471 aptos (84,23%). Lula (13) obteve 1.154.072 votos (73,24%) e Flávio (22) obteve 421.752 (26,76%) (nulos 52.319, brancos 18.926; margem de 732.320 votos).
- **755 seções (14,7%, em 122 locais) encerraram às 18:00 ou depois.** Principais zonas: 0005 (205 seções), 0019 (136) e 0002 (113).
- Essas seções receberam **658 votos depois das 17h** (17h: 418, 18h: 238, 19h: 2 → **240 votos pós-18h**, equivalentes a **0,0146% do comparecimento** ou **0,0152% dos votos válidos**), com no máximo 7 por seção.
- As 4.369 seções que fecharam antes das 18h receberam **1.110 votos na faixa das 17h** (fila normal).
- Em **333 das 755 seções abertas (44,1%)**, o último voto foi antes das 17h.
- No 1º turno, Salvador registrou **72.607 votos depois das 17h**, contra **1.768** no 2º turno.
- Votos por hora em Salvador (Brasília, após leitura de logs aninhados):
  `8h: 283.560 · 9h: 275.692 · 10h: 268.026 · 11h: 227.671 · 12h: 166.653 · 13h: 130.943 · 14h: 117.502 · 15h: 105.211 · 16h: 70.043 · 17h: 1.528 · 18h: 238 · 19h: 2` (Soma = **1.647.069**, 100% igual ao BU).

**Feira de Santana (`ba_35157`):** 1.218 seções com BU publicado na coleta (e 308 seções que ainda constavam com status "Recebida" nas zonas 0154–0156). Das 1.218 seções, **61 encerraram ≥18h**, somando **13 votos após as 18h** (e 134 na fila das 17h, contra 34.635 pós-17h no 1º turno).

**Guarulhos (`sp_64777`):** 2.851 seções. **17 seções encerraram ≥18h**, somando **6 votos após as 18h** (e 259 na fila das 17h, contra 4.258 no 1º turno).

**11 Cidades de Controle (0 seções abertas ≥18h):**
Belo Horizonte (4.927 seções), Curitiba (4.056), Porto Alegre (3.077), São Bernardo do Campo (2.011), Santo André (1.742), Osasco (1.641), Cuiabá (1.338), Joinville (1.234), Vitória da Conquista (766), Blumenau (754) e Paranaguá (322). Em todas essas 11 cidades, **100% das seções fecharam antes das 18h** (0 votos pós-18h).

## Checagens de Integridade

1. **`RDV == Comparecimento BU`:** **100% nas 57.744 seções auditadas** (16.378.557 votos conferidos).
2. **`Log (votos_2t) == Comparecimento BU`:** **57.743 de 57.744 seções (99,998%)** batem exatamente 100% após a extração recursiva dos `.jez` aninhados de urnas de contingência.
   - **Única exceção:** Na seção `0395/0298` de Guarulhos (`sp_64777`), o BU e o RDV registram 268 votos e encerramento às `17:03:06`, mas o `aux.json` disponibilizado pelo TSE não incluiu o arquivo `log.jez` (apenas `bu.dat`, `rdv.dat`, `vota.vsc` e `imgbu.dat`), resultando em 0 eventos lidos no log daquela seção. Como ela fechou às 17:03:06, isso não afeta as contagens pós-17h/pós-18h.

## Scripts

| Arquivo | O que faz |
|---|---|
| `baixar_secoes.py --uf X --mun N [--zonas a,b] [--workers 16 --delay 0.02]` | Baixa os arquivos brutos por seção, retoma de onde parou, aplica backoff global em 403/429/5xx e grava `manifest.csv` |
| `extrair_secoes.py dados/<uf>_<mun>` | Decodifica `bu.dat` e `rdv.dat` via ASN.1 e extrai recursivamente `log.jez` (incluindo `.jez` aninhados), gerando `secoes.json` |
| `gerar_dados_dashboard.py` | Consolida as 15 cidades em `dados_dashboard.js`, `dados/cidades/<cid>.js` e `dados/secoes_resumo.csv` |
| `gerar_instagram.js` | Renderiza os 4 slides retrato (1080×1350 e 1080×1920) em `instagram/` via Chromium headless |
| `monitor.sh` | Monitora o progresso local do `fila.log` (`watch -n 15 ./monitor.sh`) |
| `spec/bu.asn1`, `spec/rdv.asn1` | Especificações ASN.1 do TSE |
