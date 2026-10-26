# Procedimento: arquivos de urna do 2º turno 2026 → dashboard

Como baixar os arquivos de urna (BU, RDV e log) seção por seção, processar e incluir cidades no
dashboard (`index.html` + `dados_dashboard.js`). Para o esquema detalhado do `secoes.json` e o contexto, veja `HANDOFF.md`.

## 1. Fonte

```
https://resultados.tse.jus.br/oficial/ele2026/arquivo-urna/3221/            # pleito 3221 = 2º turno
  config/<uf>/<uf>-p003221-cs.json                                            # municípios → zonas → seções
  dados/<uf>/<mun>/<zona>/<secao>/p003221-<uf>-m<mun>-z<zona>-s<secao>-aux.json
  dados/<uf>/<mun>/<zona>/<secao>/<hash>/o03221<uf><mun><zona><secao>-{bu.dat,rdv.dat,vota.vsc,log.jez}

https://resultados.tse.jus.br/oficial/ele2026/<eleicao>/dados/<uf>/<uf><mun>-c0001-e00<eleicao>-u.json
  # resultado oficial do município (Presidente): eleição 6257 = 1º turno, 6258 = 2º turno
```

Os arquivos consolidados (`cdn.tse.jus.br/.../arqurnatot/..._2t_*.zip`) e o BU em CSV (`bweb_2t_*`) **ainda não
saíram** na data da coleta (26/10/2026). Quando saírem, prefira esses arquivos para escalas estaduais/nacionais (ver §7).

## 2. Achar o código do município

```bash
curl -s -H 'User-Agent: Mozilla/5.0' https://resultados.tse.jus.br/oficial/ele2026/arquivo-urna/3221/config/mg/mg-p003221-cs.json \
 | python3 -c "import json,sys; [print(m['cd'],m['nm'],sum(len(z['sec']) for z in m['zon'])) for a in json.load(sys.stdin)['abr'] for m in a['mu'] if 'BELO' in m['nm']]"
```

## 3. Download

### Limite do TSE (medido em 26/10)
- **O limite é por IP e disparado pela taxa de requests**, não pelo número de conexões. O HTTP 429 aparece por volta de **260 a 270 requests/s**.
  Ele também pode ocorrer com 48 conexões sem pausa baixando arquivos pequenos.
- A penalidade dura **de 1 a 2 minutos** e vale só para aquele IP.
- Pedir arquivos que não existem (404, fora do cache do CDN) gera 429 com mais facilidade. Por isso o script pula o `imgbu`.
- **Configuração segura: 16 workers e `--delay 0.02` por IP.**
- Não use serviços gratuitos de nuvem como robô de download distribuído para contornar limites da CDN.

### Execução local
```bash
python3 -u baixar_secoes.py --uf mg --mun 41238 --workers 16 --delay 0.02
```
O script pode ser interrompido e retomado (pula o que já existe), grava `dados/<uf>_<mun>/manifest.csv`,
faz pausa global (60 s, 120 s…) quando recebe 403, 429 ou 5xx e pula o `imgbu`.

Para baixar uma fila de municípios em sequência:
```bash
setsid nohup ./fila.sh "mg:41238:Belo Horizonte" "sp:70572:Santo André" >/dev/null 2>&1 < /dev/null & disown
watch -n 15 ./monitor.sh
```

## 4. Processamento

```bash
.venv/bin/python extrair_secoes.py dados/mg_41238          # → dados/mg_41238/secoes.json (requer asn1tools no .venv)
# resultado oficial (o gerador do dashboard exige os dois arquivos)
for e in 6257:1t 6258:2t; do curl -s -H 'User-Agent: Mozilla/5.0' \
  "https://resultados.tse.jus.br/oficial/ele2026/${e%%:*}/dados/mg/mg41238-c0001-e00${e%%:*}-u.json" -o dados/mg_41238/oficial_${e##*:}.json; done
python3 gerar_dados_dashboard.py                           # → dados_dashboard.js + dados/cidades/*.js + dados/secoes_resumo.csv
```

Detalhes técnicos do extrator (`extrair_secoes.py`):
- **Logs aninhados (urnas substituídas):** Quando uma urna é substituída por urna de contingência durante a votação, o `log.jez` final inclui um arquivo `.jez` interno contendo o `logd.dat` da urna original. O extrator percorre recursivamente até 2 níveis de arquivos `.jez` e desduplica as linhas mantendo a ordem original.
- **Conferência RDV × BU e Log × BU:**
  - `rdv_votos == comparecimento BU` em **100% das 57.744 seções auditadas** (16.378.557 votos).
  - `votos_2t (log) == comparecimento BU` em **57.743 de 57.744 seções (99,998%)**. A única exceção em toda a base é a seção `0395/0298` de Guarulhos (`sp_64777`), que registra 268 votos no BU e 268 no RDV (encerrada às `17:03:06`), mas cujo `aux.json` no TSE foi publicado apenas com `bu.dat`, `rdv.dat`, `vota.vsc` e `imgbu.dat` (sem arquivo `log.jez`). Como essa seção encerrou às 17:03:06, a ausência do log não afeta as contagens pós-17h/pós-18h.

