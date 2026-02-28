# Supplementary Table S1: All 20 Pearl Variants

| ClinVar_ID   | HGVS_c                                              | Category        | ClinVar_Significance         | ARCHCODE_SSIM | VEP_Score | VEP_Consequence         | Pearl | Discordance   | Mechanism_Insight                 |
| ------------ | --------------------------------------------------- | --------------- | ---------------------------- | ------------- | --------- | ----------------------- | ----- | ------------- | --------------------------------- |
| VCV000869358 | c.50dup                                             | frameshift      | Pathogenic                   | 0.8915        | 0.15      | synonymous_variant      | true  | ARCHCODE_ONLY | LoF, VEP misannotated             |
| VCV002024192 | c.93-33_96delinsACTGTCCCTTGGGCTGTTTTCCTACCCTCAGATTA | splice_acceptor | Likely pathogenic            | 0.9004        | 0.20      | coding_sequence_variant | true  | ARCHCODE_ONLY | Complex indel, VEP underscored    |
| VCV000015471 | c.-78A>G                                            | promoter        | Pathogenic/Likely pathogenic | 0.9276        | 0.20      | 5_prime_UTR_variant     | true  | AGREEMENT     | Promoter–enhancer loop disruption |
| VCV000015470 | c.-78A>C                                            | promoter        | Pathogenic                   | 0.9276        | 0.20      | 5_prime_UTR_variant     | true  | AGREEMENT     | Promoter–enhancer loop disruption |
| VCV000036284 | c.-136C>T                                           | promoter        | Pathogenic/Likely pathogenic | 0.9277        | 0.20      | 5_prime_UTR_variant     | true  | AGREEMENT     | Promoter–enhancer loop disruption |
| VCV002506212 | c.-136C>A                                           | promoter        | Likely pathogenic            | 0.9277        | 0.20      | 5_prime_UTR_variant     | true  | AGREEMENT     | Promoter–enhancer loop disruption |
| VCV000801184 | c.-121C>T                                           | promoter        | Pathogenic/Likely pathogenic | 0.9279        | 0.20      | 5_prime_UTR_variant     | true  | AGREEMENT     | Promoter–enhancer loop disruption |
| VCV000869290 | c.-80T>C                                            | promoter        | Pathogenic                   | 0.9282        | 0.20      | 5_prime_UTR_variant     | true  | AGREEMENT     | Promoter–enhancer loop disruption |
| VCV000015586 | c.-151C>G                                           | promoter        | Pathogenic                   | 0.9284        | 0.20      | 5_prime_UTR_variant     | true  | AGREEMENT     | Promoter–enhancer loop disruption |
| VCV000015466 | c.-81A>G                                            | promoter        | Pathogenic                   | 0.9287        | 0.20      | 5_prime_UTR_variant     | true  | AGREEMENT     | Promoter–enhancer loop disruption |
| VCV000036287 | c.-137C>T                                           | promoter        | Pathogenic/Likely pathogenic | 0.9289        | 0.20      | 5_prime_UTR_variant     | true  | AGREEMENT     | Promoter–enhancer loop disruption |
| VCV000036285 | c.-137C>A                                           | promoter        | Pathogenic                   | 0.9289        | 0.20      | 5_prime_UTR_variant     | true  | AGREEMENT     | Promoter–enhancer loop disruption |
| VCV000015464 | c.-137C>G                                           | promoter        | Pathogenic/Likely pathogenic | 0.9289        | 0.20      | 5_prime_UTR_variant     | true  | AGREEMENT     | Promoter–enhancer loop disruption |
| VCV000869288 | c.-79A>C                                            | promoter        | Pathogenic                   | 0.9290        | 0.20      | 5_prime_UTR_variant     | true  | AGREEMENT     | Promoter–enhancer loop disruption |
| VCV000015462 | c.-142C>T                                           | promoter        | Pathogenic/Likely pathogenic | 0.9290        | 0.20      | 5_prime_UTR_variant     | true  | AGREEMENT     | Promoter–enhancer loop disruption |
| VCV000015514 | c.-140C>T                                           | promoter        | Pathogenic/Likely pathogenic | 0.9292        | 0.20      | 5_prime_UTR_variant     | true  | AGREEMENT     | Promoter–enhancer loop disruption |
| VCV000393701 | c.-138C>A                                           | promoter        | Pathogenic/Likely pathogenic | 0.9297        | 0.20      | 5_prime_UTR_variant     | true  | AGREEMENT     | Promoter–enhancer loop disruption |
| VCV000015208 | c.279C>R                                            | missense        | Pathogenic                   | 0.9492        | 0.20      | coding_sequence_variant | true  | AGREEMENT     | Complex variant, VEP generic      |
| VCV000811500 | c.279C>A                                            | missense        | Pathogenic                   | 0.9492        | 0.20      | coding_sequence_variant | true  | AGREEMENT     | Complex variant, VEP generic      |
| VCV002664746 | c.279C>G                                            | missense        | Likely pathogenic            | 0.9492        | 0.20      | coding_sequence_variant | true  | AGREEMENT     | Complex variant, VEP generic      |

_Pearl definition: VEP_Score < 0.30 AND ARCHCODE_SSIM < 0.95._
_Sorted by ARCHCODE_SSIM ascending (strongest structural disruption first)._
_Source: results/HBB_Clinical_Atlas_REAL.csv (353 total variants)._
