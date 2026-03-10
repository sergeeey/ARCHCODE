// =============================================================================
// template.typ — Taxonomy Paper wrapper over base bioRxiv template
// =============================================================================
// ПОЧЕМУ: базовый template.typ хардкодит journal-target и date-str.
// Вместо копирования 300+ строк — импортируем и re-export с новыми значениями.
// Единственное различие: целевой журнал и дата.
// =============================================================================

// Re-export base template utilities
#import "../template.typ": biorxiv-references, hrule, thick-hrule

// Override constants for taxonomy paper
#let taxonomy-journal = "bioRxiv Genomics"
#let taxonomy-date = "2026-03-10"

// Wrapper template that patches header/footer
#let taxonomy-template(
  title: [],
  authors: (),
  abstract: [],
  keywords: (),
  doc,
) = {
  // Import and apply base template
  // We override the page header to show correct journal target
  import "../template.typ": body-font, mono-font

  set page(
    paper: "us-letter",
    margin: (top: 1in, bottom: 1in, left: 1in, right: 1in),
    numbering: "1",
    header: context {
      set text(size: 8pt, fill: luma(120))
      grid(
        columns: (1fr, 1fr),
        align(left)[Preprint — not peer reviewed — #taxonomy-journal],
        align(right)[#taxonomy-date],
      )
      line(length: 100%, stroke: 0.3pt + luma(180))
    },
    footer: context {
      line(length: 100%, stroke: 0.3pt + luma(180))
      set text(size: 8pt, fill: luma(120))
      align(center)[
        #counter(page).display("1 of 1", both: true)
      ]
    },
  )

  // Line numbering
  set par.line(
    numbering: "1",
    number-align: right,
    number-margin: left,
  )
  show figure: set par.line(numbering: none)
  show figure.where(kind: table): set block(breakable: true)

  // Typography (same as base)
  set text(
    font: body-font,
    size: 11pt,
    lang: "en",
    hyphenate: true,
  )
  set par(
    leading: 0.75em,
    spacing: 0.75em,
    first-line-indent: (amount: 1.5em, all: false),
    justify: true,
  )

  // Headings
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

  // Code blocks
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

  // Tables
  set table(stroke: none, inset: (x: 0.5em, y: 0.4em))
  show table.cell.where(y: 0): set text(weight: "bold", size: 10pt)
  show table.cell: set text(size: 10pt)

  // Lists
  set list(indent: 1.5em, spacing: 0.4em)
  set enum(indent: 1.5em, spacing: 0.4em)

  // === RENDER ===

  // Title block
  align(center)[
    #v(1em)
    #text(size: 16pt, weight: "bold", font: body-font)[#title]
    #v(1.2em)
    #for author in authors [
      #text(size: 11pt, weight: "bold")[#author.name]
      #if author.keys().contains("superscript") [#super[#author.superscript]]
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
          _Correspondence:_ #link("mailto:" + author.email)[#author.email]
        ]
      ]
    ]
    #v(0.4em)
    #text(size: 9pt, fill: luma(80))[
      Preprint submitted to #taxonomy-journal • #taxonomy-date
    ]
    #v(0.8em)
    #line(length: 100%, stroke: 0.5pt)
  ]

  // Abstract
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

  // Body
  doc
}
