# Contributing to ARCHCODE

Thank you for your interest in ARCHCODE. This project is an active research tool submitted as a bioRxiv preprint, and we welcome contributions that improve its scientific rigor, extend its capabilities, or fix bugs.

## Scientific Integrity Protocol

All contributions must comply with the [Scientific Integrity Protocol](./CLAUDE.md). In particular:

- **No phantom references** — every DOI must resolve
- **No invisible synthetic data** — mock data must be clearly watermarked
- **No hardcoded "fitted" parameters** without fitting code and data
- **Transparent provenance** — label parameters as MEASURED, CALIBRATED, or ASSUMED

## Development Setup

```bash
git clone https://github.com/sergeeey/ARCHCODE.git
cd ARCHCODE
npm install
npm test          # Run Vitest test suite
npm run build     # TypeScript compilation + Vite build
```

## Code Style

- **TypeScript**: strict mode, no `any`, explicit return types for public functions
- **Python** (scripts): PEP 8, type hints, Black formatter
- **Commits**: [Conventional Commits](https://www.conventionalcommits.org/) — `feat:`, `fix:`, `docs:`, `test:`, `refactor:`

## Pull Request Process

1. Create a feature branch from `main` (`feat/your-feature` or `fix/your-fix`)
2. Ensure all tests pass: `npm test`
3. Review the [PR Gate checklist](./PR_GATE.md) before submitting
4. Open a PR with a clear description of changes and their scientific rationale
5. At least one reviewer must approve before merge

## Reporting Issues

Use the [issue templates](./.github/ISSUE_TEMPLATE/) to report bugs or request features. For scientific questions about the methodology, please open a Discussion or contact the author directly.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](./LICENSE).
