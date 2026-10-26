#!/usr/bin/env python3
import os
import sys
import json
import time
import zipfile
import io
import urllib.request
import urllib.error
from datetime import datetime
import statistics

BASE_URL = "https://resultados.tse.jus.br/oficial"
CICLO = "ele2026"
PLEITO = "3221"
PLEITO_PAD = "003221"
UF = "ac"
MUNICIPIO = "01120"
ZONA = "0008"
DIA_TURNO = "25/10/2026"  # logd.dat inclui o 1º turno; considera só eventos deste dia

RAW_DIR = "dados/acrelandia_2t/raw"
LOGS_DIR = "dados/acrelandia_2t/logs"
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://resultados.tse.jus.br/oficial/app/index.html",
}

def fetch_url(url, retries=5, sleep_between=0.2):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as res:
                return res.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(sleep_between * (attempt + 1))
        except Exception as e:
            time.sleep(sleep_between * (attempt + 1))
    return None

def parse_log(log_text):
    lines = [l for l in log_text.splitlines() if l.startswith(DIA_TURNO)]
    
    abertura = None
    encerramento = None
    habilitados = 0
    bio = 0
    manual = 0
    votos_computados = 0
    teclas_indevidas = 0
    corrige = 0
    reinicios = 0
    bateria_eventos = 0
    modelo_urna = None
    
    # tempos de voto (entre Eleitor foi habilitado e O voto do eleitor foi computado)
    tempos_voto = []
    ultimo_habilitado_dt = None
    votacao_aberta = False

    for line in lines:
        parts = line.split('\t')
        if len(parts) < 5:
            continue
        dt_str, nivel, id_urna, modulo, msg = parts[0], parts[1], parts[2], parts[3], parts[4]
        
        # Modelo da urna
        if "Modelo de Urna:" in msg or "Modelo de urna:" in msg:
            modelo_urna = msg.split(":")[-1].strip()

        if "Urna pronta para receber votos" in msg:
            votacao_aberta = True
            if not abertura:
                abertura = dt_str

        if "Inicio do Encerramento" in msg or "Encerramento da votação" in msg or "Votação encerrada" in msg:
            votacao_aberta = False
            encerramento = dt_str

        if "Eleitor foi habilitado" in msg:
            habilitados += 1
            try:
                ultimo_habilitado_dt = datetime.strptime(dt_str, "%d/%m/%Y %H:%M:%S")
            except Exception:
                ultimo_habilitado_dt = None

        if "Tipo de habilitação do eleitor [biométrica]" in msg:
            bio += 1
        elif "Tipo de habilitação do eleitor [manual]" in msg:
            manual += 1

        if "O voto do eleitor foi computado" in msg:
            votos_computados += 1
            if ultimo_habilitado_dt:
                try:
                    dt_voto = datetime.strptime(dt_str, "%d/%m/%Y %H:%M:%S")
                    duracao = (dt_voto - ultimo_habilitado_dt).total_seconds()
                    if 0 < duracao < 600:
                        tempos_voto.append(duracao)
                except Exception:
                    pass
                ultimo_habilitado_dt = None

        if "Tecla indevida pressionada" in msg:
            teclas_indevidas += 1

        if "CORRIGE" in msg:
            corrige += 1

        if votacao_aberta and "Início das operações do logd" in msg:
            reinicios += 1

        if votacao_aberta and "Urna operando na bateria" in msg:
            bateria_eventos += 1

    tempo_med = round(statistics.median(tempos_voto), 1) if tempos_voto else None
    tempo_medio = round(statistics.mean(tempos_voto), 1) if tempos_voto else None

    return {
        "linhas": len(lines),
        "modelo": modelo_urna,
        "abertura": abertura,
        "encerramento": encerramento,
        "habilitados": habilitados,
        "bio": bio,
        "manual": manual,
        "votos_computados": votos_computados,
        "tempo_mediano_seg": tempo_med,
        "tempo_medio_seg": tempo_medio,
        "teclas_indevidas": teclas_indevidas,
        "corrige": corrige,
        "reinicios": reinicios,
        "bateria_eventos": bateria_eventos,
    }

