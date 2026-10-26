#!/usr/bin/env python3
"""Teste incremental de rate limit no resultados.tse.jus.br: sobe a concorrência em degraus e para no
primeiro sinal de limitação. Baixa aux.json + log.jez de cada seção (mesma estrutura de baixar_secoes.py).

Uso: python3 teste_rate.py --uf ba --mun 35157 [--degraus 8,16,32,64,128,192,256] [--secoes-por-degrau 150]

Para (sem retry) se: qualquer 429/403, >2% de erros no degrau, ou p95 de latência > 4x o do 1º degrau.
Resultado: tabela no terminal + dados/<uf>_<mun>/teste_rate.csv (um request por linha).
"""
import argparse
import csv
import json
import os
import statistics
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from baixar_secoes import BASE_URL, HEADERS, PLEITO_PAD

REGISTROS = []
LOCK = threading.Lock()


def get(url, degrau):
    t0 = time.time()
    status, n = 0, 0
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30) as res:
            data = res.read()
            status, n = res.status, len(data)
    except urllib.error.HTTPError as e:
        status, data = e.code, None
    except Exception as e:
        status, data = f"exc:{type(e).__name__}", None
    with LOCK:
        REGISTROS.append({"degrau": degrau, "t": round(t0, 3), "ms": round((time.time() - t0) * 1000),
                          "status": status, "bytes": n, "arquivo": url.rsplit("/", 1)[-1]})
    return status, data


def salvar(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path + ".part", "wb") as f:
        f.write(data)
    os.replace(path + ".part", path)


def secao(uf, mun, zona, sec, out_dir, degrau):
    base = f"{BASE_URL}/dados/{uf}/{mun}/{zona}/{sec}"
    st, aux = get(f"{base}/p{PLEITO_PAD}-{uf}-m{mun}-z{zona}-s{sec}-aux.json", degrau)
    if st != 200:
        return
    sec_dir = os.path.join(out_dir, zona, sec)
    salvar(os.path.join(sec_dir, "aux.json"), aux)
    for h in json.loads(aux).get("hashes", []):
        for a in h.get("arq", []):
            if a["tp"] == "log":
                st, data = get(f"{base}/{h['hash']}/{a['nm']}", degrau)
                if st == 200:
                    salvar(os.path.join(sec_dir, h["hash"], a["nm"]), data)


def resumo(degrau, regs, dur):
    ms = sorted(r["ms"] for r in regs)
    ruins = [r for r in regs if r["status"] not in (200, 404)]
    codigos = {}
    for r in ruins:
        codigos[str(r["status"])] = codigos.get(str(r["status"]), 0) + 1
    return {
        "degrau": degrau, "req": len(regs), "seg": round(dur, 1), "req_s": round(len(regs) / dur, 1),
        "mb_s": round(sum(r["bytes"] for r in regs) / dur / 1e6, 1),
        "p50_ms": ms[len(ms) // 2] if ms else 0, "p95_ms": ms[int(len(ms) * .95)] if ms else 0,
        "erros": len(ruins), "codigos": codigos,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--uf", required=True)
    ap.add_argument("--mun", required=True)
    ap.add_argument("--degraus", default="8,16,32,64,128,192,256")
    ap.add_argument("--secoes-por-degrau", type=int, default=150)
    args = ap.parse_args()
    uf = args.uf.lower()

    _, cfg = get(f"{BASE_URL}/config/{uf}/{uf}-p{PLEITO_PAD}-cs.json", 0)
    mu = next(m for a in json.loads(cfg)["abr"] for m in a["mu"] if m["cd"] == args.mun)
    out_dir = os.path.join("dados", f"{uf}_{args.mun}")
    pendentes = [(z["cd"], s["ns"]) for z in mu["zon"] for s in z["sec"]
                 if not os.path.exists(os.path.join(out_dir, z["cd"], s["ns"], "aux.json"))]
    print(f"{mu['nm']}/{uf.upper()}: {len(pendentes)} seções pendentes", flush=True)
    print(f"{'conex':>6} {'req':>5} {'seg':>6} {'req/s':>7} {'MB/s':>6} {'p50ms':>6} {'p95ms':>6} erros", flush=True)

    linhas, p95_base, motivo = [], None, None
    for degrau in [int(x) for x in args.degraus.split(",")]:
        lote, pendentes = pendentes[:args.secoes_por_degrau], pendentes[args.secoes_por_degrau:]
        if not lote:
            motivo = "acabaram as seções"
            break
        n0, t0 = len(REGISTROS), time.time()
        with ThreadPoolExecutor(degrau) as ex:
            list(ex.map(lambda zs: secao(uf, args.mun, zs[0], zs[1], out_dir, degrau), lote))
        r = resumo(degrau, REGISTROS[n0:], time.time() - t0)
        linhas.append(r)
        print(f"{degrau:>6} {r['req']:>5} {r['seg']:>6} {r['req_s']:>7} {r['mb_s']:>6} {r['p50_ms']:>6} "
              f"{r['p95_ms']:>6} {r['erros']} {r['codigos'] or ''}", flush=True)
        p95_base = p95_base or max(r["p95_ms"], 1)
        if any(c in r["codigos"] for c in ("429", "403")):
            motivo = f"limitação detectada ({r['codigos']})"
        elif r["erros"] > 0.02 * r["req"]:
            motivo = f"mais de 2% de erros ({r['codigos']})"
        elif r["p95_ms"] > 4 * p95_base:
            motivo = f"latência p95 subiu {r['p95_ms'] / p95_base:.1f}x"
        if motivo:
            break
    print(f"\nParou: {motivo or 'todos os degraus completos, sem limitação'}", flush=True)

    with open(os.path.join(out_dir, "teste_rate.csv"), "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(REGISTROS[0].keys()))
        if f.tell() == 0:
            w.writeheader()
        w.writerows(REGISTROS)
    with open(os.path.join(out_dir, "teste_rate_resumo.json"), "w") as f:
        json.dump({"degraus": linhas, "parou": motivo}, f, indent=1)


if __name__ == "__main__":
    main()
