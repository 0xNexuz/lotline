import { readdir, readFile } from "node:fs/promises";
import path from "node:path";

const root = process.cwd();
const ignoredDirectories = new Set([
  ".git",
  ".npm-cache",
  ".npm-cache-release",
  ".venv",
  ".vercel",
  "__pycache__",
  "dist",
]);
const textExtensions = new Set([
  ".css", ".html", ".js", ".json", ".md", ".mjs", ".py", ".txt", ".yml", ".yaml",
]);
const textNames = new Set([".env.example", ".gitignore", "LICENSE"]);

async function collect(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    if (entry.isDirectory() && ignoredDirectories.has(entry.name)) continue;
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) files.push(...await collect(absolute));
    else if (textExtensions.has(path.extname(entry.name).toLowerCase()) || textNames.has(entry.name)) files.push(absolute);
  }
  return files;
}

const allowlistedPlaceholders = new Set([
  "replace-me",
  "YOUR_PASSWORD",
  "your-password",
  "example",
]);
const directPatterns = [
  /-----BEGIN(?: [A-Z]+)? PRIVATE KEY-----/,
  /\bgh[pousr]_[A-Za-z0-9]{20,}\b/,
  /\bgithub_pat_[A-Za-z0-9_]{20,}\b/,
  /\bsk-[A-Za-z0-9_-]{20,}\b/,
];
const credentialUri = /\b(?:falkors?|redis|rediss):\/\/[^:@/\s]+:([^@\s]+)@/g;
const passwordAssignment = /^\s*FALKORDB_PASSWORD\s*=\s*([^\s#]+)/gm;

const findings = [];
const files = await collect(root);
for (const absolute of files) {
  const relative = path.relative(root, absolute).replaceAll("\\", "/");
  const content = await readFile(absolute, "utf8");
  for (const pattern of directPatterns) {
    if (pattern.test(content)) findings.push(`${relative}: token/private-key pattern`);
  }
  for (const match of content.matchAll(credentialUri)) {
    if (!allowlistedPlaceholders.has(decodeURIComponent(match[1]))) findings.push(`${relative}: credential URI`);
  }
  for (const match of content.matchAll(passwordAssignment)) {
    if (!allowlistedPlaceholders.has(match[1])) findings.push(`${relative}: password assignment`);
  }
}

if (findings.length) throw new Error(`Potential secrets found:\n${findings.join("\n")}`);
console.log(`secret-check: ${files.length} text files scanned; only approved placeholders allowed`);
