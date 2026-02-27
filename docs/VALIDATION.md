# ARCHCODE Validation Contract

This contract defines the Anti-Mock Leakage Policy for structural validation.

## Decision Matrix

| Mode          | API Key | API Status    | Result          | Provenance `isFallback` |
| :------------ | :------ | :------------ | :-------------- | :---------------------- |
| `strict-real` | Missing | -             | FATAL ERROR     | -                       |
| `strict-real` | Present | 5xx / Timeout | FATAL ERROR     | -                       |
| `strict-real` | Present | Returns Mock  | FATAL ERROR     | -                       |
| `strict-real` | Present | 200 OK        | SUCCESS         | `false`                 |
| `real`        | Missing | -             | DEGRADED (Mock) | `true`                  |
| `real`        | Present | 5xx / Timeout | DEGRADED (Mock) | `true`                  |
| `mock`        | Any     | Any           | SYNTHETIC       | `false`                 |

## Invariants

1. Any publication-grade validation run must use strict mode (`strict-real`) at the service level.
2. A validation artifact is invalid for publication if provenance indicates local synthetic source.
3. `strict-real` forbids silent fallback: missing key, API failure, or mock-like response must terminate execution.
4. Legacy validation entrypoints must route through `AlphaGenomeService` (no parallel mock path).

## Provenance Contract

`AlphaGenomeService.predict()` must attach:

- `provenance.mode`: `mock | real | strict-real`
- `provenance.source`: explicit source string
- `provenance.apiVersion`: optional API/model version
- `provenance.isFallback`: `true` only when real-mode fallback happened

## PR Gate Checks

1. Fail build if strict mode run does not terminate on missing API key.
2. Fail build if strict mode accepts a mock-like response.
3. Fail build if generated validation artifact contains synthetic provenance for publication pipeline.