def main():
    print(f"=== Coletor de Logs da Urna - Acrelândia/AC (2º Turno 2026) ===")
    config_url = f"{BASE_URL}/{CICLO}/arquivo-urna/{PLEITO}/config/{UF}/{UF}-p{PLEITO_PAD}-cs.json"
    print(f"1. Carregando lista de seções de: {config_url}")
    
    config_data_raw = fetch_url(config_url)
    if not config_data_raw:
        print("Erro: não foi possível obter o arquivo de configuração de seções do TSE.")
        sys.exit(1)
        
    config_json = json.loads(config_data_raw.decode('utf-8'))
    sections = []
    for abr in config_json.get("abr", []):
        for mu in abr.get("mu", []):
            if mu.get("cd") == MUNICIPIO:
                for zon in mu.get("zon", []):
                    if zon.get("cd") == ZONA:
                        for sec in zon.get("sec", []):
                            sections.append(sec["ns"])
                            
    sections = sorted(sections)
    print(f"Total de seções encontradas em Acrelândia: {len(sections)}")

    resumo_geral = []

    for idx, sec in enumerate(sections, 1):
        print(f"[{idx:02d}/{len(sections):02d}] Processando Seção {sec}...", end=" ", flush=True)
        aux_url = f"{BASE_URL}/{CICLO}/arquivo-urna/{PLEITO}/dados/{UF}/{MUNICIPIO}/{ZONA}/{sec}/p{PLEITO_PAD}-{UF}-m{MUNICIPIO}-z{ZONA}-s{sec}-aux.json"
        
        aux_raw = fetch_url(aux_url)
        if not aux_raw:
            print("AUX não disponível (404/pendente)")
            continue

        aux_data = json.loads(aux_raw.decode('utf-8'))
        hashes = aux_data.get("hashes", [])
        if not hashes:
            print("Sem urnas totalizadas")
            continue

        urna_info = hashes[0]
        urna_hash = urna_info.get("hash")
        log_file_info = next((a for a in urna_info.get("arq", []) if a.get("tp") == "log"), None)
        
        if not log_file_info:
            print("Arquivo de log não especificado")
            continue
            
        log_fname = log_file_info["nm"]
        log_url = f"{BASE_URL}/{CICLO}/arquivo-urna/{PLEITO}/dados/{UF}/{MUNICIPIO}/{ZONA}/{sec}/{urna_hash}/{log_fname}"
        
        # Download do arquivo .jez
        jez_bytes = fetch_url(log_url)
        if not jez_bytes:
            print(f"Erro ao baixar {log_fname}")
            continue

        raw_path = os.path.join(RAW_DIR, f"sec_{sec}_{log_fname}")
        with open(raw_path, "wb") as f:
            f.write(jez_bytes)

        # Extração do logd.dat
        try:
            with zipfile.ZipFile(io.BytesIO(jez_bytes)) as z:
                log_text = z.open("logd.dat").read().decode("latin-1")
        except Exception as e:
            print(f"Erro ao descompactar log: {e}")
            continue

        log_path = os.path.join(LOGS_DIR, f"acrelandia_zn0008_sec{sec}_logd.dat")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(log_text)

        stats = parse_log(log_text)
        stats["secao"] = sec
        stats["zona"] = ZONA
        stats["municipio"] = "Acrelândia"
        stats["uf"] = UF.upper()
        stats["hash"] = urna_hash
        stats["arquivo_jez"] = log_fname
        stats["tamanho_jez_bytes"] = len(jez_bytes)
        resumo_geral.append(stats)

        print(f"OK! Votos: {stats['votos_computados']} | Bio: {stats['bio']} | Med: {stats['tempo_mediano_seg']}s | Teclas ind: {stats['teclas_indevidas']}")
        time.sleep(0.08)

    # Salva resumo consolidado
    resumo_path_json = "dados/acrelandia_2t/resumo_acrelandia_2t.json"
    with open(resumo_path_json, "w", encoding="utf-8") as f:
        json.dump(resumo_geral, f, indent=2, ensure_ascii=False)

    resumo_path_csv = "dados/acrelandia_2t/resumo_acrelandia_2t.csv"
    with open(resumo_path_csv, "w", encoding="utf-8") as f:
        headers = ["secao", "votos_computados", "habilitados", "bio", "manual", "tempo_mediano_seg", "tempo_medio_seg", "teclas_indevidas", "corrige", "reinicios", "bateria_eventos", "abertura", "encerramento", "linhas", "arquivo_jez"]
        f.write(";".join(headers) + "\n")
        for s in resumo_geral:
            row = [str(s.get(h, "")) for h in headers]
            f.write(";".join(row) + "\n")

    print(f"\n Concluído! {len(resumo_geral)} seções processadas com sucesso.")
    print(f" Arquivos salvos em:")
    print(f"  - Logs brutos (.jez): {RAW_DIR}")
    print(f"  - Logs extraídos (.dat): {LOGS_DIR}")
    print(f"  - Resumo JSON: {resumo_path_json}")
    print(f"  - Resumo CSV: {resumo_path_csv}")

if __name__ == "__main__":
    main()
