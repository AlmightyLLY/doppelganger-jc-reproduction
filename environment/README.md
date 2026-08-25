# Environment Documentation

This directory separates the environments actually recorded for the two
historical GPU batches from the environment currently recommended for a clean
rerun. Earlier documentation collapsed them into one CUDA specification; the
experiment records show that this was inaccurate.

| File | Role | PyTorch build | Shared stack |
|---|---|---|---|
| `requirements-translation-cuda121.txt` | Historical Translation Type-1 batch | `2.5.1+cu121` | Transformers 4.48.3, Accelerate 1.3.0 |
| `requirements-orthography-cuda124.txt` | Historical orthography batch | `2.4.1+cu124` | Transformers 4.48.3, Accelerate 1.3.0 |
| `requirements-cuda.txt` | Current recommended Linux rerun baseline | `2.5.1+cu121` | install `requirements.txt` separately |
| `requirements-macos.txt` | Local development and small-model checks | `2.5.1` | includes `requirements.txt` |
| `requirements.txt` | Platform-independent packages | none | pinned analysis/model packages |

The historical files encode the package versions recorded in the experiment
reports; they are not reconstructed `pip freeze` lockfiles and do not claim
bit-for-bit identity of every transitive wheel, driver, or operating-system
package. The current recommended file is the tested compatibility baseline for
new reruns. A new formal run should preserve a full environment snapshot next
to its private execution log.

## Install choices

For a new Linux GPU rerun:

```bash
python -m pip install -r environment/requirements-cuda.txt
python -m pip install -r environment/requirements.txt
```

To match the recorded dependency lane of one historical batch more closely:

```bash
python -m pip install -r environment/requirements-translation-cuda121.txt
# or, in a separate virtual environment:
python -m pip install -r environment/requirements-orthography-cuda124.txt
```

Do not install the two historical CUDA files into the same virtual environment.

## Minimum record for a new formal run

```bash
python --version
python -m pip freeze
nvidia-smi
```

Also record the CPU, GPU, VRAM, operating system, CUDA driver/runtime, model
revision, dtype, command, seed, and configuration files. Never commit API keys,
access tokens, passwords, or private absolute paths.

The reported 7–8B runs used one NVIDIA A40 with 48 GiB. Local macOS runs were
used for code tracing, data audits, and small-model checks rather than as the
source of the reported 7–8B results.
