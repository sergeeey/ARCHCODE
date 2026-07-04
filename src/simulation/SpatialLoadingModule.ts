/**
 * H2: Mediator-driven Cohesin Fountains
 * Spatial loading module — модифицирует вероятность загрузки когезина по позиции.
 *
 * P_loading(x) = Baseline_Rate * (1 + beta * (MED1_Signal(x) / Median_Signal))
 *
 * Работает только с предразбитым (binned) сигналом MED1; чтение BigWig — в скриптах.
 */

import type { SeededRandom } from "../utils/random";

/** Интерфейс для интеграции с движком: вероятность загрузки за шаг и сэмплирование позиции */
export interface ISpatialLoader {
  /** Вероятность того, что на данном шаге произойдёт хотя бы одна загрузка (норма по геному). */
  getStepLoadingProbability(): number;
  /** Сэмплировать позицию загрузки (в bp относительно начала локуса). */
  sampleLoadingPosition(rng: SeededRandom): number;
}

/**
 * FountainLoader — загрузка когезина, модулированная сигналом MED1.
 * Сигнал задаётся массивом по бинам (один элемент = один бин по геному).
 */
export class FountainLoader implements ISpatialLoader {
  private readonly signalBins: number[];
  private readonly genomeStart: number;
  private readonly genomeEnd: number;
  private readonly baselineRate: number;
  private readonly beta: number;
  private readonly medianSignal: number;
  /** Вероятность загрузки по бинам (нормализованная для сэмплирования) */
  private readonly binProbs: number[];
  /** Интегральная вероятность загрузки за шаг (среднее P_loading по локусу) */
  private readonly stepLoadingProbability: number;

  constructor(options: {
    /** Сигнал MED1 по бинам (длина = число бинов) */
    signalBins: number[];
    /** Начало региона в bp (глобальные координаты) */
    genomeStart: number;
    /** Конец региона в bp */
    genomeEnd: number;
    /** Базовая вероятность загрузки за шаг (например Sabaté: 1/3600) */
    baselineRate: number;
    /** Коэффициент усиления по MED1 (например 2.0) */
    beta: number;
  }) {
    this.signalBins = options.signalBins;
    this.genomeStart = options.genomeStart;
    this.genomeEnd = options.genomeEnd;
    this.baselineRate = options.baselineRate;
    this.beta = options.beta;

    const n = this.signalBins.length;
    if (n === 0) {
      this.medianSignal = 1;
      this.binProbs = [];
      this.stepLoadingProbability = this.baselineRate;
      return;
    }

    const sorted = [...this.signalBins]
      .filter((x) => isFinite(x) && x >= 0)
      .sort((a, b) => a - b);
    this.medianSignal =
      sorted.length > 0
        ? (sorted[Math.floor((sorted.length - 1) / 2)]! +
            sorted[Math.ceil((sorted.length - 1) / 2)]!) /
          2
        : 1;
    const safeMedian = this.medianSignal > 0 ? this.medianSignal : 1;

    const rawProbs: number[] = [];
    let sum = 0;
    for (let i = 0; i < n; i++) {
      const s = this.signalBins[i] ?? 0;
      const ratio = safeMedian > 0 ? s / safeMedian : 0;
      const p = Math.max(0, 1 + this.beta * ratio);
      rawProbs.push(p);
      sum += p;
    }

    this.binProbs =
      sum > 0 ? rawProbs.map((p) => p / sum) : rawProbs.map(() => 1 / n);
    const meanP = rawProbs.reduce((a, b) => a + b, 0) / n;
    this.stepLoadingProbability = this.baselineRate * meanP;
  }

  /**
   * P_loading(x) = Baseline_Rate * (1 + beta * (MED1_Signal(x) / Median_Signal))
   * x — позиция в bp (относительно genomeStart или глобальная в пределах [genomeStart, genomeEnd]).
   */
  getLoadingProbabilityAt(positionBp: number): number {
    const n = this.signalBins.length;
    if (n === 0) return this.baselineRate;

    const span = this.genomeEnd - this.genomeStart;
    const rel = positionBp - this.genomeStart;
    const binIndex = Math.max(0, Math.min(n - 1, Math.floor((rel / span) * n)));
    const s = this.signalBins[binIndex] ?? 0;
    const safeMedian = this.medianSignal > 0 ? this.medianSignal : 1;
    const ratio = s / safeMedian;
    return this.baselineRate * Math.max(0, 1 + this.beta * ratio);
  }

  getStepLoadingProbability(): number {
    return this.stepLoadingProbability;
  }

  /**
   * Сэмплировать позицию загрузки (в bp) в диапазоне [genomeStart, genomeEnd).
   * Распределение пропорционально P_loading по бинам.
   */
  sampleLoadingPosition(rng: SeededRandom): number {
    const n = this.binProbs.length;
    if (n === 0) {
      const span = this.genomeEnd - this.genomeStart;
      return this.genomeStart + rng.random() * span;
    }

    const u = rng.random();
    let acc = 0;
    let bin = 0;
    for (let i = 0; i < n; i++) {
      acc += this.binProbs[i]!;
      if (u < acc) {
        bin = i;
        break;
      }
      bin = i;
    }

    const span = this.genomeEnd - this.genomeStart;
    const binWidth = span / n;
    const binStart = this.genomeStart + bin * binWidth;
    return binStart + rng.random() * binWidth;
  }

  getMedianSignal(): number {
    return this.medianSignal;
  }

  getBinCount(): number {
    return this.signalBins.length;
  }
}
