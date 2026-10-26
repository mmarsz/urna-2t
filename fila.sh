#!/usr/bin/env bash
# Baixa uma lista de municípios em sequência. Uso: ./fila.sh uf:mun:Nome [uf:mun:Nome ...]
# Progresso em fila.log (lido pelo monitor.sh).
cd "$(dirname "$0")"
WORKERS=${WORKERS:-16}
DELAY=${DELAY:-0.02}
: > fila.log
for item in "$@"; do
  IFS=: read -r uf mun nome <<<"$item"
  echo "== $nome ($uf/$mun) $(date +%T)" >> fila.log
  python3 -u baixar_secoes.py --uf "$uf" --mun "$mun" --workers "$WORKERS" --delay "$DELAY" >> fila.log 2>&1
done
echo "== FILA CONCLUÍDA $(date +%T)" >> fila.log
