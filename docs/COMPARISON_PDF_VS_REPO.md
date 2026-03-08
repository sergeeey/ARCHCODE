# Сравнение: ARCHCODE_v2.15_EN.pdf и текущее состояние репозитория

Источники: препринт `ARCHCODE_v2.15_EN.pdf` (arXiv q-bio.GN 2026-03-04); репозиторий (README, package.json, manuscript/RESULTS.md, скрипты, конфиги). Дата сравнения: 2026-03-06.

---

| Аспект | PDF (v2.15, 2026-03-04) | Текущий репозиторий | Совпадение / расхождение |
|--------|-------------------------|----------------------|---------------------------|
| **Версия** | v2.15 (tagged release в Software) | README: v2.8; package.json: 2.0.0 | Расхождение: в репо нет тега v2.15, указаны v2.8 / 2.0.0. |
| **Препринт** | arXiv q-bio.GN, 2026-03-04 | Тот же препринт (citation в README) | Совпадает. |
| **Варианты** | 30,318 (9 основных локусов); 32,201 с 4 expansion (13 локусов); 30,952 VUS | README: 32,201 + 30,952 VUS = 63,153; 9 основных + 4 expansion, 13 локусов | Совпадает. |
| **Жемчужины (pearl)** | 27 pearl (Abstract, Main Findings); в части текста/таблиц — 20 pearl (Table 2, Pearl summary) | README/репо: 27 pearls; manuscript TABLE_S1/RESULTS: в таблице 2 указано 20, в подписи — 27 | PDF внутренне непоследователен (20 vs 27); репо унифицирован на 27. |
| **Pearl-like VUS** | 760 candidates (LSSIM < 0.95), 641 pearl-like после исключения nonsense/frameshift | README: 641 pearl-like VUS candidates | Совпадает. |
| **AUC HBB** | 0.977; Youden < 0.994; Sens 0.966, Spec 0.988 | README: AUC 0.977, threshold LSSIM < 0.994, Sens 0.966, Spec 0.988 | Совпадает. |
| **LSSIM / пороги** | PATHOGENIC < 0.85; LIKELY 0.85–0.92; VUS 0.92–0.96; LIKELY_BENIGN 0.96–0.99; BENIGN ≥ 0.99; pearl: VEP < 0.30 AND LSSIM < 0.95 | Те же пороги в конфигах и README; pearl: VEP < 0.30, LSSIM < 0.95 | Совпадает. |
| **Hi-C** | K562 r = 0.53 (30 kb), r = 0.59 (95 kb); MLH1 r = 0.59; BRCA1 r = 0.50–0.53; GM12878 r = 0.16 (ns) | README: r = 0.28–0.59, те же выводы | Совпадает. |
| **Кинетика Kramer** | α = 0.92, γ = 0.80, k_base = 0.002; manually calibrated (Gerlich, Hansen, Sabaté 2024) | biophysics.ts / конфиги: те же значения и формулировка | Совпадает. |
| **Локусы** | HBB 1,103; CFTR 3,349; TP53 2,794; BRCA1 10,682; MLH1 4,060; LDLR 3,284; SCN5A 2,488; TERT 2,089; GJB2 469; expansion: HBA1, GATA1, BCL11A, PTEN | README и config/locus: те же локусы и порядок | Совпадает. |
| **Within-category** | HBB: SSIM не добавляет предсказательной силы (p = 1.0); CFTR ΔAUC = −0.012 (p = 0.79); TP53 ΔAUC = +0.032 (p = 0.29); BRCA1/MLH1 значимы при ΔAUC < 0.02 | Описано в README/Limitations и внутренних отчётах | Совпадает. |
| **Virtual CRISPR (V-CRISPR)** | В PDF нет раздела про V-CRISPR или in silico knockout жемчужин | В репо: раздел «In Silico Functional Validation (Virtual CRISPR)» в manuscript/RESULTS.md; скрипт run-virtual-crispr-pearls.ts; TABLE_VCRISPR_TOP3.md; results/virtual_crispr_pearls.json (~17% contact drop, LSSIM ≈ 0.81 для топ-3 pearls) | Репозиторий расширен относительно PDF: добавлен эксперимент V-CRISPR. |
| **Cold-Eye / аудит** | Не упоминается | docs/COLD_EYE_AUDIT_TZ.md, COLD_EYE_AUDIT_REPORT.md; AGENTS.md, CODEX_ZERO_HALLUCINATION_GATES | Репозиторий расширен: процесс аудита и отчёт. |
| **Пайплайн** | generate-unified-atlas.ts; Python: analyze_positional_signal, bayesian_fit_hic, download_clinvar_generic, vep_batch, within_category_analysis; benchmark_alphagenome, benchmark_akita | Те же скрипты + run-virtual-crispr-pearls.ts, scripts/lib/analyticalContact.ts, test_weak_ctcf.ts и др. | Репо содержит всё из PDF плюс новые скрипты. |
| **Zenodo** | DOI: 10.5281/zenodo.18867448 | В README/Citation может быть указан тот же DOI (нужно проверить) | Уточнить наличие DOI в README. |
| **Ограничения** | AUC = category effect; within-category null на HBB; GM12878 Hi-C ns; параметры не fitted; pearl требуют экспериментальной валидации | README Limitations и manuscript: те же пункты плюс AlphaGenome overlap, HBB-centric pearls | Совпадает; в репо ограничения сформулированы явно. |

---

## Краткий вывод

- **Числа и методология:** основные метрики (AUC, LSSIM, пороги, локусы, 27 pearls, 641 pearl-like VUS, Hi-C, Kramer) в репозитории совпадают с PDF.
- **Версия:** в PDF заявлена v2.15, в репо — v2.8 / 2.0.0; тег v2.15 в репо не найден — стоит либо выровнять версию/тег, либо зафиксировать в README, что PDF соответствует v2.15, а текущая разработка — v2.8.
- **Расширения репо относительно PDF:** (1) эксперимент V-CRISPR и подраздел в RESULTS; (2) Cold-Eye аудит (ТЗ и отчёт); (3) AGENTS.md и кодекс zero-hallucination; (4) дополнительные скрипты и артефакты (task1–task5, pearl_validation_shortlist, virtual_crispr_pearls).
- **Внутренняя непоследовательность PDF:** в одном месте 27 pearl, в таблицах/подразделах — 20; в репо везде 27, что согласуется с Abstract и Main Findings PDF.
