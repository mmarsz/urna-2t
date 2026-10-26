#!/usr/bin/env python3
"""Baixa todos os arquivos de urna (bu, rdv, vota.vsc, log.jez) por seção, 2º turno 2026.

Uso: python3 baixar_secoes.py --uf mt --mun 90670 [--zonas 0001,0039] [--workers 4] [--proxies arq.txt]

Estrutura: dados/<uf>_<mun>/<zona>/<secao>/{aux.json, <hash>/<arquivos>}
Pode ser interrompido e retomado: pula arquivos já baixados.
"""
import argparse
import itertools
import csv
import json
import os
import random
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://resultados.tse.jus.br/oficial/ele2026/arquivo-urna/3221"
PLEITO_PAD = "003221"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://resultados.tse.jus.br/oficial/app/index.html",
}
OPENERS = itertools.cycle([urllib.request.build_opener()])


def carregar_proxies(path):
    """Arquivo Webshare: ip:porta:user:senha por linha. Cada request usa o próximo proxy da lista."""
    openers = []
    for linha in open(path, encoding="utf-8"):
        partes = linha.strip().split(":")
        if len(partes) != 4:
            continue
        ip, porta, user, senha = partes
        url = f"http://{user}:{senha}@{ip}:{porta}"
        openers.append(urllib.request.build_opener(urllib.request.ProxyHandler({"http": url, "https": url})))
    if not openers:
        raise SystemExit(f"nenhum proxy válido em {path}")
    return openers


class Throttle:
    """Pausa global compartilhada entre threads quando o servidor reclama (429/403/5xx)."""

    def __init__(self, delay):
        self.delay = delay
        self.pause_until = 0.0
        self.lock = threading.Lock()

    def wait(self):
        while True:
            with self.lock:
                remaining = self.pause_until - time.time()
            if remaining <= 0:
                break
            time.sleep(min(remaining, 5))
        time.sleep(self.delay * random.uniform(0.5, 1.5))

    def backoff(self, seconds):
        with self.lock:
            self.pause_until = max(self.pause_until, time.time() + seconds)


def fetch(url, throttle, retries=8):
    for attempt in range(retries):
        throttle.wait()
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with next(OPENERS).open(req, timeout=30) as res:
                return res.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code in (403, 429) or e.code >= 500:
                wait = min(300, 60 * 2 ** attempt)  # penalidade do Akamai dura ~1-2 min
                print(f"  ! HTTP {e.code} em {url.rsplit('/', 1)[-1]} -> pausa global {wait}s", flush=True)
                throttle.backoff(wait)
            else:
                time.sleep(2 * (attempt + 1))
        except Exception:
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"falhou após {retries} tentativas: {url}")


def write_atomic(path, data):
    tmp = path + ".part"
    with open(path + ".part", "wb") as f:
        f.write(data)
    os.replace(tmp, path)


