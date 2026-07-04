# Domain Invariants (ARCHCODE)

This file enumerates invariants and where they are enforced.

## Implemented invariants

1. CTCF site constraints

- `position >= 0`
- `strength in [0,1]`
  Evidence: `D:\ДНК\src\domain\models\genome.ts`

2. Loop size

- `rightAnchor > leftAnchor`
  Evidence: enforced in engine sanity checks (see below).

3. Genome bounds

- loop anchors must be within `[0, genomeLength]`
  Evidence: enforced in engine sanity checks (see below).

## Runtime sanity checks (engine)

Checks added in `LoopExtrusionEngine`:

- Cohesin legs are finite numbers.
- `leftLeg < rightLeg` after step.
- Loop anchors are finite and within bounds before loop creation.

Evidence:

- `D:\ДНК\src\engines\LoopExtrusionEngine.ts`

## TODO invariants (not yet enforced)

- Resolution > 0 and genomeLength > 0 at config boundary.
- Matrix dimensions consistent across validation scripts.
- Seed presence for reproducibility in all validation pathways.

## Notes

If any invariant is violated at runtime, the engine should log a warning and deactivate the invalid cohesin or skip invalid loop creation.
