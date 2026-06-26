// ARCHCODE Manuscript — bioRxiv Preprint
// Compiled with Typst via Python typst package

#import "template.typ": biorxiv-template

#show: biorxiv-template.with(
  title: [ARCHCODE: A Falsification-First Framework for Evaluating 3D Chromatin Signals in Variant Pathogenicity],
  authors: (
    (
      name: "Sergey V. Boyko",
      superscript: "1",
      affiliation: "Ronin Institute for Independent Scholarship (RIIS 2.0)",
      email: "sergey.boyko@ronininstitute.org",
    ),
  ),
  abstract: include "abstract_content.typ",
)

#include "taxonomy_paper/body_content.typ"

#pagebreak()

#include "references.typ"
