#!/usr/bin/env python3
"""Extrai métricas por seção (BU + log + RDV) dos arquivos baixados por baixar_secoes.py.

Uso: .venv/bin/python extrair_secoes.py dados/mt_90670 [--saida dados/mt_90670/secoes.json]

Horários do log/BU são locais da urna; convertidos para Brasília via OFFSET_UF.
"""
import argparse
import glob
import io
import json
import os
import zipfile
from collections import Counter
from datetime import datetime, timedelta

import asn1tools

DIA_1T = "04/10/2026"
DIA_2T = "25/10/2026"
# horas a somar ao horário local para chegar ao de Brasília (sem horário de verão)
OFFSET_UF = {"ac": 2, "am": 1, "mt": 1, "ms": 1, "ro": 1, "rr": 1}

SPEC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "spec")
BU = asn1tools.compile_files(os.path.join(SPEC, "bu.asn1"), "ber")
RDV = asn1tools.compile_files(os.path.join(SPEC, "rdv.asn1"), "ber")


def ler_bu(path):
    env = BU.decode("EntidadeEnvelopeGenerico", open(path, "rb").read())
    bu = BU.decode("EntidadeBoletimUrna", env["conteudo"])
    out = {"local": bu["identificacaoSecao"]["local"], "votos": {}}
    sa = bu.get("dadosSecaoSA")
    if sa and sa[0] == "dadosSecao":
        out["bu_abertura"] = sa[1].get("dataHoraAbertura")
        out["bu_encerramento"] = sa[1].get("dataHoraEncerramento")
    for r in bu["resultadosVotacaoPorEleicao"]:
        out["aptos"] = out.get("aptos", 0) + r["qtdEleitoresAptos"]
        for rv in r["resultadosVotacao"]:
            out["comparecimento"] = out.get("comparecimento", 0) + rv["qtdComparecimento"]
            for tc in rv["totaisVotosCargo"]:
                for v in tc["votosVotaveis"]:
                    chave = str(v["identificacaoVotavel"]["codigo"]) if v["tipoVoto"] == "nominal" else v["tipoVoto"]
                    out["votos"][chave] = out["votos"].get(chave, 0) + v["quantidadeVotos"]
    return out


def contar_rdv(path):
    env = RDV.decode("EntidadeResultadoRDV", open(path, "rb").read())
    n = 0
    for el in env["rdv"]["eleicoes"][1]:
        for vc in el["votosCargos"]:
            n += len(vc["votos"])
    return n


def _extrair_linhas_log(jez_bytes, max_depth=2):
    linhas = []
    try:
        with zipfile.ZipFile(io.BytesIO(jez_bytes)) as z:
            for name in z.namelist():
                if name == "logd.dat":
                    linhas.extend(z.open(name).read().decode("latin-1").splitlines())
                elif name.endswith(".jez") and max_depth > 0:
                    linhas.extend(_extrair_linhas_log(z.read(name), max_depth - 1))
    except Exception:
        pass
    return linhas


def ler_log(jez_bytes, offset_h):
    linhas = list(dict.fromkeys(_extrair_linhas_log(jez_bytes)))
    m = {"votos_1t": 0, "votos_hora": Counter(), "votos_pos17": 0, "habilit_pos17": 0,
         "ultimo_voto": None, "encerrar": None, "votos_1t_pos17": 0}
    for linha in linhas:
        p = linha.split("\t")
        if len(p) < 5:
            continue
        dia = p[0][:10]
        if dia not in (DIA_1T, DIA_2T):
            continue
        msg = p[4]
        computado = "O voto do eleitor foi computado" in msg
        habilitado = "Eleitor foi habilitado" in msg
        selecionou_encerrar = "Operador selecionou: Encerrar votação" in msg
        if not (computado or habilitado or selecionou_encerrar):
            continue
        bsb = datetime.strptime(p[0], "%d/%m/%Y %H:%M:%S") + timedelta(hours=offset_h)
        pos17 = bsb.hour >= 17
        if dia == DIA_1T:
            if computado:
                m["votos_1t"] += 1
                m["votos_1t_pos17"] += pos17
            continue
        if computado:
            m["votos_hora"][bsb.hour] += 1
            m["votos_pos17"] += pos17
            m["ultimo_voto"] = bsb.strftime("%H:%M:%S")
        elif habilitado:
            m["habilit_pos17"] += pos17
        elif m["encerrar"] is None:
            m["encerrar"] = bsb.strftime("%H:%M:%S")
    m["votos_hora"] = {str(h): n for h, n in sorted(m["votos_hora"].items())}
    m["votos_2t"] = sum(m["votos_hora"].values())
    return m


