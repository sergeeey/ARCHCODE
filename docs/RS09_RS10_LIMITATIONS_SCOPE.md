# Limitations & Scope: Формулировки для статьи

## Раздел Limitations & Scope для публикации RS-09 + RS-10

**Цель:** Проактивно и честно ограничить scope работы, адресовав потенциальные вопросы рецензентов.

---

## 1. Compartmentalization (A/B-компартменты)

### Формулировка для Introduction

> "In this work we focus specifically on the axis of genome organization governed by active loop extrusion (cohesin–NIPBL–WAPL), and in particular on the stability of TAD boundaries. We explicitly do not model large-scale A/B compartmentalization, which emerges from distinct mechanisms (phase separation, chromatin states) that interact with but are separable from the extrusion-based axis considered here."

### Формулировка для Discussion

> "Our 'processivity + bookmarking' framework should be viewed as a theory of **TAD/loop-domain stability**, not a complete theory of whole-nucleus compartment architecture. Large-scale A/B compartmentalization, driven by phase separation and chromatin state interactions, represents a distinct organizational axis that we do not address here."

### Подтверждение (если есть данные)

> "We verified that varying processivity in our model primarily affects TAD-level insulation while leaving large-scale compartment patterns largely unchanged, consistent with the view that compartments and TADs are controlled by partially separable mechanisms."

---

## 2. NIPBL: Velocity vs Loading Rate

### Формулировка для Methods

> "For modeling purposes, we lump multiple NIPBL-dependent effects (loading frequency, stimulation of cohesin ATPase, pause-release kinetics) into a single effective extrusion rate parameter, v_eff. We do not claim that NIPBL acts purely as a 'speed knob'; rather, we show that **any NIPBL-dependent reduction in effective processivity** (v_eff × lifetime) has equivalent architectural consequences."

### Формулировка для Results (если есть robustness check)

> "We find that whether NIPBL primarily reduces extrusion speed, active cohesin density, or both, the **effective processivity** emerges as the key determinant of boundary stability. This suggests that the architectural phenotype depends on the aggregated v_eff, rather than on which specific micromolecular mechanism is affected."

### Альтернативная формулировка формулы

**Вместо:**
```
Processivity = NIPBL_velocity × WAPL_lifetime
```

**Можно использовать:**
```
Processivity = EffectiveExtrusionRate × CohesinLifetime
```

**С объяснением:**
> "Where EffectiveExtrusionRate decreases under NIPBL haploinsufficiency, reflecting the combined effects of loading frequency, motor activation, and pause-release kinetics."

---

## 3. Bookmarking Threshold (30–40%)

### Формулировка для Results

> "In our minimal CTCF-only memory model, we observe an apparent critical fraction of bookmarked boundaries (~30–40%), below which architectural memory decays rapidly over 5–10 simulated cell cycles."

**Ключевые слова:** *minimal*, *CTCF-only*, *apparent critical fraction*, *simulated cell cycles*

### Перколяционный аргумент (если подтвержден)

> "This threshold is not imposed by hand; rather, it emerges as a percolation-like transition in the graph of boundaries that retain memory across cycles in our model. Below this threshold, the largest connected component of stable boundaries collapses, leading to rapid architectural drift."

### Примирение с реальной биологией

> "Importantly, real cells likely exploit multiple overlapping memory channels—CTCF bookmarking, histone modifications, transcription-driven reestablishment—which together can sustain architectural memory even when the pure CTCF bookmarking fraction is below the ~30–40% threshold observed in our minimal model."

### Подтверждение (если есть данные)

> "When we add a second memory channel (transcriptional memory) to our model, the effective threshold shifts downward, consistent with the observation that embryonic stem cells can maintain architectural memory with lower CTCF bookmarking fractions than predicted by our CTCF-only model."

---

## 4. Общий раздел Limitations

### Полная формулировка для статьи

> **"Limitations and Scope"**
> 
> "Our model focuses on the loop extrusion axis of genome organization, specifically TAD boundary stability and architectural memory. Several important limitations should be noted:
> 
> **1. Compartmentalization:** We do not model large-scale A/B compartmentalization, which represents a distinct organizational mechanism driven by phase separation and chromatin state interactions. Our model addresses TAD-level organization, not whole-nucleus compartment architecture.
> 
> **2. NIPBL mechanism:** We model NIPBL effects through an aggregated 'effective extrusion rate' parameter, rather than explicitly separating loading frequency, motor activation, and pause-release kinetics. Our robustness checks suggest that the architectural phenotype depends on effective processivity regardless of the specific micromolecular mechanism, but future work could refine this distinction.
> 
> **3. Bookmarking threshold:** The ~30–40% bookmarking threshold we observe emerges from our minimal CTCF-only model. Real cells likely exploit multiple overlapping memory channels (histone modifications, transcription), which may shift this threshold. Our model provides a baseline for understanding pure CTCF-dependent memory.
> 
> **4. Model complexity:** Our current model uses simplified representations of chromatin states, methylation, and TE motifs. Future extensions could incorporate more detailed biochemical mechanisms and tissue-specific factors.
> 
> **5. Validation:** While our model recapitulates known phenotypes (CdLS, WAPL overactivation), comprehensive validation against experimental Hi-C data across cell types and conditions remains an important future direction."

---

## 5. Strengths (для баланса)

### Что подчеркнуть

> **"Strengths"**
> 
> "Despite these limitations, our model provides several key advances:
> 
> **1. Quantitative framework:** We establish the first quantitative model linking molecular mechanisms (NIPBL, WAPL) to architectural stability through a single parameter (processivity).
> 
> **2. Predictive power:** Our model predicts critical thresholds and phase transitions that can be tested experimentally.
> 
> **3. Unification:** We unify previously disparate observations (CdLS, WAPL pathologies, bookmarking defects) under a single theoretical framework.
> 
> **4. Extensibility:** The model provides a foundation for incorporating additional factors and mechanisms."

---

## 6. Future Directions

### Что предложить

> **"Future Directions"**
> 
> "Several directions would extend and strengthen our model:
> 
> **1. Integration with compartments:** Incorporating phase separation mechanisms to model A/B compartmentalization alongside TAD organization.
> 
> **2. Mechanistic refinement:** Explicitly modeling NIPBL loading kinetics, cohesin ATPase cycles, and pause-release mechanisms.
> 
> **3. Multi-channel memory:** Incorporating histone modifications, transcription, and other memory channels beyond CTCF bookmarking.
> 
> **4. Tissue-specificity:** Extending the model to capture tissue-specific architectural patterns and developmental dynamics.
> 
> **5. Experimental validation:** Systematic comparison with Hi-C data across cell types, conditions, and perturbations."

---

## Использование в статье

### Структура разделов

1. **Introduction:**
   - Использовать формулировку о compartmentalization (ограничение scope)

2. **Methods:**
   - Использовать формулировку о NIPBL как effective extrusion rate

3. **Results:**
   - Использовать формулировку о bookmarking threshold как apparent critical fraction
   - Если есть данные: добавить перколяционный аргумент

4. **Discussion:**
   - Полный раздел Limitations & Scope
   - Примирение с реальной биологией
   - Future Directions

---

**Дата:** 23 ноября 2025  
**Статус:** Ready for Article Integration









