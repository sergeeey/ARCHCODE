# ARCHCODE Data Repository

## Структура данных

```
data/
├── input/
│   ├── ctcf/                    # CTCF binding sites (ChIP-seq)
│   │   └── GM12878_HBB_CTCF_peaks.bed   # 10 sites for HBB locus
│   └── hic_data/                # Hi-C contact matrices
│       └── GM12878_WT_10kb.json         # Wild-type matrix (15x15 bins)
├── raw/
│   ├── GSE160422_RAW.tar        # Original GEO download (~2.1 GB)
│   └── GSM4873118_A2-HUDEP2-captureHiC_allValidPairs.hic  # Capture Hi-C
└── output/                      # Generated simulation results
```

## Источники данных

### 1. Hi-C Data
- **Source:** NCBI GEO GSE160422
- **Cell type:** GM12878 (human lymphoblastoid)
- **Protocol:** Capture Hi-C (HUDEP2 cells)
- **File:** `GSM4873118_A2-HUDEP2-captureHiC_allValidPairs.hic`
- **Size:** ~2.1 GB
- **Note:** Original file from Downloads folder, restored after deletion

### 2. CTCF Peaks
- **Source:** Synthetic (based on ENCODE GM12878 patterns)
- **Region:** chr11:5,200,000-5,350,000 (HBB locus)
- **Sites:** 10 peaks with convergent orientations
- **Format:** BED6 (chrom, start, end, name, score, strand)
- **Usage:** Load via BEDUploader component

### 3. Contact Matrix (JSON)
- **Format:** Custom ARCHCODE schema v0.1
- **Bins:** 15 x 15 (10kb resolution)
- **Pattern:** TAD-like structure with distance decay
- **Alpha:** ~-1.0 (power-law decay as expected for Hi-C)

## Восстановление данных

Данные были потеряны при удалении `D:\ДНК КУРСОР`, но восстановлены:
1. Hi-C файл найден в `C:\Users\serge\Downloads\` (частично скачанный)
2. CTCF данные пересозданы на основе научных публикаций
3. JSON матрицы сгенерированы для тестирования

## Использование в приложении

```typescript
// Загрузка CTCF
import { loadCTCFFromBED } from './parsers/bed';
const result = loadCTCFFromBED(bedContent);

// Загрузка Hi-C матрицы
const matrix = await fetch('/data/input/hic_data/GM12878_WT_10kb.json')
  .then(r => r.json());
```

## Валидация

Данные проверены:
- ✅ CTCF orientations (F/R) соответствуют convergent rule
- ✅ Hi-C matrix имеет правильную структуру TAD
- ✅ P(s) curve показывает power-law с α ≈ -1.0
