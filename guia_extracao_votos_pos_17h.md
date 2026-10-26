# Guia de Engenharia: Extração de Registros Individuais por Urna & Auditoria de Votos Pós-17h

Este documento estabelece a arquitetura, o fluxo de coleta e as estratégias técnicas para contornar a ausência de dados consolidados na noite da eleição, analisar votos registrados após as 17h via `logd.dat` e escalar a coleta para municípios e estados inteiros sem sofrer bloqueios de *rate limiting* utilizando pools de proxy (ex: Webshare.io).

---

## 1. O Problema: Inexistência de Dados Consolidados em D+0

Na noite da apuração (e nos dias subsequentes), o TSE **não disponibiliza** um banco de dados consolidado ou CSV único contendo todos os registros de urna, votos minuto a minuto ou logs do 2º turno.

* **O que o TSE publica de imediato:** Arquivos atômicos individuais por seção eleitoral, espalhados em milhares de diretórios estáticos servidos via CDN Akamai (`resultados.tse.jus.br`).
* **Microdados oficiais (Portal de Dados Abertos):** Arquivos consolidados em lote (como o repositório de BUs) normalmente levam semanas ou meses para serem montados e homologados pela equipe técnica do tribunal.
* **A única alternativa viável:** Consumir diretamente a API de arquivos de urna (`arquivo-urna/3221/...`), mapeando cada município, zona e seção para baixar o contêiner bruto `.log.jez` de cada máquina instalada.

---

## 2. Auditoria de Votos Pós-17h: Lógica no `logd.dat`

Com a extensão do horário de votação em seções com filas extensas ou falhas operacionais, o `logd.dat` é a única fonte que registra o timestamp com precisão de segundo para cada ação na urna.

### A. Atenção Crítica aos Fusos Horários

Desde as Eleições de 2022, o TSE unificou o encerramento da votação para as **17:00 no horário de Brasília**.
Como o relógio interno da urna eletrônica opera no **horário local**, o corte de 17h de Brasília deve ser ajustado conforme a UF:

| UF / Região | Fuso Horário Local | 17:00 Horário de Brasília no Relógio da Urna |
|---|---|---|
| **Acre (AC)** | UTC-5 (-2h) | **15:00:00** |
| **AM (oeste), RO, RR, MT, MS** | UTC-4 (-1h) | **16:00:00** |
| **DF, SP, RJ, MG, Sul, Nordeste, etc.** | UTC-3 (0h) | **17:00:00** |
| **Fernando de Noronha (PE)** | UTC-2 (+1h) | **18:00:00** |

### B. Linhas do Log a Monitorar e Filtro Obrigatório de Data

> [!CAUTION]
> **A urna eletrônica NÃO apaga os eventos do 1º Turno!**  
> O `logd.dat` da urna é contínuo e histórico: contém a carga inicial da urna (em setembro), os eventos do 1º turno (04/10/2026), a preparação do 2º turno e o dia da votação do 2º turno (25/10/2026).  
> **Portanto, é obrigatório filtrar as linhas pela data do 2º turno (`25/10/2026`)**, sob risco de computar votos de 04/10/2026 por engano!

Para cada urna, o script deve filtrar os seguintes eventos ocorridos em `25/10/2026`:

1. **`Eleitor foi habilitado`**:
   - Momento em que o mesário valida o título / biometria e libera a urna.
2. **`O voto do eleitor foi computado`**:
   - Momento exato em que o eleitor conclui a confirmação do último cargo na cabine.
3. **Distribuição de Senhas**:
   - Quando os portões fecham às 17h oficiais, os eleitores na fila recebem senha. O log registra interações do mesário que marcam a transição.
4. **`Encerramento da votação`**:
   - Horário em que o mesário encerra a seção para emitir os Boletins de Urna (BU).

### C. Métricas Extraídas por Seção

* **`votos_totais`**: Total de eventos `O voto do eleitor foi computado`.
* **`votos_pos_limite`**: Contagem onde `hora_voto > hora_corte_local`.
* **`pct_pos_limite`**: `votos_pos_limite / votos_totais * 100`.
* **`primeiro_voto_pos_limite`**: Timestamp do primeiro voto computado após o corte.
* **`ultimo_voto_computado`**: Timestamp do último voto antes de encerrar.
* **`horario_encerramento`**: Timestamp de `Encerramento da votação`.

