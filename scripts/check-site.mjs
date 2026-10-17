import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import path from "node:path";

const root = process.cwd();
const required = [
  "frontend/index.html",
  "frontend/styles.css",
  "frontend/app.js",
  "frontend/favicon.svg",
  "frontend/site.webmanifest",
  "frontend/assets/lotline-mark.svg",
  "frontend/assets/lotline-eye-reference.png",
  "frontend/assets/lotline-ornate-reference.png",
];

for (const relative of required) await readFile(path.join(root, relative));

const expectedReferenceHashes = new Map([
  ["frontend/assets/lotline-eye-reference.png", "1a17d28094377bca624f9e3efabbc0970098d744d13822dc980ddfbee0d0ceca"],
  ["frontend/assets/lotline-ornate-reference.png", "17ed21b78bd7ad0954d8767d48f68dfb41af96a6494070878cf60def4cceb98c"],
]);

for (const [relative, expected] of expectedReferenceHashes) {
  const bytes = await readFile(path.join(root, relative));
  const actual = createHash("sha256").update(bytes).digest("hex");
  if (actual !== expected) throw new Error(`${relative} no longer matches the supplied reference`);
}

const html = await readFile(path.join(root, "frontend/index.html"), "utf8");
for (const token of ["LOTLINE", "FalkorDB", "lotline-mark.svg", "favicon.svg", "id=\"proof\"", "id=\"evidence\""]) {
  if (!html.includes(token)) throw new Error(`Required site token missing: ${token}`);
}

if (/Greaguy|FALKORDB_PASSWORD\s*=\s*[^<]/i.test(html)) {
  throw new Error("Potential credential material found in public HTML");
}

if (/open the live case/i.test(html)) {
  throw new Error("Static deployment must not describe evidence playback as a live case");
}

const cloudProof = JSON.parse(
  await readFile(path.join(root, "evidence", "cloud-demo-run.json"), "utf8"),
);
const expectedLots = ["LOT-BITES-201", "LOT-GRANOLA-101", "LOT-GRANOLA-102"];
if (!String(cloudProof.execution_status).startsWith("REAL")) {
  throw new Error("Cloud evidence is not marked as a real execution");
}
if (JSON.stringify(cloudProof.plan?.affected_lots) !== JSON.stringify(expectedLots)) {
  throw new Error("Cloud evidence affected-lot set does not match the public proof");
}
if (cloudProof.plan?.safe_lots_spared !== 7) throw new Error("Cloud evidence safe-lot count changed");
if (cloudProof.first_execution?.new_effects !== 5) throw new Error("Cloud first-execution proof changed");
if (cloudProof.replay_execution?.new_effects !== 0) throw new Error("Cloud replay proof is not idempotent");
if (cloudProof.final_case?.status !== "COMPLETED") throw new Error("Cloud proof did not complete");

console.log(`site-check: ${required.length} required assets present; exact references verified`);
