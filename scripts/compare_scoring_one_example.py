#!/usr/bin/env python3
"""Compare full-prompt and candidate-only scoring on one real model.

The full-prompt score follows the official repository: average next-token loss
over the complete prompt. The candidate-only score uses the same forward pass
but averages loss only over tokens belonging to the candidate translation.
"""

from __future__ import annotations

import argparse
import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("HF_HOME", str(PROJECT_ROOT / ".cache" / "huggingface"))
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
sys.path.insert(0, str(PROJECT_ROOT))

import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

from calc_ppl_translation import formatInput
from questions.jp_zh.homographs import dataset as JP_ZH_DATASET
from questions.zh_jp.homographs import dataset as ZH_JP_DATASET


DEFAULT_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"


@dataclass(frozen=True)
class Score:
    full_loss: float
    full_ppl: float
    candidate_loss: float
    candidate_ppl: float
    full_token_count: int
    candidate_tokens: tuple[str, ...]


def select_device(requested: str) -> torch.device:
    if requested != "auto":
        return torch.device(requested)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def select_dtype(device: torch.device) -> torch.dtype:
    if device.type == "cuda":
        return torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    if device.type == "mps":
        return torch.float16
    return torch.float32


def candidate_span(
    original: str,
    candidate: str,
    to_lang: str = "zh",
) -> tuple[str, int, int]:
    if to_lang == "zh":
        prefix = f'「{original}」的中文翻译是"'
        suffix = '".'
    elif to_lang == "jp":
        prefix = f'“{original}”という中国語の文章の日本語訳は「'
        suffix = '」です。'
    else:
        raise ValueError(f"Unsupported target language: {to_lang}")

    prompt = formatInput(original, candidate, to_lang)
    expected = f"{prefix}{candidate}{suffix}"
    if prompt != expected:
        raise ValueError("The prompt template changed; candidate offsets are no longer valid.")
    start = len(prefix)
    return prompt, start, start + len(candidate)


def encode_with_offsets(tokenizer, prompt: str):
    """Tokenize a prompt and return character offsets for fast or SentencePiece tokenizers.

    Hugging Face fast tokenizers expose ``offset_mapping`` directly.  Baichuan2
    ships only a slow tokenizer, but its underlying SentencePiece processor can
    return the same raw-text boundaries through an immutable proto.  We align
    those SentencePiece IDs inside the final encoded sequence so any model-added
    special tokens retain empty offsets and cannot enter the candidate mask.
    """
    if getattr(tokenizer, "is_fast", False):
        encoded = tokenizer(
            prompt,
            return_offsets_mapping=True,
            return_tensors="pt",
        )
        offsets = encoded.pop("offset_mapping")[0]
        return encoded, offsets

    sentencepiece = getattr(tokenizer, "sp_model", None)
    if sentencepiece is None or not hasattr(
        sentencepiece, "encode_as_immutable_proto"
    ):
        raise RuntimeError(
            "Candidate-only scoring requires either a fast tokenizer with offset "
            "mappings or a slow SentencePiece tokenizer exposing immutable-proto "
            "character boundaries."
        )

    encoded = tokenizer(prompt, return_tensors="pt")
    proto = sentencepiece.encode_as_immutable_proto(prompt)
    piece_ids = [int(piece.id) for piece in proto.pieces]
    piece_offsets = [(int(piece.begin), int(piece.end)) for piece in proto.pieces]
    input_ids = encoded["input_ids"][0].tolist()

    matches = [
        start
        for start in range(len(input_ids) - len(piece_ids) + 1)
        if input_ids[start : start + len(piece_ids)] == piece_ids
    ]
    if len(matches) != 1:
        raise RuntimeError(
            "Could not uniquely align SentencePiece IDs with the encoded prompt."
        )

    piece_start = matches[0]
    piece_end = piece_start + len(piece_ids)
    special_ids = set(getattr(tokenizer, "all_special_ids", ()))
    outside_piece_ids = input_ids[:piece_start] + input_ids[piece_end:]
    if any(token_id not in special_ids for token_id in outside_piece_ids):
        raise RuntimeError(
            "Non-special tokens appeared outside the aligned SentencePiece span."
        )

    offsets = [(0, 0)] * len(input_ids)
    offsets[piece_start:piece_end] = piece_offsets
    return encoded, offsets


