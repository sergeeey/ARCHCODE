// =============================================================================
// template.typ — bioRxiv Preprint Template for ARCHCODE Manuscript
// =============================================================================
// ПОЧЕМУ: Typst позволяет задать layout один раз как функцию и применить ко
// всему документу через show-правило. Это надёжнее LaTeX-пакетов при 2400+
// строках: нет проблем с буферами floats, нет broken packages от CTAN.
// =============================================================================

// -----------------------------------------------------------------------------
// Шрифты: приоритет New Computer Modern → Linux Libertine → системный serif.
// ПОЧЕМУ: NCM — стандарт academic publishing, хорошо рендерит греческие символы
// (α, γ) и математику без внешних пакетов. Linux Libertine — fallback для систем
// без NCM (типичен для Linux CI / Typst web app). Georgia / Times New Roman —
// Windows fallback. Typst автоматически выбирает первый доступный шрифт из списка,
// поэтому порядок критичен: сначала publication-grade, потом system fonts.
// -----------------------------------------------------------------------------
#let body-font = (
  "New Computer Modern",   // Typst встроенный — первый приоритет в Typst web/CI
  "Linux Libertine",       // Linux, некоторые Typst дистрибутивы
  "Georgia",               // Windows: отличный serif, хорошие символы
  "Times New Roman",       // Windows: классический academic fallback
  "serif",                 // Последний рубеж: любой serif системы
)
#let mono-font = (
  "New Computer Modern Mono",  // Typst встроенный моноширинный
  "Consolas",                  // Windows: высококачественный mono
  "Courier New",               // Universal fallback
  "monospace",
)

// -----------------------------------------------------------------------------
// Константы документа
// -----------------------------------------------------------------------------
#let preprint-notice = "Preprint — not peer reviewed"
#let journal-target   = "arXiv q-bio.GN"
#let date-str         = "2026-03-04"

// =============================================================================
// Вспомогательная функция: горизонтальная линия для таблиц
// ПОЧЕМУ: bioRxiv требует "three-line tables" (booktabs-стиль).
// Typst table не имеет встроенного toprule/midrule/bottomrule —
// задаём их вручную через stroke параметры в самой таблице.
// =============================================================================
#let hrule(width: 100%, thickness: 0.5pt) = line(length: width, stroke: thickness)
#let thick-hrule(width: 100%, thickness: 1pt) = line(length: width, stroke: thickness)