def bu_hora_bsb(s, offset_h):
    return (datetime.strptime(s, "%Y%m%dT%H%M%S") + timedelta(hours=offset_h)).strftime("%H:%M:%S") if s else None


def _proc_secao(item):
    aux_path, off = item
    sec_dir = os.path.dirname(aux_path)
    zona, sec = sec_dir.split(os.sep)[-2:]
    aux = json.load(open(aux_path))
    row = {"zona": zona, "secao": sec, "st": aux.get("st"), "n_urnas": len(aux.get("hashes", []))}
    err = None
    try:
        log_tot = None
        for h in aux.get("hashes", []):
            arqs = {a["tp"]: os.path.join(sec_dir, h["hash"], a["nm"]) for a in h.get("arq", [])}
            if "bu" in arqs and os.path.exists(arqs["bu"]) and "aptos" not in row:
                row.update(ler_bu(arqs["bu"]))
                row["abertura"] = bu_hora_bsb(row.pop("bu_abertura", None), off)
                row["encerramento"] = bu_hora_bsb(row.pop("bu_encerramento", None), off)
            if "rdv" in arqs and os.path.exists(arqs["rdv"]):
                row["rdv_votos"] = row.get("rdv_votos", 0) + contar_rdv(arqs["rdv"])
            if "log" in arqs and os.path.exists(arqs["log"]):
                lg = ler_log(open(arqs["log"], "rb").read(), off)
                if log_tot is None:
                    log_tot = lg
                else:  # urna substituída: soma contagens, mantém últimos horários
                    for k in ("votos_1t", "votos_pos17", "habilit_pos17", "votos_1t_pos17", "votos_2t"):
                        log_tot[k] += lg[k]
                    hrs = Counter(log_tot["votos_hora"]) + Counter(lg["votos_hora"])
                    log_tot["votos_hora"] = {k: hrs[k] for k in sorted(hrs, key=int)}
                    for k in ("ultimo_voto", "encerrar"):
                        log_tot[k] = max(filter(None, (log_tot[k], lg[k])), default=None)
        if log_tot:
            row.update(log_tot)
    except Exception as e:
        err = f"{zona}/{sec}: {e}"
    return row, err


def main():
    from concurrent.futures import ProcessPoolExecutor
    ap = argparse.ArgumentParser()
    ap.add_argument("pasta")
    ap.add_argument("--saida")
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 4)
    args = ap.parse_args()
    uf = os.path.basename(args.pasta.rstrip("/")).split("_")[0]
    off = OFFSET_UF.get(uf, 0)
    secoes, erros = [], []

    paths = sorted(glob.glob(os.path.join(args.pasta, "*", "*", "aux.json")))
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for row, err in ex.map(_proc_secao, ((p, off) for p in paths), chunksize=64):
            secoes.append(row)
            if err:
                erros.append(err)

    saida = args.saida or os.path.join(args.pasta, "secoes.json")
    json.dump({"uf": uf, "offset_bsb_h": off, "secoes": secoes}, open(saida, "w"), ensure_ascii=False)
    print(f"{len(secoes)} seções -> {saida}; {len(erros)} erros")
    for e in erros[:10]:
        print("  ", e)


if __name__ == "__main__":
    main()
