#!/usr/bin/env bash
# Progresso das filas locais (e remotas opcionais via variável REMOTES="user@host1 user@host2").
# Uso: watch -n 15 ./monitor.sh
cd "$(dirname "$0")"

linha() {  # identificador, conteúdo do fila.log
  local maq="$1" log="$2" cidade prog feitas total bloq
  cidade=$(grep '^== ' <<<"$log" | tail -n1 | sed 's/^== //')
  prog=$(grep '^\[' <<<"$log" | tail -n1)
  feitas=$(grep -c '^Fim:' <<<"$log")
  total=$(grep -c '^== [^F]' <<<"$log")
  bloq=$(grep -c ' ! HTTP' <<<"$log")
  printf "%-12s cidade %s/%s  %-45s %-38s 429s: %s\n" "$maq" "$((feitas < total ? feitas + 1 : total))" "$total" "$cidade" "$prog" "$bloq"
}

remoto() {
  timeout 10 ssh -n -o BatchMode=yes -o ConnectTimeout=5 "$1" 'tr -d "\0" < ~/urna-2t/fila.log 2>/dev/null' || echo "(sem conexão)"
}

date '+%H:%M:%S'
linha local "$(tr -d '\0' < fila.log 2>/dev/null)"
for host in ${REMOTES:-}; do
  linha "$host" "$(remoto "$host")"
done
