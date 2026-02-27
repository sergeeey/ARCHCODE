# Failure Modes Review (ARCHCODE)

This file maps failure modes to detection mechanisms and current status.

| Failure mode           | Description                            | Detection          | Status           | Evidence                                           |
| ---------------------- | -------------------------------------- | ------------------ | ---------------- | -------------------------------------------------- |
| Data/logic leakage     | Mock data used without disclosure      | Manual review only | Needs automation | `D:\ДНК\CLAUDE.md`, `D:\ДНК\KNOWN_ISSUES.md`       |
| Distribution shift     | Validation on different loci/cell type | Manual analysis    | Needs automation | `D:\ДНК\scripts\validate-hic.ts`                   |
| Inverted logic         | Score directionality flipped           | Unit test          | Implemented      | `D:\ДНК\src\__tests__\alphagenome-metrics.test.ts` |
| Silent failure         | Validation runs without artifacts      | Manual review      | Needs automation | `D:\ДНК\results\`                                  |
| Security regression    | Secrets accidentally committed         | Manual review      | Needs automation | `.env`/`.gitignore`                                |
| Performance regression | Large genome/matrix OOM                | Manual observation | Needs automation | `D:\ДНК\KNOWN_ISSUES.md`                           |

## TODO

- Add CI checks for mock-data watermarking.
- Add automated artifact checks (presence + schema validation).
- Add performance baseline for core engine.
