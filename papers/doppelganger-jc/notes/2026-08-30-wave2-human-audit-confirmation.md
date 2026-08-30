# Wave 2 Human-Audit Confirmation

Date: 2026-08-30
Researcher: LIU Lingyun

## Status

Three Wave 2 review workbooks have been completed and frozen as
researcher-confirmed development annotations. The entries were initially
prepared through an assisted prefill workflow, then personally checked and
explicitly accepted by Lingyun.

This status means:

- the final annotation authority is Lingyun;
- the judgments may be used for the next development-stage data-cleaning gate;
- they are not independent double-human annotation;
- they are not Japanese native-speaker adjudication;
- they are not an untouched confirmatory test set.

## Audit summary

| Packet | Rows | Confirmed fields | Frozen outcome summary |
|---|---:|---:|---|
| Wave 2 Japanese–Chinese review | 13 | 91 | 10 ACCEPT, 3 REVISE, 0 REJECT |
| Chinese target-only audit | 9 | 81 | All rows completed; one carrier-leakage flag and two trivial-rejection flags |
| Bilingual semantic audit | 9 | 81 | 5 ACCEPT, 3 REVISE, 1 REJECT |

The frozen judgments preserve the documented cautions rather than upgrading
every row mechanically to `ACCEPT`. Items marked `REVISE` or `REJECT` must be
repaired or excluded before they enter a later experimental manifest.

## Public/private boundary

The complete workbooks remain in the repository's ignored local
`research_notes/` workspace because they contain source sentences, candidate
materials, and blind-review information. They are not published in this public
repository. This note and the accompanying machine-readable manifest preserve
their status, aggregate outcomes, paths, and SHA-256 hashes without
redistributing the underlying review material.

No model run or downstream experiment is authorized by this confirmation
record alone.
