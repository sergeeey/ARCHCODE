// ARCHCODE Manuscript — bioRxiv Preprint (biology-first version)
// Compiled with Typst via Python typst package

#import "template.typ": biorxiv-template

#show: biorxiv-template.with(
  title: [A Tissue-Dependent Structural Prioritization Framework for Enhancer-Proximal ClinVar Variants Across Nine Genomic Loci],
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