def baixar_secao(uf, mun, zona, sec, out_dir, throttle):
    sec_dir = os.path.join(out_dir, zona, sec)
    os.makedirs(sec_dir, exist_ok=True)
    aux_path = os.path.join(sec_dir, "aux.json")
    base = f"{BASE_URL}/dados/{uf}/{mun}/{zona}/{sec}"

    if os.path.exists(aux_path):
        aux_raw = open(aux_path, "rb").read()
    else:
        aux_raw = fetch(f"{base}/p{PLEITO_PAD}-{uf}-m{mun}-z{zona}-s{sec}-aux.json", throttle)
        if aux_raw is None:
            return [{"zona": zona, "secao": sec, "status": "sem_aux"}]
        write_atomic(aux_path, aux_raw)

    aux = json.loads(aux_raw)
    rows = []
    for h in aux.get("hashes", []):
        h_dir = os.path.join(sec_dir, h["hash"])
        os.makedirs(h_dir, exist_ok=True)
        for arq in h.get("arq", []):
            if arq.get("tp") == "imgbu":  # listado em seções "Recebida", mas ainda não publicado (404)
                continue
            path = os.path.join(h_dir, arq["nm"])
            status = "ok"
            if not os.path.exists(path):
                data = fetch(f"{base}/{h['hash']}/{arq['nm']}", throttle)
                if data is None:
                    status = "404"
                else:
                    write_atomic(path, data)
            rows.append({
                "zona": zona, "secao": sec, "st_secao": aux.get("st"), "hash": h["hash"],
                "st_hash": h.get("st"), "dr": h.get("dr"), "hr": h.get("hr"),
                "tp": arq.get("tp"), "arquivo": arq["nm"], "status": status,
                "bytes": os.path.getsize(path) if status == "ok" else 0,
            })
    if not rows:
        rows.append({"zona": zona, "secao": sec, "st_secao": aux.get("st"), "status": "sem_hash"})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--uf", required=True)
    ap.add_argument("--mun", required=True, help="código TSE do município (5 dígitos)")
    ap.add_argument("--zonas", help="lista separada por vírgula; padrão: todas")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--proxies", help="arquivo ip:porta:user:senha (Webshare); padrão: IP direto")
    ap.add_argument("--delay", type=float, default=0.15, help="pausa média por request, por worker (s)")
    args = ap.parse_args()
    uf = args.uf.lower()

    if args.proxies:
        global OPENERS
        lista = carregar_proxies(args.proxies)
        OPENERS = itertools.cycle(lista)
        print(f"usando {len(lista)} proxies em rodízio", flush=True)
    throttle = Throttle(args.delay)
    cfg = json.loads(fetch(f"{BASE_URL}/config/{uf}/{uf}-p{PLEITO_PAD}-cs.json", throttle))
    mu = next((m for a in cfg["abr"] for m in a["mu"] if m["cd"] == args.mun), None)
    if mu is None:
        raise SystemExit(f"município {args.mun} não encontrado em {uf.upper()}")
    zonas_filtro = set(args.zonas.split(",")) if args.zonas else None
    secoes = [(z["cd"], s["ns"]) for z in mu["zon"] if not zonas_filtro or z["cd"] in zonas_filtro
              for s in z["sec"]]

    out_dir = os.path.join("dados", f"{uf}_{args.mun}")
    os.makedirs(out_dir, exist_ok=True)
    print(f"{mu['nm']}/{uf.upper()}: {len(secoes)} seções -> {out_dir} ({args.workers} workers)", flush=True)

    manifest, falhas = [], []
    t0 = time.time()
    with ThreadPoolExecutor(args.workers) as ex:
        futs = {ex.submit(baixar_secao, uf, args.mun, z, s, out_dir, throttle): (z, s) for z, s in secoes}
        for i, fut in enumerate(as_completed(futs), 1):
            z, s = futs[fut]
            try:
                manifest.extend(fut.result())
            except Exception as e:
                falhas.append((z, s, str(e)))
                print(f"  x {z}/{s}: {e}", flush=True)
            if i % 25 == 0 or i == len(secoes):
                el = time.time() - t0
                print(f"[{i}/{len(secoes)}] {el / 60:.1f} min, ETA {el / i * (len(secoes) - i) / 60:.1f} min", flush=True)

    campos = ["zona", "secao", "st_secao", "hash", "st_hash", "dr", "hr", "tp", "arquivo", "status", "bytes"]
    manifest.sort(key=lambda r: (r["zona"], r["secao"], r.get("hash", ""), r.get("tp", "")))
    with open(os.path.join(out_dir, "manifest.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos, delimiter=";", restval="")
        w.writeheader()
        w.writerows(manifest)

    n_hash = len({(r["zona"], r["secao"], r.get("hash")) for r in manifest if r.get("hash")})
    print(f"\nFim: {len(secoes) - len(falhas)}/{len(secoes)} seções, {n_hash} urnas, "
          f"{sum(r.get('bytes', 0) for r in manifest) / 1e6:.0f} MB, {len(falhas)} falhas. "
          f"Rode de novo para retomar falhas.")


if __name__ == "__main__":
    main()
