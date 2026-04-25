---
tags:
  - project-card
  - infompemba
  - research
  - physics
  - mpemba
  - langevin
created: '2026-04-12'
updated: '2026-04-15'
status: paper-ready
---
# InfoMpemba

**Одно предложение:** Эффект Мпемба в overdamped Langevin динамике зависит от наблюдаемой: basin occupancy показывает crossing, energy и position variance -- нет.
**Статус:** Paper READY (v1, 6 pages REVTeX, 4 figures). Endorsement pending.
**Стек:** Python 3.11, NumPy, SciPy, Matplotlib
**Где:** E:\Метрологический эффект Мпемба в информационной геометрии нейросетей
**Paper:** paper/preprint.tex, compiled to PDF (6 pages)

## Главный результат

Горячее остывает быстрее холодного -- но только если смотришь правильную величину.

Одни и те же частицы, одна и та же симуляция -- но вывод "есть Mpemba или нет" зависит от того, ЧТО измеряешь:

| Наблюдаемая | Crossing | Значение |
|-------------|----------|----------|
| Basin occupancy (p left) | 94.7% (30/30 seeds) | Горячее побеждает |
| Energy | 0% | Эффекта нет |
| Position variance | 0% | Эффекта нет |

Это observable-specificity -- не было показано в явном виде до нас.

## Механизм (4 из 4 контроля verified)

1. Basin imbalance: горячие частицы стартуют в обоих колодцах (близко к равновесию), холодные застревают в одном
2. Balanced cold: 43% (шум) -- эффект убит
3. Single-well: 50% (шум) -- нет метастабильности, нет эффекта
4. Gradient clipping control: 94.6% vs 94.8% -- не артефакт
5. 30 из 30 seeds STRONG

## Количественные результаты

- 720 симуляций (9 barriers x 8 temperatures x 10 seeds)
- Фазовая диаграмма: эффект сильный при b=0.5-2.0, T=0.1-0.2
- Пик: 95.4% при b=2.0, T=0.2
- Fokker-Planck спектральный анализ предсказывает все 25 strong points (recall=100%)
- Kramers formula (1940): предсказывает lambda-1 с 89% точностью (within factor 2, median ratio 1.03)
- p-left проецируется на медленную моду (inter-basin), energy -- на быстрые (intra-basin)

## ML track -- NOT CONFIRMED (negative result)

- MLP + FashionMNIST: нет дискретных бассейнов, нет basin-imbalance Mpemba
- Cold drift +7400% -- experimental design невалиден
- Negative result включён в paper как Supplemental Material

## Paper status

- Text (Introduction -- Conclusion): DONE
- 14 references (all DOI-verified): DONE
- 4 figures (PNG, compiled): DONE
- Supplemental (ML negative): DONE
- LaTeX (REVTeX PRE, 6 pages): DONE, compiled
- arXiv bundle (tar.gz): DONE, on Desktop
- Endorser emails (Raz, Bechhoefer, Goold): DRAFTED in Gmail
- Research Square submission: TODO (user to upload PDF manually)
- Gmail draft to Raz (oren.raz@weizmann.ac.il): READY (user to attach PDF and send)
- Gmail drafts to Bechhoefer + Goold: READY (backup, send if Raz silent 3 days)

## Submission plan

- arXiv cond-mat.stat-mech. Endorsement needed.
- Priority: Oren Raz (Weizmann) -- наш paper реализует его Lu and Raz 2017 spectral criterion
- Backup: Bechhoefer (SFU), Goold (Trinity Dublin)
- Research Square: параллельно, мгновенный DOI
- Target journal: Physical Review E, Rapid Communication
- Alternative: J. Stat. Mech. Letter

## Оценка (2026-04-14)

- Gap: 10 из 10 -- observable-specificity мало исследована
- Готовность: 9 из 10 -- paper compiled, figures ready, endorser emails drafted
- Impact: solid PRE paper. Новый угол на известный эффект, воспроизводимый, с механизмом

up:: [[Каталог всех проектов 2026]]
