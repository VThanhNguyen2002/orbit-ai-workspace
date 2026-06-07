#!/usr/bin/env bash
set -Eeuo pipefail

BASE_URL="${SYNAPSE_DEMO_API_BASE_URL:-${1:-http://127.0.0.1:8000}}"
BASE_URL="${BASE_URL%/}"
API_URL="${BASE_URL}/v1"
REQUEST_COUNTER=1

case "${BASE_URL}" in
  http://127.0.0.1 | http://127.0.0.1:* | http://localhost | http://localhost:* | http://[::1] | http://[::1]:*) ;;
  *)
    printf 'Refusing to run: this demo script targets a local backend only.\n' >&2
    printf 'Use http://127.0.0.1:8000 or http://localhost:8000.\n' >&2
    exit 2
    ;;
esac

for required_tool in curl python3; do
  if ! command -v "${required_tool}" >/dev/null 2>&1; then
    printf 'Missing required tool: %s\n' "${required_tool}" >&2
    exit 2
  fi
done

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

info() {
  printf '\n==> %s\n' "$1"
}

ok() {
  printf '    %s\n' "$1"
}

fail() {
  printf '\nDemo stopped: %s\n' "$1" >&2
  exit 1
}

request() {
  local method="$1"
  local path="$2"
  local output_file="$3"
  local payload="${4-}"
  local request_id
  local status
  local -a curl_args

  request_id="req_demo_api_${REQUEST_COUNTER}"
  REQUEST_COUNTER=$((REQUEST_COUNTER + 1))

  curl_args=(
    --silent
    --show-error
    --request "${method}"
    "${API_URL}${path}"
    --header "Accept: application/json"
    --header "x-request-id: ${request_id}"
    --output "${output_file}"
    --write-out "%{http_code}"
  )

  if [[ -n "${payload}" ]]; then
    curl_args+=(--header "Content-Type: application/json" --data "${payload}")
  fi

  if ! status="$(curl "${curl_args[@]}")"; then
    fail "could not reach ${BASE_URL}. Start the local backend first."
  fi

  printf '%s' "${status}"
}

expect_status() {
  local step="$1"
  local actual="$2"
  local expected="$3"

  if [[ "${actual}" != "${expected}" ]]; then
    fail "${step} returned HTTP ${actual}; expected ${expected}."
  fi
}

json_value() {
  local file="$1"
  local expression="$2"

  python3 - "$file" "$expression" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    document = json.load(handle)

value = document
for part in sys.argv[2].split("."):
    if part:
        value = value[int(part)] if part.isdigit() else value[part]

if value is None:
    print("")
else:
    print(value)
PY
}

json_length() {
  local file="$1"
  local expression="$2"

  python3 - "$file" "$expression" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    document = json.load(handle)

value = document
for part in sys.argv[2].split("."):
    if part:
        value = value[int(part)] if part.isdigit() else value[part]

print(len(value))
PY
}

ensure_history_order() {
  local file="$1"
  local first_summary_id="$2"
  local second_summary_id="$3"

  python3 - "$file" "$first_summary_id" "$second_summary_id" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    document = json.load(handle)

items = document["data"]["items"]
if len(items) < 2:
    raise SystemExit("history did not contain two summaries")
if items[0]["id"] != sys.argv[3] or items[1]["id"] != sys.argv[2]:
    raise SystemExit("history is not newest-first for the repeated summaries")
PY
}

NOTE_PAYLOAD='{"title":"Local demo planning note","content":"Synthetic local demo note for the fake-provider API walkthrough. It includes decisions and follow-up items only.","content_type":"plain"}'

cat <<EOF
Synapse local API demo

Target: ${BASE_URL}

This script is local-demo only. It uses dev auth defaults, sends no auth
header, creates no .env file, starts no Docker/Supabase/Expo process, and makes
no live provider calls. Summary history is memory-only and resets with backend
process state.

Expected backend startup:
  cd apps/api
  SYNAPSE_AI_SUMMARIZATION_ENABLED=true uvicorn app.main:app --reload
EOF

