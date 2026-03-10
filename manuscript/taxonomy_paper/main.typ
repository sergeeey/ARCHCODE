// Taxonomy Paper — bioRxiv Preprint
// Compiled with Typst via Python typst package

#import "template.typ": taxonomy-template

#show: taxonomy-template.with(
  title: [Regulatory Pathogenicity Is Mechanistically Heterogeneous: A Taxonomy of Activity-, Architecture-, and Coverage-Driven Blind Spots],
  authors: (
    (
      name: "Sergey V. Boyko",
      superscript: "1",
      affiliation: "Independent Researcher, Almaty, Kazakhstan",
      email: "sergeikuch80@gmail.com",
    ),
  ),
  abstract: include "abstract_content.typ",
)

#include "body_content.typ"
