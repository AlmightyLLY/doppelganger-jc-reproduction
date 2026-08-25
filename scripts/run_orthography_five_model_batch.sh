#!/usr/bin/env bash
set -uo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_dir="${1:-$(dirname "$script_dir")}"
python_bin="${2:-python3}"
material="$project_dir/results/causal/orthography-control-relevance-full-v1.jsonl"
result_dir="$project_dir/results/local/orthography-batch"
smoke_dir="$project_dir/results/local/orthography-batch-smoke"
log_dir="$project_dir/results/local/logs"
status_file="$log_dir/orthography-five-model-batch-status.tsv"

mkdir -p "$result_dir" "$smoke_dir" "$log_dir"
printf 'model\tstage\tstatus\toutput\n' > "$status_file"

models=(
  'llm-jp/llm-jp-3-7.2b-instruct3'
  'elyza/Llama-3-ELYZA-JP-8B'
  'baichuan-inc/Baichuan2-7B-Base'
  'mistralai/Mistral-7B-Instruct-v0.2'
  'google/gemma-7b'
)
revisions=(
  'cdd4c7f3296fdc7785423a864bd9a86ce4c15915'
  'e6c316496ee7d9a11710c50229e8cb39b6b0a4a3'
  'f9d4d8dd2f7a3dbede3bda3b0cf0224e9272bbe5'
  '63a8b081895390a26e140280378bc85ec8bce07a'
  'ff6768d9368919a1f025a54f9f5aa0ee591730bb'
)
slugs=(
  'llm-jp--llm-jp-3-7.2b-instruct3'
  'elyza--Llama-3-ELYZA-JP-8B'
  'baichuan-inc--Baichuan2-7B-Base'
  'mistralai--Mistral-7B-Instruct-v0.2'
  'google--gemma-7b'
)

export HF_HOME="${HF_HOME:-$project_dir/.cache/huggingface}"
export TOKENIZERS_PARALLELISM=false
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128

cd "$project_dir" || exit 2

for index in "${!models[@]}"; do
  model="${models[$index]}"
  revision="${revisions[$index]}"
  slug="${slugs[$index]}"
  smoke_output="$smoke_dir/${slug}-orthography-control-relevance-smoke-n3.jsonl"
  full_output="$result_dir/${slug}-orthography-control-relevance-full-v1.jsonl"
  smoke_log="$log_dir/${slug}-orthography-control-relevance-smoke-n3.log"
  full_log="$log_dir/${slug}-orthography-control-relevance-full-v1.log"

  printf '%s\tsmoke\trunning\t%s\n' "$model" "$smoke_output" >> "$status_file"
  if ! "$python_bin" -u scripts/run_orthography_control_relevance_full.py \
      --material "$material" \
      --model "$model" \
      --revision "$revision" \
      --device cuda \
      --limit 3 \
      --output "$smoke_output" > "$smoke_log" 2>&1; then
    printf '%s\tsmoke\tfailed\t%s\n' "$model" "$smoke_output" >> "$status_file"
    continue
  fi
  if ! "$python_bin" scripts/validate_orthography_control_relevance_full_output.py \
      "$smoke_output" \
      --expected-items 3 \
      --expected-related 2 \
      --expected-revision "$revision" >> "$smoke_log" 2>&1; then
    printf '%s\tsmoke-validation\tfailed\t%s\n' "$model" "$smoke_output" >> "$status_file"
    continue
  fi
  printf '%s\tsmoke\tpassed\t%s\n' "$model" "$smoke_output" >> "$status_file"

  printf '%s\tfull\trunning\t%s\n' "$model" "$full_output" >> "$status_file"
  if ! "$python_bin" -u scripts/run_orthography_control_relevance_full.py \
      --material "$material" \
      --model "$model" \
      --revision "$revision" \
      --device cuda \
      --local-files-only \
      --output "$full_output" > "$full_log" 2>&1; then
    printf '%s\tfull\tfailed\t%s\n' "$model" "$full_output" >> "$status_file"
    continue
  fi
  if ! "$python_bin" scripts/validate_orthography_control_relevance_full_output.py \
      "$full_output" \
      --expected-items 450 \
      --expected-related 411 \
      --expected-revision "$revision" >> "$full_log" 2>&1; then
    printf '%s\tfull-validation\tfailed\t%s\n' "$model" "$full_output" >> "$status_file"
    continue
  fi
  printf '%s\tfull\tpassed\t%s\n' "$model" "$full_output" >> "$status_file"
done

printf 'batch\tall\tfinished\t%s\n' "$status_file" >> "$status_file"
