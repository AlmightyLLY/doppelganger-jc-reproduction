#!/usr/bin/env python3
"""Run one translation item through the paper's perplexity selection method."""

from __future__ import annotations

import argparse
import math
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("HF_HOME", str(PROJECT_ROOT / ".cache" / "huggingface"))
sys.path.insert(0, str(PROJECT_ROOT))

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from calc_ppl_translation import formatInput
from questions.jp_zh.homographs import dataset


def select_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def perplexity(model, tokenizer, text: str, device: torch.device) -> float:
    inputs = tokenizer(text, return_tensors="pt").to(device)
    with torch.inference_mode():
        output = model(**inputs, labels=inputs["input_ids"])
    return math.exp(output.loss.item())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        default="hf-internal-testing/tiny-random-gpt2",
        help="A small causal language model on Hugging Face.",
    )
    args = parser.parse_args()

    device = select_device()
    print(f"model:  {args.model}")
    print(f"device: {device}")

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model).to(device).eval()

    word, item = next(iter(dataset.items()))
    candidates = [item["correct"], item["wrong1"], item["wrong2"], item["wrong3"]]
    scored = []
    for index, candidate in enumerate(candidates):
        prompt = formatInput(item["target-sentence"], candidate, "zh")
        score = perplexity(model, tokenizer, prompt, device)
        scored.append(score)
        label = "correct" if index == 0 else f"wrong{index}"
        print(f"{index} {label:<7} ppl={score:10.4f}  {candidate}")

    prediction = min(range(len(scored)), key=scored.__getitem__)
    print(f"selected option: {prediction}")
    print("PASS: model download, tokenization, forward pass, and perplexity selection worked.")
    print("The tiny random model is only a pipeline check; its answer is not a research result.")


if __name__ == "__main__":
    main()