## 5. Dados consolidados das 15 cidades (após leitura de logs aninhados)

| Cidade | Pasta | Seções c/ BU | Abertas ≥18h | Votos pós-17h (Fila 17h / 18h / 19h) | Pós-17h no 1ºT | Lula (13) / Flávio (22) | Comparecimento |
|---|---|---:|---:|---|---:|---|---:|
| **São Paulo (SP)** | `sp_71072` | 26.683 | **1.661** | 4.492 (3.886 / 601 / 5) | 26.366 | 55,50% / 44,50% | 79,64% |
| **Salvador (BA)** | `ba_38490` | 5.124 | **755** | 1.768 (1.528 / 238 / 2) | 72.607 | 73,24% / 26,76% | 84,23% |
| **Feira de Santana (BA)** | `ba_35157` | 1.218 | **61** | 147 (134 / 13 / 0) | 34.635 | 64,15% / 35,85% | 86,98% |
| **Guarulhos (SP)** | `sp_64777` | 2.851 | **17** | 265 (259 / 6 / 0) | 4.258 | 48,91% / 51,09% | 82,36% |
| Belo Horizonte (MG) | `mg_41238` | 4.927 | 0 | 327 (327 / 0 / 0) | 35.141 | 49,20% / 50,80% | 79,32% |
| Curitiba (PR) | `pr_75353` | 4.056 | 0 | 144 (144 / 0 / 0) | 2.769 | 37,71% / 62,29% | 82,53% |
| Porto Alegre (RS) | `rs_88013` | 3.077 | 0 | 121 (121 / 0 / 0) | 2.584 | 55,84% / 44,16% | 78,89% |
| São Bernardo do Campo (SP) | `sp_70750` | 2.011 | 0 | 126 (126 / 0 / 0) | 563 | 55,37% / 44,63% | 81,09% |
| Santo André (SP) | `sp_70572` | 1.742 | 0 | 85 (85 / 0 / 0) | 949 | 49,71% / 50,29% | 79,57% |
| Osasco (SP) | `sp_67890` | 1.641 | 0 | 165 (165 / 0 / 0) | 2.522 | 52,36% / 47,64% | 79,68% |
| Cuiabá (MT) | `mt_90670` | 1.338 | 0 | 157 (157 / 0 / 0) | 11.786 | 40,42% / 59,58% | 82,76% |
| Joinville (SC) | `sc_81795` | 1.234 | 0 | 38 (38 / 0 / 0) | 1.151 | 26,18% / 73,82% | 84,12% |
| Vitória da Conquista (BA) | `ba_39659` | 766 | 0 | 94 (94 / 0 / 0) | 17.585 | 58,78% / 41,22% | 85,37% |
| Blumenau (SC) | `sc_80470` | 754 | 0 | 20 (20 / 0 / 0) | 734 | 26,58% / 73,42% | 83,03% |
| Paranaguá (PR) | `pr_77453` | 322 | 0 | 30 (30 / 0 / 0) | 1.145 | 36,80% / 63,20% | 81,50% |
| **TOTAL (15 CIDADES)** | — | **57.744** | **2.494** | **7.979 (7.114 / 858 / 7)** | **214.795** | **53,57% / 46,43%** | **80,85%** |

## 6. Cuidados metodológicos no dashboard

- **Status de Feira de Santana:** Na coleta em 26/10, 1.218 seções de Feira de Santana tinham BU publicado e 308 seções (zonas 0154 a 0156) ainda constavam como "Recebida" no TSE.
- **Sigilo do voto no RDV:** O arquivo `rdv.dat` embaralha os votos e não possui carimbo de horário (para preservar o sigilo constitucional do voto). Portanto, não é possível saber em quem votaram especificamente os eleitores que compareceram após as 17h ou após as 18h; mede-se a quantidade exata de votos por horário via `logd.dat` e o resultado agregado das seções via `bu.dat`.
- **Proporção exata dos votos pós-18h:**
  - Em **São Paulo**, os **606 votos pós-18h** equivalem a **0,0083%** do comparecimento municipal (7.284.071) e **0,079%** da diferença entre os candidatos (766.431).
  - Em **Salvador**, os **240 votos pós-18h** equivalem a **0,0146%** do comparecimento municipal (1.647.069) — ou **0,0152%** dos votos válidos (1.575.824) — e **0,033%** da diferença municipal (732.320).
- **Separação entre pós-17h (fila normal) e pós-18h (prorrogação):** O critério de seção prorrogada é `encerramento >= "18:00"` (horário de Brasília no BU). Votos entre 17:00 e 17:59 existem em todas as 15 cidades e correspondem à fila normal de encerramento com senha às 17h.

## 7. Publicação (GitHub Pages)

- O repositório inclui apenas `index.html`, `vendor/`, `dados_dashboard.js`, `dados/cidades/*.js`, `dados/secoes_resumo.csv` e `instagram/`.
- Os diretórios de arquivos brutos (`dados/<uf>_<mun>/`, ~13 GB) ficam excluídos pelo `.gitignore`.