info "Checking local backend health"
health_file="${TMP_DIR}/health.json"
health_status="$(request GET /health "${health_file}")"
expect_status "Health check" "${health_status}" "200"
ok "health ok: $(json_value "${health_file}" "data.status")"

info "Creating a synthetic note"
create_file="${TMP_DIR}/create-note.json"
create_status="$(request POST /notes "${create_file}" "${NOTE_PAYLOAD}")"
if [[ "${create_status}" == "401" ]]; then
  fail "notes route returned 401. This demo expects local dev auth mode."
fi
expect_status "Create note" "${create_status}" "201"
note_id="$(json_value "${create_file}" "data.id")"
note_version="$(json_value "${create_file}" "data.version")"
ok "created note ${note_id} at version ${note_version}"

info "Listing notes"
list_file="${TMP_DIR}/list-notes.json"
list_status="$(request GET "/notes?page=1&per_page=20&sort=updated_at&order=desc" "${list_file}")"
expect_status "List notes" "${list_status}" "200"
note_count="$(json_length "${list_file}" "data.items")"
ok "list returned ${note_count} note(s)"

info "Loading note detail"
detail_file="${TMP_DIR}/note-detail.json"
detail_status="$(request GET "/notes/${note_id}" "${detail_file}")"
expect_status "Get note detail" "${detail_status}" "200"
ok "detail loaded for note $(json_value "${detail_file}" "data.id")"

info "Listing empty summary history"
empty_history_file="${TMP_DIR}/summary-history-empty.json"
empty_history_status="$(request GET "/ai/notes/${note_id}/summaries" "${empty_history_file}")"
expect_status "List empty summary history" "${empty_history_status}" "200"
empty_history_count="$(json_length "${empty_history_file}" "data.items")"
ok "summary history contains ${empty_history_count} item(s)"

info "Generating first fake summary"
first_summary_file="${TMP_DIR}/summary-first.json"
first_summary_status="$(request POST "/ai/notes/${note_id}/summarize" "${first_summary_file}")"
if [[ "${first_summary_status}" == "503" ]]; then
  fail "AI summarization is disabled. Restart the local backend with SYNAPSE_AI_SUMMARIZATION_ENABLED=true."
fi
expect_status "Generate first fake summary" "${first_summary_status}" "200"
first_summary_id="$(json_value "${first_summary_file}" "data.id")"
first_provider="$(json_value "${first_summary_file}" "data.provider")"
first_model="$(json_value "${first_summary_file}" "data.model")"
ok "first summary ${first_summary_id} generated by ${first_provider}/${first_model}"

info "Listing summary history after first summary"
first_history_file="${TMP_DIR}/summary-history-first.json"
first_history_status="$(request GET "/ai/notes/${note_id}/summaries" "${first_history_file}")"
expect_status "List summary history after first summary" "${first_history_status}" "200"
first_history_count="$(json_length "${first_history_file}" "data.items")"
ok "summary history contains ${first_history_count} item(s)"

info "Generating second fake summary"
second_summary_file="${TMP_DIR}/summary-second.json"
second_summary_status="$(request POST "/ai/notes/${note_id}/summarize" "${second_summary_file}")"
expect_status "Generate second fake summary" "${second_summary_status}" "200"
second_summary_id="$(json_value "${second_summary_file}" "data.id")"
ok "second summary ${second_summary_id} generated"

info "Verifying newest-first appended history"
final_history_file="${TMP_DIR}/summary-history-final.json"
final_history_status="$(request GET "/ai/notes/${note_id}/summaries" "${final_history_file}")"
expect_status "List final summary history" "${final_history_status}" "200"
ensure_history_order "${final_history_file}" "${first_summary_id}" "${second_summary_id}"
final_history_count="$(json_length "${final_history_file}" "data.items")"
ok "summary history contains ${final_history_count} item(s), newest first"

cat <<EOF

Demo complete.

- Note CRUD route exercised: create, list, detail.
- Fake-provider AI flow exercised: summarize twice, then list history.
- Summary history append/newest-first behavior verified.
- No auth header, provider credential, .env file, Docker, Supabase, Expo, or
  live provider call was used.

Reminder: summary history is memory-only demo state and resets when the backend
process restarts.
EOF