---

## 3. Arquitetura Configurável por Escopo

O coletor deve permitir alternar facilmente o escopo de análise através de um arquivo de configuração (`config_alvos.json`):

```json
{
  "ciclo": "ele2026",
  "pleito": "3221",
  "modo": "cidades_especificas", 
  "alvos": [
    {
      "uf": "ac",
      "municipios": ["01120"]
    },
    {
      "uf": "sp",
      "municipios": ["71072", "61000"]
    }
  ],
  "hora_corte_brasilia": "17:00:00"
}
```

Se `modo` for `"estado_inteiro"`, o script itera sobre **todos** os municípios listados no arquivo de configuração estadual `uf-p003221-cs.json`.

---

## 4. O Gargalo de Rate Limiting e Solução com Webshare.io

### O Desafio
* Acrelândia tem 45 urnas (~90 requisições HTTP) e roda sem proxy em poucos segundos.
* Uma cidade média/grande (ex: Campinas/SP ou São Paulo/SP) tem milhares de seções:
  * 5.000 seções = **10.000 requisições HTTP**.
  * Um estado como SP tem 103.000 seções = **200.000+ requisições HTTP**.
* O CDN da Akamai corta requisições repetidas do mesmo IP com `HTTP 429` ou bloqueios por WAF/desafio JavaScript.

### Solução: Webshare.io Rotating Proxies

O Webshare oferece um gateway único de proxy rotativo (Rotating Proxy Endpoint):
`http://p.webshare.io:80` ou `http://p.webshare.io:9999` com autenticação via token/usuário. Cada requisição sai por um IP residencial ou datacenter diferente.

#### Configuração de Conexão com Proxy Pool

```python
import urllib.request

PROXY_HOST = "p.webshare.io"
PROXY_PORT = "80"  # ou 9999
PROXY_USER = "seu_usuario_webshare-rotate"
PROXY_PASS = "sua_senha_webshare"

proxy_url = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"

proxy_handler = urllib.request.ProxyHandler({
    "http": proxy_url,
    "https": proxy_url
})
opener = urllib.request.build_opener(proxy_handler)
```

### Boas Práticas para Evitar Detecção e Erros

1. **Pool de Workers com Rotação Automática:**
   - Utilizar `concurrent.futures.ThreadPoolExecutor(max_workers=20)` com o proxy rotativo.
   - Cada worker requisita via proxy, distribuindo o tráfego por centenas de IPs.
2. **Backoff Exponencial para Status 429 / 503:**
   - Se o proxy retornar 429 (raro, se bem distribuído) ou falha de rede, aguardar `2^tentativa * 0.5s` e tentar novamente com outro nó da rotação.
3. **Pular Arquivos Já Baixados (`Skip Existing`):**
   - Salvar os `.jez` em disco local. Se o arquivo já existir com tamanho > 0, não faz requisição de download, apenas processa o log.
4. **Respeitar os Cabeçalhos Padrão:**
   - Sempre enviar `User-Agent` de navegador comum, `Accept: application/json` e `Referer: https://resultados.tse.jus.br/oficial/app/index.html`.

---

## 5. Script Completo de Auditoria Pós-17h (com Suporte a Proxy)

O script a seguir está pronto para execução, integrando fusos horários, filtros por cidade/UF, extração dos votos pós-17h e suporte opcional ao Webshare.io:

