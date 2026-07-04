# Paper 3 Positive Locus Gate Template

Use this template before any live gnomAD query. A locus that fails this gate is
not a regulatory-positive Paper 3 locus.

## Verdict

- Decision: **YES / NO / NOT YET / REBUILD / STOP**
- Can this locus serve as a clean regulatory-positive locus? **YES / NO / NOT YET**
- Main blocker:
- Next required action:

## Eligibility Checklist

| Check | Status | Evidence |
|---|---|---|
| Non-synthetic rows only | TODO | |
| Real source provenance | TODO | |
| `Position_GRCh38` present | TODO | |
| `Ref` / `Alt` present and queryable | TODO | |
| `HGVS` or equivalent source notation present | TODO | |
| Regulatory subclass supported by source | TODO | |
| Coding/missense/nonsense/frameshift separated | TODO | |
| Primary bottom-5% denominator frozen within locus | TODO | |
| Primary candidate cohort non-empty | TODO | |
| Matched controls non-empty | TODO | |
| Controls are same locus and position/mechanism matched | TODO | |
| Source semantics clean enough for population interpretation | TODO | |
| Candidate dry-run passed | TODO | |
| Control dry-run passed | TODO | |
| Live query row count `<=20` per group | TODO | |
| Live gate justified | TODO | |

## Candidate Count

| Group | n | queryable SNVs | regulatory subclass | bottom-5% | source-clean | live eligible |
|---|---:|---:|---:|---:|---:|---:|
| Candidates | TODO | TODO | TODO | TODO | TODO | TODO |
| Controls | TODO | TODO | TODO | TODO | TODO | TODO |

## Dry-Run Result

Candidate dry-run command:

```powershell
python scripts\population_filter.py --atlas results\TODO_candidates.csv --chrom TODO --cohort-column TODO --cohort-op equals --cohort-value true --locus-name TODO --out TODO_candidates --rate-limit 3.0 --dry-run
```

Control dry-run command:

```powershell
python scripts\population_filter.py --atlas results\TODO_controls.csv --chrom TODO --cohort-column TODO --cohort-op equals --cohort-value true --locus-name TODO_controls --out TODO_controls --rate-limit 3.0 --dry-run
```

| Group | dry-run status | matched rows | blocker |
|---|---|---:|---|
| Candidates | TODO | TODO | TODO |
| Controls | TODO | TODO | TODO |

## Live Eligibility

- Live gnomAD allowed: **YES / NO**
- Reason:
- Required mode: strict first.
- `--treat-not-found-as-absent`: **NO** unless strict failures are only `Variant not found` after coordinate/build sanity checks.

## Candidate vs Controls

| Group | n | successful | not_observed | query_failed | interpretation |
|---|---:|---:|---:|---:|---|
| Candidates | TODO | TODO | TODO | TODO | TODO |
| Controls | TODO | TODO | TODO | TODO | TODO |

## Allowed Claim

TODO: write one cautious sentence. Do not claim validation or proof.

## Not Allowed

- "validates ARCHCODE"
- "multi-locus confirmed"
- "Paper 3 ready"
- "not found proves constraint"
- "ARCHCODE beats VEP/CADD"
- "universal constraint"

## Decision

- **CONTINUE** only if candidates differ from controls and source audit is clean.
- **REBUILD** if useful rows exist but source/category/coordinate audit is incomplete.
- **STOP** if candidates and controls show the same pattern, queryability is broken, or controls are empty.
