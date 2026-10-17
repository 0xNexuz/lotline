import { createHash } from "node:crypto";
import { cp, mkdir, readdir, readFile, rm, writeFile } from "node:fs/promises";
import path from "node:path";

const root = process.cwd();
const source = path.join(root, "frontend");
const output = path.join(root, "dist");
const evidenceSource = path.join(root, "evidence", "cloud-demo-run.json");

await rm(output, { force: true, recursive: true });
await mkdir(output, { recursive: true });
await cp(source, output, { recursive: true });
await mkdir(path.join(output, "evidence"), { recursive: true });
await cp(evidenceSource, path.join(output, "evidence", "cloud-demo-run.json"));
await cp(path.join(source, "index.html"), path.join(output, "404.html"));

async function collect(directory, prefix = "") {
  const entries = await readdir(directory, { withFileTypes: true });
  const files = [];
  for (const entry of entries.sort((a, b) => a.name.localeCompare(b.name))) {
    const absolute = path.join(directory, entry.name);
    const relative = path.posix.join(prefix, entry.name);
    if (entry.isDirectory()) files.push(...await collect(absolute, relative));
    else files.push({ absolute, relative });
  }
  return files;
}

const files = await collect(output);
const manifest = [];
for (const file of files) {
  const bytes = await readFile(file.absolute);
  manifest.push({
    path: file.relative,
    bytes: bytes.length,
    sha256: createHash("sha256").update(bytes).digest("hex"),
  });
}

await writeFile(
  path.join(output, "build-manifest.json"),
  `${JSON.stringify({ artifact: "lotline-static-demo", files: manifest }, null, 2)}\n`,
  "utf8",
);

console.log(`build: wrote ${manifest.length} assets to dist/`);
