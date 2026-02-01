# 🧭 FAQ: AlphaGenome + ARCHCODE

## Источник вопросов
- **Getting a free API key** (отчёт 01.02.2026, новая тема, 4 просмотра, 0 ответов) — пользователи не понимают, как вообще получить ключ и куда его вставить.
- **AlphaGenome: Nature Publication & weights for academic use** (299 просмотров, 2 лайка) — интерес к релизу модели/весов и к тому, как ARCHCODE может к нему подтянуться.
- **Is there a way to obtain embeddings?**, **How to use a different GENCODE version…**, **How are people using Illumina bulk RNA-seq…**, **Is full fine-tuning feasible on a single H100?** — масштабный интерес к гибкости входных данных, версии материалов и производительности.
- Визуализационные темы (“Splice Junction Plot”, “How to interpret junction_End starting in an intron?”, “How to display track names…”) показывают, что нужна помощь с интерпретацией тепловых карт, P(s) и raw scores.

Все цитаты и статистика взяты из отчётов `AlphaGenome_Latest_Report.md` и `AlphaGenome_Full_Report.md` за 01.02.2026.

## 1. Как получить и использовать AlphaGenome API-ключ?
**Проблема:** новая тема “Getting a free API key” висит без ответов — значит, многие не знают ни порядок, ни место для ключа в ARCHCODE.

**Что делать:**
1. Перейди на deepmind.google.com/science/alphagenome и нажми “Get API key”.
2. В описании use case укажи “Research on chromatin loop extrusion modeling”.
3. После получения ключа вставь его в UI (раздел “🔑 AlphaGenome API Key”) или пропиши в `.env`/скриптах (`export ALPHAGENOME_API_KEY=...`/`scripts/validate-alphagenome.js -k`).
4. Для контроля вызовов используем mock-переключатель — ключ должен применяться только в режиме валидации; для всех остальных сценариев работаем по умолчанию (см. `docs/ALPHAGENOME.md`).

## 2. Где взять веса / публикацию?
- Тема “alphaGenome Nature Publication & weights for academic use” собрала 299 просмотров, что говорит о спросе на академический доступ к модели.

**Решение:**
1. Приведи в `docs/ALPHAGENOME.md` ссылку на Nature-публикацию и репозиторий DeepMind, чтобы пользователи не переходили на внешние форумы.
2. Включи краткий блок “Что нового” в `ARCHCODE` (можно в `docs/STRATEGY.md` или `README`), в котором показываешь: “модель опубликована; мы сохраняем mock, но при наличии ключа можно валидировать”.
3. Предложи pipeline: симуляция → mock → валидация с реальными весами, как в секции “Примеры использования” документа.

## 3. Подготовка данных (GENCODE, Illumina, embeddings)
**Факты:** топики про GENCODE v49, Illumina bulk RNA-seq и embeddings (тема #testing) — это постоянные вопросы по входным данным.

**Рекомендации:**
- Предоставь готовые скрипты/примеры преобразования BED/VCF в нужный формат (см. `scripts/`), добавь ссылку на `docs/METHODS.md`.
- Добавь раздел “Data prep” в FAQ:
  - Как нормализовать варианты (`bcftools norm`) перед тем, как подавать в ARCHCODE (см. рекомендации из форума “coordinate change when predicting long variants”).
  - Как использовать разные версии GENCODE — сохранять маппинг и обновлять константы `domain/constants`.
  - Как загружать Illumina bulk RNA-seq в `data/` и привязывать к симуляции (чтоб было похоже на “How are people using Illumina bulk RNA-seq?”).
  - Что такое embeddings и как их читать: хранить их вместе с heatmap и использовать `validation/` утилиты для визуального сравнения (вспомним “Is there a way to obtain embeddings?”).

## 4. Интерпретация результатов и визуализация
Пользователи спрашивают про junction plots и значения над сплайсами, поэтому дайте отчётливые инструкции:
1. Покажите, как в ARCHCODE отображаются петли (3D viewer + contact matrix) и почему изменения связаны с ориентацией CTCF.
2. Добавьте подписи (например, “Left leg”, “Right leg”, “Loop formed”) рядом с тепловой картой, как это описано в “Splice Junction Plot” и “How to interpret junction_End starting in an intron?”.
3. Предоставьте галерею (“Визуализация + объяснение”), в которую входят P(s) curve, diffusion map и raw scores (как в Discord-топиках), чтобы пользователи видели, что делает корреляция.

## 5. Fine-tuning и производительность
**Тема:** “Is full fine-tuning feasible on a single H100?” показывает, что нужна информация о ресурсах.

**Ответ:**
- В FAQ изложить, что ARCHCODE — физическая симуляция, потому fine-tuning (как в DeepMind) не применяется, но:
  - Если хочешь сравнить с AlphaGenome, делай Grid search: `scripts/grid-search.ts` + `validation/`.
  - В документации указать рекомендуемые параметры (velocity 500–2000 bp/s, numCohesins 20, processivity 600 kb) и производительность на разных GPU/CPU (например, H100, RTX 4090).
- Указать, какие отчёты использовать, чтобы показать “Pearson r ≥ 0.7” (см. секцию “Validation” в `README`).

## 6. Обратная связь и community-led roadmap
1. Используй парсер, чтобы каждую неделю отслеживать “новые темы” и включать их в цифровую доску (например, `docs/STRATEGY.md` или `SESSION_REPORT_2026-02-02.md`).
2. В FAQ добавь восемь последних тем (см. `AlphaGenome_Report_20260201.html`) и связывай каждую с существующей функцией комнаты/предстоящим тикетом.
3. Для тем без ответов (например, “Getting a free API key”) напиши “Если нужной информации нет — пиши на ARCHCODE Slack/email, команда ответит за 24 часа”.

## Что дальше
1. **Материализация FAQ** — разместите `docs/ALPHAGENOME_FAQ.md` на сайте вместе с [ALPHAGENOME.md](./ALPHAGENOME.md) и включите в `README`.
2. **Автоматическое обновление** — используйте парсер для определения популярных тем и добавляйте их в блок “Текущие болевые точки” в релизных заметках.
3. **Обучающие материалы** — снимите короткие видео/анимации (см. `docs/COGNITIVE_CORE.md`), которые иллюстрируют рекомендации из FAQ (особенно data prep и visual cues).
