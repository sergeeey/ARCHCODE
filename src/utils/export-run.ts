import type { ArchcodeRun } from "../domain/models/experiment";

const APP_VERSION = "0.3.1";

export function downloadJson(data: unknown, filename: string): void {
  const blob = new Blob([JSON.stringify(data, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export function exportRunFilename(run: ArchcodeRun): string {
  const d = new Date(run.run.createdAt);
  const Y = d.getFullYear();
  const M = String(d.getMonth() + 1).padStart(2, "0");
  const D = String(d.getDate()).padStart(2, "0");
  const h = String(d.getHours()).padStart(2, "0");
  const m = String(d.getMinutes()).padStart(2, "0");
  const mode = run.run.mode;
  const loops = run.results.loopsFormed;
  const pairs = run.results.convergentPairs;
  return `ARCHCODE_run_${Y}${M}${D}_${h}${m}_${mode}_${loops}_${pairs}.json`;
}

export class ArchcodeRunValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ArchcodeRunValidationError";
  }
}

export function validateImportedRun(data: unknown): data is ArchcodeRun {
  if (data === null || typeof data !== "object") return false;
  const o = data as Record<string, unknown>;
  if (o.schemaVersion !== "1.0") return false;
  if (!o.app || typeof (o.app as Record<string, unknown>).name !== "string")
    return false;
  if (!o.run || typeof o.run !== "object") return false;
  const run = o.run as Record<string, unknown>;
  if (typeof run.id !== "string" || typeof run.createdAt !== "string")
    return false;
  if (
    typeof run.mode !== "string" ||
    !["tube", "linear", "helix"].includes(run.mode)
  )
    return false;
  if (
    typeof run.status !== "string" ||
    !["running", "plateau", "stopped", "error"].includes(run.status)
  )
    return false;
  if (!o.params || typeof o.params !== "object") return false;
  const params = o.params as Record<string, unknown>;
  if (
    typeof params.extrusionSpeed !== "number" ||
    Number.isNaN(params.extrusionSpeed)
  )
    return false;
  if (
    typeof params.matrixResolution !== "number" ||
    Number.isNaN(params.matrixResolution)
  )
    return false;
  if (
    typeof params.genomeLengthBp !== "number" ||
    Number.isNaN(params.genomeLengthBp)
  )
    return false;
  if (!o.model || typeof o.model !== "object") return false;
  const model = o.model as Record<string, unknown>;
  if (!Array.isArray(model.ctcfSites)) return false;
  for (const s of model.ctcfSites as Array<unknown>) {
    if (typeof s !== "object" || s === null) return false;
    const site = s as Record<string, unknown>;
    if (typeof site.pos !== "number" || Number.isNaN(site.pos)) return false;
    if (site.orient !== "F" && site.orient !== "R") return false;
  }
  if (!o.results || typeof o.results !== "object") return false;
  const results = o.results as Record<string, unknown>;
  if (typeof results.steps !== "number" || Number.isNaN(results.steps))
    return false;
  if (
    typeof results.loopsFormed !== "number" ||
    Number.isNaN(results.loopsFormed)
  )
    return false;
  if (
    typeof results.convergentPairs !== "number" ||
    Number.isNaN(results.convergentPairs)
  )
    return false;
  if (!Array.isArray(results.stablePairs)) return false;
  if (!Array.isArray(o.events)) return false;
  return true;
}

export function formatSummaryMarkdown(run: ArchcodeRun): string {
  const r = run.run;
  const res = run.results;
  const lines: string[] = [
    `# ARCHCODE Run ${r.id.slice(0, 12)}`,
    "",
    `- **Date:** ${r.createdAt}`,
    `- **Mode:** ${r.mode}`,
    `- **Status:** ${r.status}${r.stopReason ? ` (${r.stopReason})` : ""}`,
    `- **Steps:** ${res.steps}`,
    `- **Loops formed (events):** ${res.loopsFormed}`,
    ...(res.uniqueLoopsFormed != null
      ? [`- **Unique pairs (left-right):** ${res.uniqueLoopsFormed}`]
      : []),
    `- **Convergent pairs:** ${res.convergentPairs}`,
    "",
  ];
  if (res.stablePairs.length > 0) {
    lines.push("## Stable pairs (top 3)");
    lines.push("");
    res.stablePairs.slice(0, 3).forEach((p, i) => {
      lines.push(
        `${i + 1}. ${p.left.toLocaleString()} – ${p.right.toLocaleString()} bp${p.sizeBp != null ? ` (${(p.sizeBp / 1000).toFixed(1)} kb)` : ""}`,
      );
    });
    lines.push("");
  }
  if (res.convergentPairs === 0) {
    lines.push("Устойчивые петли не сформировались при данных условиях.");
  } else {
    lines.push(`Сформировано устойчивых петель: ${res.convergentPairs}`);
  }
  return lines.join("\n");
}

export function buildRunInitial(params: {
  runId: string;
  mode: "tube" | "linear" | "helix";
  extrusionSpeed: number;
  matrixResolution: number;
  genomeLengthBp: number;
  ctcfSites: Array<{
    position: number;
    orientation: "F" | "R";
    chrom?: string;
  }>;
  seed?: number;
  chromosome?: string;
}): ArchcodeRun {
  const now = new Date().toISOString();
  // Extract chromosome from first CTCF site if not provided
  const chromosome = params.chromosome ?? params.ctcfSites[0]?.chrom ?? "chr1";
  return {
    schemaVersion: "1.0",
    app: { name: "ARCHCODE", version: APP_VERSION },
    run: {
      id: params.runId,
      createdAt: now,
      mode: params.mode,
      status: "running",
      seed: params.seed,
    },
    params: {
      extrusionSpeed: params.extrusionSpeed,
      matrixResolution: params.matrixResolution,
      genomeLengthBp: params.genomeLengthBp,
    },
    model: {
      ctcfSites: params.ctcfSites.map((s) => ({
        pos: s.position,
        orient: s.orientation,
        chrom: s.chrom,
      })),
      chromosome,
    },
    results: {
      steps: 0,
      loopsFormed: 0,
      uniqueLoopsFormed: 0,
      convergentPairs: 0,
      stablePairs: [],
    },
    events: [],
  };
}