def score_candidate(
    model,
    tokenizer,
    original: str,
    candidate: str,
    device: torch.device,
    to_lang: str = "zh",
) -> Score:
    prompt, candidate_start, candidate_end = candidate_span(
        original, candidate, to_lang
    )
    encoded, offsets = encode_with_offsets(tokenizer, prompt)
    model_inputs = {name: tensor.to(device) for name, tensor in encoded.items()}

    with torch.inference_mode():
        logits = model(**model_inputs).logits

    # token_nll[i] is the loss for predicting input_ids[i + 1].
    shifted_logits = logits[:, :-1, :].float()
    shifted_labels = model_inputs["input_ids"][:, 1:]
    token_nll = F.cross_entropy(
        shifted_logits.transpose(1, 2),
        shifted_labels,
        reduction="none",
    )[0]

    full_loss = token_nll.mean()
    target_offsets = offsets[1:]
    candidate_mask = torch.tensor(
        [
            int(end) > candidate_start and int(start) < candidate_end
            for start, end in target_offsets
        ],
        dtype=torch.bool,
        device=token_nll.device,
    )
    if not candidate_mask.any():
        raise RuntimeError("Tokenizer offsets did not identify any candidate tokens.")

    candidate_loss = token_nll[candidate_mask].mean()
    candidate_ids = shifted_labels[0][candidate_mask].tolist()
    candidate_tokens = tuple(
        tokenizer.decode([token_id], clean_up_tokenization_spaces=False)
        for token_id in candidate_ids
    )

    return Score(
        full_loss=full_loss.item(),
        full_ppl=math.exp(full_loss.item()),
        candidate_loss=candidate_loss.item(),
        candidate_ppl=math.exp(candidate_loss.item()),
        full_token_count=model_inputs["input_ids"].shape[1],
        candidate_tokens=candidate_tokens,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument(
        "--direction",
        default="jp_zh",
        choices=("jp_zh", "zh_jp"),
        help="Translation direction: Japanese-to-Chinese or Chinese-to-Japanese.",
    )
    parser.add_argument(
        "--revision",
        help="Pin the exact Hugging Face model commit used for this run.",
    )
    parser.add_argument(
        "--device",
        default="auto",
        choices=("auto", "cpu", "mps", "cuda"),
    )
    parser.add_argument(
        "--local-files-only",
        action="store_true",
        help="Do not access Hugging Face; useful for testing an already cached model.",
    )
    args = parser.parse_args()

    if args.direction == "jp_zh":
        dataset = JP_ZH_DATASET
        to_lang = "zh"
    else:
        dataset = ZH_JP_DATASET
        to_lang = "jp"

    device = select_device(args.device)
    dtype = select_dtype(device)
    print(f"model:  {args.model}")
    print(f"direction: {args.direction}")
    print(f"device: {device}")
    print(f"dtype:  {dtype}")
    print("首次运行会先下载模型；看到下载进度条属于正常现象。\n")

    tokenizer = AutoTokenizer.from_pretrained(
        args.model,
        revision=args.revision,
        local_files_only=args.local_files_only,
        trust_remote_code=True,
    )

    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        revision=args.revision,
        torch_dtype=dtype,
        low_cpu_mem_usage=True,
        local_files_only=args.local_files_only,
        trust_remote_code=True,
    ).to(device).eval()
    parameter_count = sum(parameter.numel() for parameter in model.parameters())
    print(f"parameters: {parameter_count / 1e9:.3f}B\n")

    word, item = next(iter(dataset.items()))
    original = item["target-sentence"]
    fields = ("correct", "wrong1", "wrong2", "wrong3")
    results: list[Score] = []

    print(f"word:     {word}")
    print(f"original: {original}\n")
    for index, field in enumerate(fields):
        candidate = item[field]
        result = score_candidate(
            model, tokenizer, original, candidate, device, to_lang=to_lang
        )
        results.append(result)
        print(f"candidate {index} ({field}): {candidate}")
        print(f"  candidate tokens: {list(result.candidate_tokens)}")
        print(
            f"  official/full     tokens={result.full_token_count:>2}  "
            f"loss={result.full_loss:>9.6f}  PPL={result.full_ppl:>10.3f}"
        )
        print(
            f"  candidate-only    tokens={len(result.candidate_tokens):>2}  "
            f"loss={result.candidate_loss:>9.6f}  PPL={result.candidate_ppl:>10.3f}"
        )

    official_index = min(range(len(results)), key=lambda i: results[i].full_ppl)
    candidate_index = min(range(len(results)), key=lambda i: results[i].candidate_ppl)

    print("\n=== comparison ===")
    print(
        f"official/full-prompt choice:  {official_index} "
        f"({fields[official_index]})  correct={official_index == 0}"
    )
    print(
        f"candidate-only choice:        {candidate_index} "
        f"({fields[candidate_index]})  correct={candidate_index == 0}"
    )
    print(f"same ranking winner:          {official_index == candidate_index}")


if __name__ == "__main__":
    main()
