/**
 * Physics Validation Script
 * Run with: npx tsx src/__tests__/physics-validation.ts
 */

import {
  LoopExtrusionEngine,
  loopsToContactMatrix,
  computePSCurve,
  fitPSPowerLaw,
} from "../engines/LoopExtrusionEngine";
import { loadCTCFFromBED } from "../parsers/bed";
import * as fs from "fs";

console.log("🔬 ARCHCODE Physics Validation\n");

// Test 1: Convergent CTCF should form loop
console.log("=== Test 1: Convergent CTCF (R...F) ===");
const engine1 = new LoopExtrusionEngine({
  genomeLength: 100000,
  ctcfSites: [
    { chrom: "chr11", position: 30000, orientation: "R", strength: 1.0 },
    { chrom: "chr11", position: 70000, orientation: "F", strength: 1.0 },
  ],
  cohesinLoadPosition: 50000,
  velocity: 1000,
  seed: 42,
});

console.log(
  "CTCF sites: R@30kb, F@70kb (convergent: left leg hits R, right leg hits F)",
);
console.log("Cohesin loaded at 50kb");

const loops1 = engine1.run(100);
console.log(`Result: ${loops1.length} loop(s) formed`);
if (loops1.length > 0) {
  console.log(
    `✅ PASS: Loop anchors at ${loops1[0].leftAnchor / 1000}kb - ${loops1[0].rightAnchor / 1000}kb`,
  );
} else {
  console.log("❌ FAIL: Expected 1 loop");
}

// Test 2: Divergent CTCF should NOT form loop
console.log("\n=== Test 2: Divergent CTCF (F...R) ===");
const engine2 = new LoopExtrusionEngine({
  genomeLength: 100000,
  ctcfSites: [
    { chrom: "chr11", position: 30000, orientation: "F", strength: 1.0 },
    { chrom: "chr11", position: 70000, orientation: "R", strength: 1.0 },
  ],
  cohesinLoadPosition: 50000,
  velocity: 1000,
  seed: 42,
});

console.log("CTCF sites: F@30kb, R@70kb (divergent: both legs escape)");
const loops2 = engine2.run(100);
console.log(`Result: ${loops2.length} loop(s) formed`);
if (loops2.length === 0) {
  console.log("✅ PASS: No loop (as expected)");
} else {
  console.log("❌ FAIL: Divergent should not form loop");
}

// Test 3: Load BED file
console.log("\n=== Test 3: BED File Loading ===");
const bedContent = fs.readFileSync(
  "data/input/ctcf/GM12878_HBB_CTCF_peaks.bed",
  "utf-8",
);
const bedResult = loadCTCFFromBED(bedContent);
console.log(`Parsed ${bedResult.parsed} CTCF sites`);
console.log(
  `Forward: ${bedResult.sites.filter((s) => s.orientation === "F").length}`,
);
console.log(
  `Reverse: ${bedResult.sites.filter((s) => s.orientation === "R").length}`,
);

// Test 4: Full simulation with BED data
console.log("\n=== Test 4: Full Simulation ===");
const engine3 = new LoopExtrusionEngine({
  genomeLength: 550000,
  ctcfSites: bedResult.sites,
  cohesinLoadPosition: 5275000,
  velocity: 500,
  seed: 42,
});

console.log("Running simulation with real CTCF data...");
const loops3 = engine3.run(500);
console.log(`Formed ${loops3.length} loop(s)`);
loops3.forEach((loop, i) => {
  console.log(
    `  Loop ${i + 1}: ${loop.leftAnchor.toLocaleString()} - ${loop.rightAnchor.toLocaleString()} bp (size: ${((loop.rightAnchor - loop.leftAnchor) / 1000).toFixed(1)} kb)`,
  );
});

// Test 5: Contact Matrix and P(s)
console.log("\n=== Test 5: Contact Matrix Analysis ===");
if (loops3.length > 0) {
  const matrix = loopsToContactMatrix(loops3, 5200000, 5350000, 10000);
  const ps = computePSCurve(matrix);
  const fit = fitPSPowerLaw(ps.distances, ps.contacts);

  console.log(`Matrix size: ${matrix.length}x${matrix.length}`);
  console.log(`P(s) curve: ${ps.distances.length} points`);
  console.log(
    `Power-law fit: α = ${fit.alpha.toFixed(3)}, R² = ${fit.r2.toFixed(3)}`,
  );

  if (fit.alpha < -0.8 && fit.alpha > -1.2) {
    console.log("✅ PASS: α ≈ -1.0 (typical for Hi-C)");
  } else {
    console.log("⚠️ WARNING: α outside typical range (-0.8 to -1.2)");
  }
}

console.log("\n=== Validation Complete ===");
