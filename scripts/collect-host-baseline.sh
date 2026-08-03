#!/usr/bin/env bash
# Read-only Enterprise AI host baseline collector. It never uses docker inspect.

set -uo pipefail

readonly VALID_HOSTS='rddb rdapp rdvector rdautomation rdmonitor'
host_id=''
output_dir='/var/tmp/enterprise-ai-baseline'

usage() {
  cat <<'EOF'
Usage: collect-host-baseline.sh --host-id <rddb|rdapp|rdvector|rdautomation|rdmonitor> [--output-dir <path>]

Collects non-secret, read-only host baseline evidence as JSON. The default output
directory is /var/tmp/enterprise-ai-baseline and is outside the Git repository.
Exit code 0 means all collection commands succeeded; 2 means output was written
but one or more commands were unavailable or failed; 64 means invalid arguments.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --host-id) host_id=${2:-}; shift 2 ;;
    --output-dir) output_dir=${2:-}; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) echo "ERROR: unknown argument: $1" >&2; usage >&2; exit 64 ;;
  esac
done

if [[ -z "$host_id" ]] || [[ " $VALID_HOSTS " != *" $host_id "* ]]; then
  echo 'ERROR: --host-id must be one of: rddb, rdapp, rdvector, rdautomation, rdmonitor.' >&2
  exit 64
fi
if [[ -z "$output_dir" ]]; then
  echo 'ERROR: --output-dir must not be empty.' >&2
  exit 64
fi

timestamp=$(date -u +%Y%m%dT%H%M%SZ)
work_dir=$(mktemp -d "${TMPDIR:-/tmp}/enterprise-ai-baseline.XXXXXX") || exit 1
trap 'rm -rf "$work_dir"' EXIT
mkdir -p "$output_dir" || { echo "ERROR: cannot create output directory: $output_dir" >&2; exit 1; }

overall_rc=0
result_names=()
result_codes=()
result_files=()

capture() {
  local name=$1
  shift
  local file="$work_dir/${#result_names[@]}.txt"
  local rc=0
  "$@" >"$file" 2>&1 || rc=$?
  result_names+=("$name")
  result_codes+=("$rc")
  result_files+=("$file")
  if [[ $rc -ne 0 ]]; then overall_rc=2; fi
}

capture 'uname' uname -a
capture 'os_release' cat /etc/os-release
capture 'docker_version' docker version --format '{{json .}}'
capture 'docker_compose_version' docker compose version
capture 'docker_containers' docker ps --format '{{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}\t{{.Names}}'
capture 'tcp_listeners' ss -lnt

json_file="$output_dir/${host_id}-${timestamp}.json"
{
  printf '{\n  "schema_version": 1,\n  "collected_at_utc": "%s",\n  "host_id": "%s",\n  "results": [' "$timestamp" "$host_id"
  for i in "${!result_names[@]}"; do
    [[ $i -gt 0 ]] && printf ','
    printf '\n    {"name":"%s","exit_code":%s,"output":' "${result_names[$i]}" "${result_codes[$i]}"
    python3 -c 'import json, sys; print(json.dumps(sys.stdin.read()), end="")' < "${result_files[$i]}" 2>/dev/null || printf '"JSON encoding unavailable"'
    printf '}'
  done
  printf '\n  ]\n}\n'
} >"$json_file"

echo "Evidence written: $json_file"
if [[ $overall_rc -ne 0 ]]; then
  echo 'Collection incomplete: review result exit_code values; unavailable commands remain unknown.' >&2
fi
exit "$overall_rc"