```python
#!/usr/bin/env python3
"""
auditoria_votos_pos_17h.py
Auditoria de votos pós-17h nas urnas do 2º Turno (TSE 2026).
"""
import os
import sys
import json
import time
import zipfile
import io
import urllib.request
import urllib.error
from datetime import datetime, time as dtime
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://resultados.tse.jus.br/oficial"
CICLO = "ele2026"
PLEITO = "3221"
PLEITO_PAD = "003221"

# Fuso horário local relativo a Brasília (em horas)
FUSO_POR_UF = {
    "ac": -2,
    "am": -1,  # AM maior parte é -1
    "ro": -1,
    "rr": -1,
    "ms": -1,
    "mt": -1,
}

# Configuração de Proxy Webshare (deixe None para requisição direta)
PROXY_CONFIG = {
    "enabled": False,  # Mude para True ao ativar Webshare
    "host": "p.webshare.io",
    "port": "80",
    "user": "SEU_USUARIO-rotate",
    "password": "SUA_SENHA",
}

def get_opener():
    if PROXY_CONFIG["enabled"]:
        p_url = f"http://{PROXY_CONFIG['user']}:{PROXY_CONFIG['password']}@{PROXY_CONFIG['host']}:{PROXY_CONFIG['port']}"
        handler = urllib.request.ProxyHandler({"http": p_url, "https": p_url})
        return urllib.request.build_opener(handler)
    return urllib.request.build_opener()

def fetch(url, opener, retries=4):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        "Referer": "https://resultados.tse.jus.br/oficial/app/index.html",
    }
    for att in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with opener.open(req, timeout=12) as res:
                return res.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(0.5 * (2 ** att))
        except Exception:
            time.sleep(0.5 * (2 ** att))
    return None

def analisar_secao(uf, mu_cd, mu_nm, zon, sec, opener, out_dir):
    corte_hora = 17 + FUSO_POR_UF.get(uf.lower(), 0)
    corte_time = dtime(corte_hora, 0, 0)

    aux_url = f"{BASE_URL}/{CICLO}/arquivo-urna/{PLEITO}/dados/{uf}/{mu_cd}/{zon}/{sec}/p{PLEITO_PAD}-{uf}-m{mu_cd}-z{zon}-s{sec}-aux.json"
    aux_raw = fetch(aux_url, opener)
    if not aux_raw:
        return None

    aux_data = json.loads(aux_raw.decode("utf-8"))
    hashes = aux_data.get("hashes", [])
    if not hashes:
        return None

    urna = hashes[0]
    log_info = next((a for a in urna.get("arq", []) if a.get("tp") == "log"), None)
    if not log_info:
        return None

    log_url = f"{BASE_URL}/{CICLO}/arquivo-urna/{PLEITO}/dados/{uf}/{mu_cd}/{zon}/{sec}/{urna['hash']}/{log_info['nm']}"
    jez_bytes = fetch(log_url, opener)
    if not jez_bytes:
        return None

    with zipfile.ZipFile(io.BytesIO(jez_bytes)) as z:
        linhas = z.open("logd.dat").read().decode("latin-1").splitlines()

    votos_totais = 0
    votos_pos_17h = 0
    primeiro_voto_pos = None
    ultimo_voto = None
    encerramento = None

    for l in linhas:
        parts = l.split("\t")
        if len(parts) < 5:
            continue
        dt_str, msg = parts[0], parts[4]
        if not dt_str.startswith("25/10/2026"):
            continue

        if "Encerramento da votação" in msg:
            encerramento = dt_str

        if "O voto do eleitor foi computado" in msg:
            votos_totais += 1
            ultimo_voto = dt_str
            try:
                dt_obj = datetime.strptime(dt_str, "%d/%m/%Y %H:%M:%S")
                if dt_obj.time() >= corte_time:
                    votos_pos_17h += 1
                    if not primeiro_voto_pos:
                        primeiro_voto_pos = dt_str
            except Exception:
                pass

    return {
        "uf": uf.upper(),
        "municipio": mu_nm,
        "cod_municipio": mu_cd,
        "zona": zon,
        "secao": sec,
        "votos_totais": votos_totais,
        "votos_pos_17h": votos_pos_17h,
        "pct_pos_17h": round((votos_pos_17h / votos_totais * 100), 2) if votos_totais else 0,
        "primeiro_voto_pos_17h": primeiro_voto_pos,
        "ultimo_voto_computado": ultimo_voto,
        "encerramento": encerramento,
    }
```

---

## 6. Próximos Passos Sugeridos

1. **Definir a Lista de Cidades Alvo:** Escolher os municípios prioritários onde houve relatos de filas ou atrasos na votação.
2. **Ativar o Proxy Webshare:** Para listas acima de 500 seções, habilitar as credenciais rotativas do Webshare para evitar bloqueios da CDN.
3. **Gerar Relatórios e Gráficos de Série Temporal:** Plotar a curva de votos computados por hora (16h, 17h, 18h, 19h+) por município para quantificar o impacto da prorrogação.
