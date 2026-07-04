// =============================================================================
// template_ru.typ — Russian Version of bioRxiv Preprint Template
// =============================================================================

#let body-font = (
  "New Computer Modern",
  "Linux Libertine",
  "Georgia",
  "Times New Roman",
  "serif",
)
#let mono-font = (
  "New Computer Modern Mono",
  "Consolas",
  "Courier New",
  "monospace",
)

#let preprint-notice = "Препринт — без рецензирования"
#let journal-target   = "arXiv q-bio.GN"
#let date-str         = "2026-03-04"

#let hrule(width: 100%, thickness: 0.5pt) = line(length: width, stroke: thickness)
#let thick-hrule(width: 100%, thickness: 1pt) = line(length: width, stroke: thickness)

#let biorxiv-template(
  title: [],
  authors: (),
  abstract: [],
  keywords: (),
  doc,
) = {

  set page(
    paper: "us-letter",
    margin: (top: 1in, bottom: 1in, left: 1in, right: 1in),
    numbering: "1",
    header: context {
      set text(size: 8pt, fill: luma(120))
      grid(
        columns: (1fr, 1fr),
        align(left)[#preprint-notice — #journal-target],
        align(right)[#date-str],
      )
      line(length: 100%, stroke: 0.3pt + luma(180))
    },
    footer: context {
      line(length: 100%, stroke: 0.3pt + luma(180))
      set text(size: 8pt, fill: luma(120))
      align(center)[
        #counter(page).display("1 из 1", both: true)
      ]
    },
  )

  set par.line(
    numbering: "1",
    number-align: right,
    number-margin: left,
  )

  show figure: set par.line(numbering: none)
  show figure.where(kind: table): set block(breakable: true)

  set text(
    font: body-font,
    size: 11pt,
    lang: "ru",
    hyphenate: true,
  )

  set par(
    leading: 0.75em,
    spacing: 0.75em,
    first-line-indent: (amount: 1.5em, all: false),
    justify: true,
  )

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

  set table(
    stroke: none,
    inset: (x: 0.5em, y: 0.4em),
  )

  show table.cell.where(y: 0): set text(weight: "bold", size: 10pt)
  show table.cell: set text(size: 10pt)

  set list(indent: 1.5em, spacing: 0.4em)
  set enum(indent: 1.5em, spacing: 0.4em)

  // Titleblock
  align(center)[
    #v(1em)
    #text(size: 16pt, weight: "bold", font: body-font)[
      #title
    ]
    #v(1.2em)
    #for author in authors [
      #text(size: 11pt, weight: "bold")[#author.name]
      #if author.keys().contains("superscript") [
        #super[#author.superscript]
      ]
      #text(size: 11pt)[\ ]
    ]
    #v(0.5em)
    #for (i, author) in authors.enumerate() [
      #if author.keys().contains("affiliation") [
        #text(size: 9.5pt, fill: luma(60))[
          #if authors.len() > 1 [#super[#str(i + 1)]]
          #author.affiliation \
        ]
      ]
    ]
    #v(0.4em)
    #for author in authors [
      #if author.keys().contains("email") [
        #text(size: 9.5pt)[
          _Корреспонденция:_ #link("mailto:" + author.email)[#author.email]
        ]
      ]
    ]
    #v(0.4em)
    #text(size: 9pt, fill: luma(80))[
      Препринт для #journal-target • #date-str
    ]
    #v(0.8em)
    #line(length: 100%, stroke: 0.5pt)
  ]

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
        #text(size: 11pt, weight: "bold")[Аннотация]
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

  doc
}

// Вспомогательные компоненты

#let biorxiv-references(content) = {
  v(1em)
  line(length: 100%, stroke: 0.5pt)
  heading(level: 1, "Список литературы")
  set text(size: 9.5pt)
  set par(
    leading: 0.6em,
    spacing: 0.5em,
    first-line-indent: (amount: 0em, all: false),
    hanging-indent: 1.5em,
  )
  content
}

#let scientific-table(columns: (), header-rows: 1, ..cells) = {
  line(length: 100%, stroke: 1pt)
  v(-0.3em)
  table(
    columns: columns,
    stroke: (x, y) => {
      if y == header-rows { (bottom: 0.5pt) }
      else { none }
    },
    ..cells
  )
  v(-0.3em)
  line(length: 100%, stroke: 1pt)
}

#let transparency-table(..rows) = {
  scientific-table(
    columns: (2fr, 1.2fr, 3fr),
    header-rows: 1,
    [*Источник данных*], [*Статус*], [*Примечания*],
    ..rows
  )
}

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

#let limitations(..items) = {
  v(0.5em)
  block(
    stroke: 0.5pt + luma(200),
    fill: luma(252),
    inset: (x: 1em, y: 0.8em),
    radius: 3pt,
    width: 100%,
  )[
    #text(weight: "bold")[Ограничения]
    #enum(..items)
  ]
}

#let pearl(content) = {
  box(
    fill: rgb("fff9e6"),
    inset: (x: 0.2em, y: 0.05em),
    radius: 2pt,
  )[#content]
}
