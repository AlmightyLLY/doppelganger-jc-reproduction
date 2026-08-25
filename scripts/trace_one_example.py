#!/usr/bin/env python3
"""Print every important intermediate value for one translation example.

This deliberately uses a tiny randomly initialized Qwen2 model. The matching
Qwen tokenizer is real, but no research-model weights are downloaded. The
script teaches the evaluation mechanics; its prediction is not a result.
"""

from __future__ import annotations

import math
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("HF_HOME", str(PROJECT_ROOT / ".cache" / "huggingface"))
sys.path.insert(0, str(PROJECT_ROOT))

import torch
from transformers import AutoTokenizer, Qwen2Config, Qwen2ForCausalLM

from calc_ppl_translation import formatInput
from questions.jp_zh.homographs import dataset


TOKENIZER_NAME = "Qwen/Qwen2.5-0.5B-Instruct"


def select_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def build_tiny_random_model(vocab_size: int, device: torch.device):
    torch.manual_seed(7)
    config = Qwen2Config(
        vocab_size=vocab_size,
        hidden_size=64,
        intermediate_size=128,
        num_hidden_layers=2,
        num_attention_heads=4,
        num_key_value_heads=2,
        max_position_embeddings=512,
        tie_word_embeddings=True,
    )
    return Qwen2ForCausalLM(config).to(device).eval()


def score(model, tokenizer, prompt: str, device: torch.device):
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    with torch.inference_mode():
        outputs = model(**inputs, labels=inputs["input_ids"])
    loss = outputs.loss.item()
    return inputs["input_ids"][0].tolist(), loss, math.exp(loss)


def main() -> None:
    device = select_device()
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_NAME, local_files_only=True)
    model = build_tiny_random_model(len(tokenizer), device)

    word, item = next(iter(dataset.items()))
    candidate_fields = ("correct", "wrong1", "wrong2", "wrong3")

    print("=== 1. 原始数据 ===")
    print(f'word            = {word!r}')
    print(f'target-sentence = {item["target-sentence"]!r}')
    for index, field in enumerate(candidate_fields):
        print(f'candidate {index}     = QADataset[word]["{field}"] = {item[field]!r}')

    prompts = [
        formatInput(item["target-sentence"], item[field], "zh")
        for field in candidate_fields
    ]

    print("\n=== 2. s1 与 s2 的实际值 ===")
    print(f"s1 = {prompts[0]}")
    print(f"s2 = {prompts[1]}")
    print("相同部分：target-sentence；变化部分：correct → wrong1")

    first_ids = tokenizer(prompts[0], return_tensors="pt")["input_ids"][0].tolist()
    first_tokens = [
        tokenizer.decode([token_id], clean_up_tokenization_spaces=False)
        for token_id in first_ids
    ]
    print("\n=== 3. correct 提示经过 tokenizer ===")
    print(f"token 数量 = {len(first_ids)}")
    print(f"{'位置':>4} {'token ID':>9}  解码后的 token")
    for position, (token_id, token) in enumerate(zip(first_ids, first_tokens)):
        print(f"{position:>4} {token_id:>9}  {token!r}")

    print("\n=== 4. 四个候选的 loss 与 PPL ===")
    print(f"教学模型：随机初始化的微型 Qwen2（仅使用真实 Qwen tokenizer）")
    print(f"设备：{device}")
    scores = []
    for index, (field, prompt) in enumerate(zip(candidate_fields, prompts)):
        token_ids, loss, ppl = score(model, tokenizer, prompt, device)
        scores.append(ppl)
        prediction_count = len(token_ids) - 1
        print(
            f"candidate {index} ({field:<7})  "
            f"预测 {prediction_count:>2} 个下一 token  "
            f"平均 loss={loss:.6f}  PPL={ppl:.3f}"
        )

    min_index = min(range(len(scores)), key=scores.__getitem__)
    print("\n=== 5. 最终评分 ===")
    print(f"ppls      = {[round(value, 3) for value in scores]}")
    print(f"min_index = {min_index}")
    print(f"模型选择  = {candidate_fields[min_index]}")
    print(f"是否得分  = {min_index == 0}（只有 candidate 0/correct 才计 1 分）")
    print("\n注意：随机教学模型的选择没有研究意义；这里验证的是代码执行过程。")


if __name__ == "__main__":
    main()
