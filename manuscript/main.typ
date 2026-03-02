// ARCHCODE Manuscript — bioRxiv Preprint
// Compiled with Typst via Python typst package

#import "template.typ": biorxiv-template

#show: biorxiv-template.with(
  title: [ARCHCODE: 3D Chromatin Loop Extrusion Simulation Reveals Structural Pathogenicity Invisible to Sequence-Based Predictors in β-Globin Variants],
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
