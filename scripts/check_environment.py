#!/usr/bin/env python3
"""Check the minimum Doppelganger-JC runtime without downloading a model."""

from __future__ import annotations

import importlib.util
import platform
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PACKAGES = (
    "accelerate",
    "numpy",
    "protobuf",
    "safetensors",
    "sentencepiece",
    "torch",
    "transformers",
    "transformers-stream-generator",
)
REQUIRED_DATA = (
    "cognate_fixed/jp/homographs.txt",
    "cognate_fixed/zh/homographs.txt",
    "questions/jp_zh/homographs.py",
    "questions/zh_jp/homographs.py",
    "models.txt",
)


def gib(value: int) -> str:
    return f"{value / 1024**3:.1f} GiB"


def main() -> int:
    errors: list[str] = []

    print("Doppelganger-JC environment check")
    print(f"Python:   {platform.python_version()} ({platform.machine()})")
    print(f"Platform: {platform.platform()}")

    if not ((3, 9) <= sys.version_info[:2] <= (3, 12)):
        errors.append("Python must be between 3.9 and 3.12; Python 3.11 is preferred.")

    print("\nPackages:")
    for package in REQUIRED_PACKAGES:
        try:
            installed = version(package)
        except PackageNotFoundError:
            installed = "MISSING"
            errors.append(f"Missing package: {package}")
        print(f"  {package:<31} {installed}")

    if importlib.util.find_spec("torch") is not None:
        import torch

        print("\nCompute:")
        if torch.cuda.is_available():
            index = torch.cuda.current_device()
            props = torch.cuda.get_device_properties(index)
            print(f"  backend                       CUDA {torch.version.cuda}")
            print(f"  device                        {props.name}")
            print(f"  compute capability            {props.major}.{props.minor}")
            print(f"  VRAM                          {gib(props.total_memory)}")
            print(f"  native BF16                   {torch.cuda.is_bf16_supported()}")
            if props.total_memory < 20 * 1024**3:
                print("  NOTE: less than 20 GiB VRAM is tight for the paper's 7-8B models.")
            if not torch.cuda.is_bf16_supported():
                print("  NOTE: use float16 rather than bfloat16 on this GPU.")
        elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            print("  backend                       Apple MPS")
            print("  NOTE: suitable for development and small-model smoke tests.")
            print("        Use NVIDIA CUDA for the paper's full 7-8B experiments.")
        elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_built():
            print("  backend                       CPU (MPS is built but unavailable)")
            print("  NOTE: this PyTorch/macOS combination cannot currently expose Apple MPS.")
            print("        The CPU is still sufficient for the tiny smoke test.")
        else:
            print("  backend                       CPU")
            print("  NOTE: environment checks will work, but full inference will be impractical.")

    print("\nProject data:")
    for relative_path in REQUIRED_DATA:
        exists = (PROJECT_ROOT / relative_path).is_file()
        print(f"  {relative_path:<43} {'OK' if exists else 'MISSING'}")
        if not exists:
            errors.append(f"Missing project file: {relative_path}")

    if errors:
        print("\nFAILED")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("\nOK: the basic runtime and dataset layout are ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