// =============================================================================
// Основной шаблон: функция biorxiv-template
// Принимает весь контент документа как единый блок.
// =============================================================================
#let biorxiv-template(
  title: [],
  authors: (),        // array of (name: str, affil: str, email: str)
  abstract: [],
  keywords: (),
  doc,                // основной контент
) = {

  // ---------------------------------------------------------------------------
  // Параметры страницы: US Letter, 1-inch margins, line numbers
  // ПОЧЕМУ: US Letter (8.5×11") — стандарт bioRxiv/PubMed; 1" margin даёт
  // ~6.5" текста, что оптимально для 11pt шрифта без orphans/widows.
  // ---------------------------------------------------------------------------
  set page(
    paper: "us-letter",
    margin: (top: 1in, bottom: 1in, left: 1in, right: 1in),

    // Нумерация строк — слева от текста
    // ПОЧЕМУ: bioRxiv требует line numbers для peer-review, чтобы рецензент
    // мог ссылаться на конкретную строку. Typst поддерживает это нативно.
    numbering: "1",

    // Колонтитул: верхний — preprint notice + название (сокращённое)
    header: context {
      set text(size: 8pt, fill: luma(120))
      grid(
        columns: (1fr, 1fr),
        align(left)[#preprint-notice — #journal-target],
        align(right)[#date-str],
      )
      line(length: 100%, stroke: 0.3pt + luma(180))
    },

    // Нижний колонтитул: номер страницы по центру
    footer: context {
      line(length: 100%, stroke: 0.3pt + luma(180))
      set text(size: 8pt, fill: luma(120))
      align(center)[
        #counter(page).display("1 of 1", both: true)
      ]
    },
  )

  // ---------------------------------------------------------------------------
  // Нумерация строк: включаем для всего документа (peer-review requirement)
  // ---------------------------------------------------------------------------
  set par.line(
    numbering: "1",
    number-align: right,   // номер справа от поля, т.е. левее текста
    number-margin: left,
  )

  // Отключаем нумерацию строк внутри figure (таблицы, изображения)
  // ПОЧЕМУ: line numbers нужны для рецензирования текста, но внутри таблиц
  // и фигур они рендерятся поверх содержимого, делая его нечитаемым.
  show figure: set par.line(numbering: none)

  // Разрешаем таблицам ломаться между страницами
  // ПОЧЕМУ: длинные таблицы (Data Transparency, 27 строк) не помещаются
  // на одну страницу. Без breakable Typst сжимает строки в кашу внизу.
  show figure.where(kind: table): set block(breakable: true)

  // ---------------------------------------------------------------------------
  // Типографика основного текста
  // ПОЧЕМУ: 11pt + 1.5 leading — стандарт bioRxiv. Первый абзац без отступа
  // (как в Nature/Cell), последующие с отступом 1.5em — визуально разделяет
  // параграфы без пустых строк, экономит место.
  // ---------------------------------------------------------------------------
  set text(
    font: body-font,
    size: 11pt,
    lang: "en",
    hyphenate: true,
  )

  set par(
    leading: 0.75em,        // межстрочный интервал (~1.5 при 11pt)
    spacing: 0.75em,        // между абзацами
    first-line-indent: (amount: 1.5em, all: false),  // отступ со второго абзаца
    justify: true,
  )

  // ---------------------------------------------------------------------------
  // Заголовки разделов
  // ПОЧЕМУ: иерархия H1/H2/H3 соответствует структуре рукописи.
  // H1 = крупный раздел (Introduction, Methods, Results, Discussion)
  // H2 = подраздел внутри раздела
  // H3 = под-подраздел (например, конкретный метод)
  // ---------------------------------------------------------------------------
  show heading.where(level: 1): it => {
    v(1.5em, weak: true)
    text(size: 14pt, weight: "bold", font: body-font)[#it.body]
    v(0.6em, weak: true)
  }

  show heading.where(level: 2): it => {
    v(1.2em, weak: true)
    text(size: 12pt, weight: "bold", font: body-font)[#it.body]
    v(0.4em, weak: true)
  }

  show heading.where(level: 3): it => {
    v(1.0em, weak: true)
    text(size: 11pt, weight: "bold", style: "italic", font: body-font)[#it.body]
    v(0.3em, weak: true)
  }

  // ---------------------------------------------------------------------------
  // Код и моноширинные блоки
  // ПОЧЕМУ: рукопись содержит формулы в виде code-блоков (Kramer kinetics,
  // contact matrix formula). Серый фон + мелкий шрифт отличает их от текста
  // без риска путаницы. raw block vs raw inline обрабатываются раздельно.
  // ---------------------------------------------------------------------------
  show raw.where(block: true): it => {
    block(
      fill: luma(245),
      inset: (x: 0.8em, y: 0.6em),
      radius: 3pt,
      width: 100%,
      stroke: 0.4pt + luma(200),
    )[
      #text(font: mono-font, size: 9pt)[#it]
    ]
  }

  show raw.where(block: false): it => {
    box(
      fill: luma(245),
      inset: (x: 0.25em, y: 0.1em),
      radius: 2pt,
    )[
      #text(font: mono-font, size: 9.5pt)[#it]
    ]
  }

  // ---------------------------------------------------------------------------
  // Таблицы: clean scientific style (booktabs)
  // ПОЧЕМУ: scientific journals запрещают вертикальные линии в таблицах.
  // Горизонтальные правила — toprule, midrule, bottomrule — достаточны.
  // Здесь задаём стиль ячеек заголовка таблицы через show.
  // ---------------------------------------------------------------------------
  set table(
    stroke: none,           // убираем все рамки по умолчанию
    inset: (x: 0.5em, y: 0.4em),
  )

  // Заголовок таблицы — bold
  show table.cell.where(y: 0): set text(weight: "bold", size: 10pt)
  show table.cell: set text(size: 10pt)

  // ---------------------------------------------------------------------------
  // Раздел References: мельче шрифт
  // ПОЧЕМУ: References не читаются линейно, их сканируют для проверки.
  // Меньший шрифт (9.5pt) экономит 1–2 страницы при большом списке.
  // ---------------------------------------------------------------------------
  // (применяется внутри content через специальный блок biorxiv-references)

  // ---------------------------------------------------------------------------
  // Списки: компактные, без лишних отступов
  // ---------------------------------------------------------------------------
  set list(indent: 1.5em, spacing: 0.4em)
  set enum(indent: 1.5em, spacing: 0.4em)

  // ===========================================================================
  // РЕНДЕРИНГ ДОКУМЕНТА
  // ===========================================================================

  // ---------------------------------------------------------------------------
  // Titleblock: заголовок + авторы + аффилиации + корреспонденция
  // ---------------------------------------------------------------------------
  align(center)[
    #v(1em)

    // Заголовок
    #text(size: 16pt, weight: "bold", font: body-font)[
      #title
    ]

    #v(1.2em)

    // Авторы
    #for author in authors [
      #text(size: 11pt, weight: "bold")[#author.name]
      #if author.keys().contains("superscript") [
        #super[#author.superscript]
      ]
      #text(size: 11pt)[\ ]
    ]

    #v(0.5em)

    // Аффилиации
    #for (i, author) in authors.enumerate() [
      #if author.keys().contains("affiliation") [
        #text(size: 9.5pt, fill: luma(60))[
          #if authors.len() > 1 [#super[#str(i + 1)]]
          #author.affiliation \
        ]
      ]
    ]

    #v(0.4em)

    // Корреспонденция
    #for author in authors [
      #if author.keys().contains("email") [
        #text(size: 9.5pt)[
          _Correspondence:_ #link("mailto:" + author.email)[#author.email]
        ]
      ]
    ]

    #v(0.4em)

    // Дата и preprint notice
    #text(size: 9pt, fill: luma(80))[
      Preprint submitted to #journal-target • #date-str
    ]

    #v(0.8em)
    #line(length: 100%, stroke: 0.5pt)
  ]

  // ---------------------------------------------------------------------------
  // Abstract: в рамке с отступами
  // ПОЧЕМУ: bioRxiv выделяет abstract визуально. Рамка + серый фон делают его
  // сразу узнаваемым. Ширина 90% центрируется для визуального отделения
  // от основного текста.
  // ---------------------------------------------------------------------------
  if abstract != [] {
    v(1em)
    align(center)[
      #block(
        width: 92%,
        inset: (x: 1.2em, y: 1em),
        stroke: 0.6pt + luma(180),
        fill: luma(252),
        radius: 3pt,
      )[
        #text(size: 11pt, weight: "bold")[Abstract]
        #v(0.4em)
        #set text(size: 10.5pt)
        #set par(first-line-indent: (amount: 0em, all: false))
        #abstract
      ]
    ]
    v(0.5em)
    line(length: 100%, stroke: 0.3pt + luma(200))
    v(1em)
  }

  // ---------------------------------------------------------------------------
  // Основной контент
  // ---------------------------------------------------------------------------
  doc

}

