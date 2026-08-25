# Benchmark Data, Provenance, and Public-Artifact Policy

The authoritative benchmark is the public
[`0017-alt/Doppelganger-JC`](https://github.com/0017-alt/Doppelganger-JC)
repository. This study pins commit:

```text
eb1c4f3f17403af238046bf218dc49643bc2e2e2
```

The upstream repository licenses its code under Apache-2.0 but states that the
`cognate_fixed/` and `questions/` data are derived from the *Database of
Japanese Kanji Vocabulary in Contrast to Chinese* and are governed by separate
data terms. Those terms were not interpreted here as an affirmative grant to
republish the benchmark in a second repository. The conservative policy is
therefore to retrieve the data from its authoritative location and avoid
redistributing benchmark or derived intervention text.

Run:

```bash
python3 scripts/bootstrap_upstream.py
```

This creates ignored local links to `questions/`, `cognate_fixed/`, the
upstream scoring script, and the upstream model list. The bootstrap validates
the pinned commit before installing the links.

## What the public artifacts contain

Committed per-item JSONL files retain only:

- `item_index`, dataset flags, and pinned model metadata;
- four-option losses, PPLs, choices, and correctness flags;
- candidate token counts;
- orthography-condition token counts, margins, effects, and analysis metadata.

They do not contain source sentences, candidate translations, target words,
kana rewrites, or control spans. After obtaining the pinned upstream data, a
reader can join scores to benchmark content using `item_index`. The mapping
between complete local-run hashes and redacted public artifacts is recorded in
`results/public-artifacts.manifest.json`.

The constructed orthography material is also not distributed. Its text-free
build config, exposed-item union, package versions, expected counts, and frozen
SHA-256 are committed in `configs/orthography_material_v1.json`. The exact
material is regenerated locally with:

```bash
python scripts/prepare_orthography_control_relevance_full.py
```

The builder refuses a material whose hash differs from the frozen value.

## Automated guard

```bash
make data-check
```

This fails if a published model JSONL contains benchmark text fields, if a
summary or analysis leaks lexical content, or if known bulk review/material
files are reintroduced. This is a repository-safety check, not legal advice.
