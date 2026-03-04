// ARCHCODE Manuscript — Russian Version
// Compiled with Typst via Python typst package

#import "template_ru.typ": biorxiv-template

#show: biorxiv-template.with(
  title: [ARCHCODE: симуляция 3D-экструзии хроматиновых петель выявляет энхансер-проксимальную структурную патогенность по девяти геномным локусам],
  authors: (
    (
      name: "Бойко Сергей Валерьевич",
      superscript: "1",
      affiliation: "Независимый исследователь, Алматы, Казахстан",
      email: "sergeikuch80@gmail.com",
    ),
  ),
  abstract: include "abstract_content_ru.typ",
)

#include "body_content_ru.typ"