// =============================================================================
// Вспомогательные компоненты (используются в основном документе)
// =============================================================================

// Блок References с уменьшенным шрифтом
// Использование: #biorxiv-references[ ... список литературы ... ]
#let biorxiv-references(content) = {
  v(1em)
  line(length: 100%, stroke: 0.5pt)
  heading(level: 1, "References")
  set text(size: 9.5pt)
  set par(
    leading: 0.6em,
    spacing: 0.5em,
    first-line-indent: (amount: 0em, all: false),
    hanging-indent: 1.5em,
  )
  content
}

// Таблица с booktabs-стилем (toprule / midrule / bottomrule)
// Использование: #scientific-table(columns: ..., header: [...], [...])
// ПОЧЕМУ: инкапсулируем повторяющийся паттерн из 10+ таблиц в рукописи.
// Не нужно вручную расставлять линии в каждой таблице.
#let scientific-table(columns: (), header-rows: 1, ..cells) = {
  // toprule
  line(length: 100%, stroke: 1pt)
  v(-0.3em)

  table(
    columns: columns,
    stroke: (x, y) => {
      // midrule после header строк
      if y == header-rows { (bottom: 0.5pt) }
      else { none }
    },
    ..cells
  )

  // bottomrule
  v(-0.3em)
  line(length: 100%, stroke: 1pt)
}

// Data Transparency Table: специальный стиль для таблицы данных
// с тремя колонками: источник | статус | примечания
#let transparency-table(..rows) = {
  scientific-table(
    columns: (2fr, 1.2fr, 3fr),
    header-rows: 1,
    [*Data source*], [*Status*], [*Notes*],
    ..rows
  )
}

// Статус-бейдж: цветовое кодирование для REAL / COMPUTATIONAL / NOT AVAILABLE
// ПОЧЕМУ: таблица Data Transparency Declaration появляется несколько раз
// в рукописи. Визуальное кодирование делает её сканируемой за 5 секунд.
#let status-badge(s) = {
  let (bg, fg) = if s == "REAL" {
    (rgb("d4edda"), rgb("155724"))
  } else if s == "COMPUTATIONAL" {
    (rgb("cce5ff"), rgb("004085"))
  } else if s == "REAL (positive)" {
    (rgb("d4edda"), rgb("155724"))
  } else if s == "REAL (negative)" {
    (rgb("fff3cd"), rgb("856404"))
  } else if s == "REAL (moderate)" {
    (rgb("fff3cd"), rgb("856404"))
  } else if s == "MANUALLY CALIBRATED" {
    (rgb("e2d9f3"), rgb("432874"))
  } else {
    // NOT AVAILABLE / unknown
    (rgb("f8d7da"), rgb("721c24"))
  }
  box(
    fill: bg,
    inset: (x: 0.35em, y: 0.15em),
    radius: 2pt,
  )[
    #text(size: 8.5pt, fill: fg, weight: "bold")[#s]
  ]
}

// Блок "Limitation" — нумерованный список ограничений
#let limitations(..items) = {
  v(0.5em)
  block(
    stroke: 0.5pt + luma(200),
    fill: luma(252),
    inset: (x: 1em, y: 0.8em),
    radius: 3pt,
    width: 100%,
  )[
    #text(weight: "bold")[Limitations]
    #enum(..items)
  ]
}

// Встроенный "pearl variant" — выделение специальным цветом
#let pearl(content) = {
  box(
    fill: rgb("fff9e6"),
    inset: (x: 0.2em, y: 0.05em),
    radius: 2pt,
  )[#content]
}
