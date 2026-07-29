/**
 * Compares two builds of the site (old vs new) by crawling every page
 * and reporting differences in errors, network failures, and visual rendering.
 *
 * Uses AWS Bedrock for Claude vision (no ANTHROPIC_API_KEY needed).
 *
 * Usage:
 *   # Serve old build on port 1414 and new build on port 1415, then:
 *   cd tests && npm run compare -- --old http://localhost:1414 --new http://localhost:1415
 *
 * Quick setup:
 *   # Terminal 1: serve old build
 *   git stash && make site && npx serve _build -l 1414
 *
 *   # Terminal 2: serve new build
 *   git stash pop && make site && npx serve _build -l 1415
 *
 *   # Terminal 3: run comparison
 *   cd tests && npm run compare
 */

import AnthropicBedrock from "@anthropic-ai/bedrock-sdk";
import sharp from "sharp";
import { chromium, type Browser } from "playwright";
import { writeFileSync } from "fs";
import { join } from "path";
import { __dirname, capturePage, getPages, normalizeError, pooled, withRetry } from "./shared.js";

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const DEFAULT_OLD = "http://localhost:1414";
const DEFAULT_NEW = "http://localhost:1415";
// Each worker snapshots old+new concurrently, so effective browser concurrency = CONCURRENCY * 2
const CONCURRENCY = 2;

const bedrock = new AnthropicBedrock({ awsRegion: process.env.AWS_REGION ?? "us-east-1" });

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** Discriminated union so callers never need string-prefix guards on observations. */
type Observations =
  | { kind: "screenshot"; data: Buffer }  // raw viewport screenshot, not yet resized
  | { kind: "http-error"; status: number }
  | { kind: "error"; message: string };

interface PageSnapshot {
  path: string;
  httpStatus: number | null;
  consoleErrors: string[];
  networkErrors: string[];
  observations: Observations;
}

interface PageDiff {
  path: string;
  summary: string;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function parseArgs(): { oldUrl: string; newUrl: string; filter?: string; exclude?: string } {
  const args = process.argv.slice(2);
  let oldUrl = DEFAULT_OLD;
  let newUrl = DEFAULT_NEW;
  let filter: string | undefined;
  let exclude: string | undefined;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--old" && args[i + 1]) {
      oldUrl = args[++i];
      try { new URL(oldUrl); } catch { console.error(`Invalid --old URL: ${oldUrl}`); process.exit(1); }
    }
    if (args[i] === "--new" && args[i + 1]) {
      newUrl = args[++i];
      try { new URL(newUrl); } catch { console.error(`Invalid --new URL: ${newUrl}`); process.exit(1); }
    }
    if (args[i] === "--filter" && args[i + 1]) filter = args[++i];
    if (args[i] === "--exclude" && args[i + 1]) exclude = args[++i];
  }

  return { oldUrl, newUrl, filter, exclude };
}

/**
 * Sends both screenshots to Claude in a single call for a direct comparison.
 * Returns null if they look the same, or a one-sentence description of the difference.
 * Single call avoids non-determinism from comparing two independent descriptions.
 * Images are viewport-only (1280×900), not full-page scrolls.
 */
async function compareScreenshots(oldShot: Buffer, newShot: Buffer): Promise<string | null> {
  // Resize once here — snapshotPage stores raw screenshots intentionally
  const [oldResized, newResized] = await Promise.all([
    sharp(oldShot).resize(640).toBuffer(),
    sharp(newShot).resize(640).toBuffer(),
  ]);

  const response = await withRetry(() =>
    bedrock.messages.create({
      model: "us.anthropic.claude-sonnet-4-6",
      max_tokens: 200,
      messages: [
        {
          role: "user",
          content: [
            {
              type: "image",
              source: { type: "base64", media_type: "image/png", data: oldResized.toString("base64") },
            },
            {
              type: "image",
              source: { type: "base64", media_type: "image/png", data: newResized.toString("base64") },
            },
            {
              type: "text",
              text: `These are viewport-only screenshots (top portion of the page, not full-page scrolls) from two builds of the same documentation page — old first, new second.
Are there any meaningful visual differences? Check layout, missing content, broken images, navigation changes.
If they look the same, respond with exactly "SAME".
If the ONLY difference is a Shinylive app showing a loading spinner or placeholder (grey dotted circular pattern) where a loaded app appears in the other build, respond with exactly "SHINYLIVE_NOT_LOADED".
If the ONLY difference is a change to the top navigation bar (such as a new search icon, a new logo or badge, or other nav bar additions), respond with exactly "NAV_CHANGE: <brief description of what changed>".
Otherwise describe what changed in one sentence.`,
            },
          ],
        },
      ],
    })
  );

  const block = response.content[0];
  const text = block.type === "text" ? block.text.trim() : "SAME";
  if (text === "SAME") return null;
  return text; // may be "SHINYLIVE_NOT_LOADED" or a description
}

async function snapshotPage(browser: Browser, baseUrl: string, path: string): Promise<PageSnapshot> {
  const captured = await capturePage(browser, `${baseUrl}${path}`);

  if ("error" in captured) {
    return { path, httpStatus: null, consoleErrors: [], networkErrors: [], observations: { kind: "error", message: captured.error } };
  }

  const { httpStatus, consoleErrors, networkErrors, close, screenshot } = captured;

  try {
    if (httpStatus === null || httpStatus >= 400) {
      return { path, httpStatus, consoleErrors, networkErrors, observations: { kind: "http-error", status: httpStatus ?? 0 } };
    }

    // Store raw buffer — compareScreenshots resizes once when needed
    const data = await screenshot();
    return { path, httpStatus, consoleErrors, networkErrors, observations: { kind: "screenshot", data } };
  } finally {
    await close();
  }
}

function diffSnapshots(path: string, old: PageSnapshot, new_: PageSnapshot): string[] {
  const diffs: string[] = [];

  // HTTP status change — return early to avoid doubled diff with visual section
  if (old.httpStatus !== new_.httpStatus) {
    diffs.push(`HTTP status: ${old.httpStatus} → ${new_.httpStatus}`);
    return diffs;
  }

  // Console errors (normalized to strip dynamic content like timestamps/IDs)
  const oldNormalized = old.consoleErrors.map(normalizeError);
  const newNormalized = new_.consoleErrors.map(normalizeError);
  const newConsole = newNormalized.filter((e) => !oldNormalized.includes(e));
  const resolvedConsole = oldNormalized.filter((e) => !newNormalized.includes(e));
  function collapseErrors(errors: string[]): string {
    const counts = new Map<string, number>();
    for (const e of errors) counts.set(e, (counts.get(e) ?? 0) + 1);
    return [...counts.entries()].map(([e, n]) => n > 1 ? `${e} (×${n})` : e).join("; ");
  }

  if (newConsole.length) diffs.push(`New console errors: ${collapseErrors(newConsole)}`);
  if (resolvedConsole.length) diffs.push(`Resolved console errors: ${collapseErrors(resolvedConsole)}`);

  // Network errors (also normalized)
  const oldNetNorm = old.networkErrors.map(normalizeError);
  const newNetNorm = new_.networkErrors.map(normalizeError);
  const newNetwork = newNetNorm.filter((e) => !oldNetNorm.includes(e));
  const resolvedNetwork = oldNetNorm.filter((e) => !newNetNorm.includes(e));
  if (newNetwork.length) diffs.push(`New network errors: ${collapseErrors(newNetwork)}`);
  if (resolvedNetwork.length) diffs.push(`Resolved network errors: ${collapseErrors(resolvedNetwork)}`);

  return diffs;
}

// ---------------------------------------------------------------------------
// Common pattern extraction
// ---------------------------------------------------------------------------

interface CommonPattern {
  pattern: string;
  pages: string[];
}

function extractCommonPatterns(diffs: PageDiff[], threshold = 5): {
  dedupedDiffs: PageDiff[];
  commonPatterns: CommonPattern[];
} {
  // Count how many pages each individual summary line appears in
  const lineToPages = new Map<string, string[]>();
  for (const diff of diffs) {
    const lines = diff.summary.split("\n  ").map((l) => l.trim()).filter(Boolean);
    for (const line of lines) {
      if (!lineToPages.has(line)) lineToPages.set(line, []);
      lineToPages.get(line)!.push(diff.path);
    }
  }

  // Patterns on threshold+ pages become common
  const commonPatterns: CommonPattern[] = [...lineToPages.entries()]
    .filter(([, pages]) => pages.length >= threshold)
    .map(([pattern, pages]) => ({ pattern, pages }))
    .sort((a, b) => b.pages.length - a.pages.length);

  const commonSet = new Set(commonPatterns.map((c) => c.pattern));

  // Strip common lines from per-page entries; drop pages where nothing unique remains
  const dedupedDiffs = diffs
    .map((diff) => {
      const lines = diff.summary.split("\n  ").map((l) => l.trim()).filter(Boolean);
      const remaining = lines.filter((l) => !commonSet.has(l));
      return remaining.length > 0 ? { path: diff.path, summary: remaining.join("\n  ") } : null;
    })
    .filter((d): d is PageDiff => d !== null);

  return { dedupedDiffs, commonPatterns };
}

// ---------------------------------------------------------------------------
// Executive summary
// ---------------------------------------------------------------------------

async function generateExecutiveSummary(regressions: PageDiff[], commonPatterns: CommonPattern[], clusterResult: ClusterResult): Promise<string> {
  if (regressions.length === 0) return "No regressions were found between the two builds.";

  const findingsList = regressions.map((d) => `Page: ${d.path}\n  ${d.summary}`).join("\n\n");
  const commonSection = commonPatterns.length > 0
    ? `\n\nCommon patterns (each appearing on ${commonPatterns[0]?.pages.length ?? "many"}+ pages, already grouped separately):\n` +
      commonPatterns.map((c) => `- "${c.pattern}" on ${c.pages.length} pages`).join("\n")
    : "";
  const clusterSection = clusterResult.clusters.length > 0
    ? "\n\nVisual change clusters:\n" + clusterResult.clusters.map((c) => `- "${c.theme}" on ${c.pages.length} pages`).join("\n")
    : "";

  const response = await withRetry(() =>
    bedrock.messages.create({
      model: "us.anthropic.claude-sonnet-4-6",
      max_tokens: 400,
      messages: [{
        role: "user",
        content: `You are reviewing the results of a documentation site comparison between two builds. Here are the regressions found:\n\n${findingsList}${commonSection}${clusterSection}\n\nWrite a brief executive summary of the most likely actual issues in order of priority. Be concise — use bullet points, 1 sentence each. Skip anything that sounds like a tool or rendering artifact rather than a real site problem.`,
      }],
    })
  );

  const block = response.content[0];
  const text = block.type === "text" ? block.text.trim() : "";
  return text.replace(/^##?\s*Executive Summary\s*\n+/i, "").trim();
}

// ---------------------------------------------------------------------------
// Visual change clustering
// ---------------------------------------------------------------------------

interface VisualCluster {
  theme: string;
  pages: string[];
}
interface ClusterResult {
  clusters: VisualCluster[];
  unclustered: { path: string; description: string }[];
}

const CLUSTER_BATCH_SIZE = 40;

async function clusterBatch(
  changes: { path: string; description: string }[]
): Promise<{ theme: string; paths: string[] }[]> {
  const list = changes.map((c) => `- ${c.path}: ${c.description.slice(0, 120)}`).join("\n");
  let raw: string;
  try {
    const response = await withRetry(() =>
      bedrock.messages.create({
        model: "us.anthropic.claude-sonnet-4-6",
        max_tokens: 2048,
        messages: [{
          role: "user",
          content: `Group these visual changes by theme. Only group pages that describe the same underlying change. Minimum cluster size 2.

Return JSON only: {"clusters":[{"theme":"short theme name","paths":["/path1","/path2"]}],"unclustered":["/path3"]}

Changes:
${list}`,
        }],
      })
    );
    const block = response.content[0];
    raw = block.type === "text" ? block.text.trim().replace(/^```(?:json)?\n?/, "").replace(/\n?```$/, "") : "{}";
  } catch {
    return [];
  }
  try {
    const parsed = JSON.parse(raw) as { clusters: { theme: string; paths: string[] }[] };
    return parsed.clusters ?? [];
  } catch {
    return [];
  }
}

async function consolidateClusters(
  allClusters: { theme: string; paths: string[] }[]
): Promise<{ theme: string; paths: string[] }[]> {
  if (allClusters.length === 0) return [];
  const list = allClusters.map((c, i) => `${i}: "${c.theme}" (${c.paths.length} pages)`).join("\n");
  let raw: string;
  try {
    const response = await withRetry(() =>
      bedrock.messages.create({
        model: "us.anthropic.claude-sonnet-4-6",
        max_tokens: 1024,
        messages: [{
          role: "user",
          content: `These are cluster themes from a site comparison. Merge clusters that describe the same underlying change. Keep distinct themes separate.

Return JSON only: {"merged":[[0,1,4],[2,3],[5]]}

Themes:
${list}`,
        }],
      })
    );
    const block = response.content[0];
    raw = block.type === "text" ? block.text.trim().replace(/^```(?:json)?\n?/, "").replace(/\n?```$/, "") : "{}";
  } catch {
    return allClusters;
  }
  try {
    const parsed = JSON.parse(raw) as { merged: number[][] };
    const groups = parsed.merged ?? allClusters.map((_, i) => [i]);
    return groups
      .map((indices) => {
        const members = indices.map((i) => allClusters[i]).filter(Boolean);
        if (members.length === 0) return null;
        const theme = members.reduce((a, b) => a.theme.length >= b.theme.length ? a : b).theme;
        const paths = [...new Set(members.flatMap((m) => m.paths))];
        return { theme, paths };
      })
      .filter((c): c is { theme: string; paths: string[] } => c !== null && c.paths.length >= 2);
  } catch {
    return allClusters;
  }
}

async function clusterVisualChanges(
  changes: { path: string; description: string }[]
): Promise<ClusterResult> {
  if (changes.length === 0) return { clusters: [], unclustered: [] };
  if (changes.length === 1) return { clusters: [], unclustered: changes };

  const allBatchClusters: { theme: string; paths: string[] }[] = [];
  for (let i = 0; i < changes.length; i += CLUSTER_BATCH_SIZE) {
    const batch = changes.slice(i, i + CLUSTER_BATCH_SIZE);
    const clusters = await clusterBatch(batch);
    allBatchClusters.push(...clusters);
  }

  const consolidated = await consolidateClusters(allBatchClusters);
  const clusteredPaths = new Set(consolidated.flatMap((c) => c.paths));

  return {
    clusters: consolidated
      .map((c) => ({ theme: c.theme, pages: c.paths }))
      .sort((a, b) => b.pages.length - a.pages.length),
    unclustered: changes.filter((c) => !clusteredPaths.has(c.path)),
  };
}

// ---------------------------------------------------------------------------
// Report writing
// ---------------------------------------------------------------------------

function writeReport(
  summaryPath: string,
  oldUrl: string,
  newUrl: string,
  pages: string[],
  errorCount: number,
  diffs: PageDiff[],
  navChanges: { path: string; description: string }[],
  commonPatterns: CommonPattern[],
  completed: number,
  total: number,
  executiveSummary?: string,
  clusterResult?: ClusterResult,
): void {
  const regressions = diffs.filter(
    (d) =>
      d.summary.includes("New console errors") ||
      d.summary.includes("New network errors") ||
      d.summary.includes("HTTP status") ||
      d.summary.includes("Visual change")
  );
  const unverified = diffs.filter((d) => d.summary.includes("Shinylive not verified:"));
  const improvements = diffs.filter(
    (d) =>
      !regressions.includes(d) &&
      !unverified.includes(d) &&
      (d.summary.includes("Resolved console errors") || d.summary.includes("Resolved network errors"))
  );

  const timestamp = summaryPath.match(/compare-versions-(.+)\.md$/)?.[1] ?? "";
  const lines: string[] = [];

  lines.push(`# Compare Versions Report — ${timestamp}`);
  lines.push(``);
  lines.push(`**Old:** ${oldUrl}`);
  lines.push(`**New:** ${newUrl}`);
  lines.push(`**Model:** claude-sonnet-4-6 via AWS Bedrock`);

  if (executiveSummary) {
    lines.push(``);
    lines.push(`## Executive Summary`);
    lines.push(``);
    lines.push(executiveSummary);
  }

  lines.push(``);
  lines.push(`| | |`);
  lines.push(`|---|---|`);
  lines.push(`| Total pages | ${pages.length} |`);
  lines.push(`| Compared | ${completed}/${total} |`);
  lines.push(`| Snapshot errors | ${errorCount} |`);
  lines.push(`| Regressions | ${regressions.length} |`);
  lines.push(`| Improvements | ${improvements.length} |`);
  lines.push(`| Shinylive not verified | ${unverified.length} |`);
  if (navChanges.length > 0) lines.push(`| Nav bar changes only | ${navChanges.length} |`);
  if (commonPatterns.length > 0) lines.push(`| Common patterns (5+ pages) | ${commonPatterns.length} |`);

  if (completed === total && diffs.length === 0 && navChanges.length === 0 && errorCount === 0) {
    lines.push(``);
    lines.push(`No differences found between old and new builds.`);
  }

  // Visual Changes
  const hasVisualDiffs = clusterResult && (clusterResult.clusters.length > 0 || clusterResult.unclustered.length > 0);
  if (hasVisualDiffs) {
    lines.push(``);
    lines.push(`## Visual Changes`);
    for (const { theme, pages: clusterPages } of clusterResult!.clusters) {
      lines.push(``);
      lines.push(`### ${theme} — ${clusterPages.length} pages`);
      lines.push(``);
      for (const p of clusterPages) lines.push(`- ${p}`);
    }
    if (clusterResult!.unclustered.length > 0) {
      lines.push(``);
      lines.push(`### Individual page changes`);
      lines.push(``);
      for (const { path, description } of clusterResult!.unclustered) {
        lines.push(`**\`${path}\`**: ${description}`);
        lines.push(``);
      }
    }
  }

  // New Network / Console Errors — group pages by error string
  const networkErrorMap = new Map<string, string[]>(); // error string → pages
  for (const d of regressions) {
    for (const line of d.summary.split("\n")) {
      const trimmed = line.trim();
      if (trimmed.startsWith("New network errors:") || trimmed.startsWith("New console errors:")) {
        const label = trimmed.startsWith("New network errors:") ? "New network errors" : "New console errors";
        const errPart = trimmed.replace(/^New (network|console) errors:\s*/, "");
        const key = `${label}: ${errPart}`;
        if (!networkErrorMap.has(key)) networkErrorMap.set(key, []);
        networkErrorMap.get(key)!.push(d.path);
      }
    }
  }
  if (networkErrorMap.size > 0) {
    lines.push(``);
    lines.push(`## New Errors`);
    for (const [errorStr, affectedPages] of networkErrorMap) {
      lines.push(``);
      lines.push(`### ${errorStr} — ${affectedPages.length} page${affectedPages.length > 1 ? "s" : ""}`);
      lines.push(``);
      for (const p of affectedPages) lines.push(`- ${p}`);
    }
  }

  // Navigation Bar Changes (keep existing logic)
  if (navChanges.length > 0) {
    const uniqueDescriptions = [...new Set(navChanges.map((c) => c.description))];
    lines.push(``);
    lines.push(`## Navigation Bar Changes (${navChanges.length} pages)`);
    lines.push(``);
    for (const desc of uniqueDescriptions) lines.push(`- ${desc}`);
    lines.push(``);
    for (const { path } of navChanges) lines.push(`  - ${path}`);
    lines.push(``);
  }

  // Shinylive not verified — compact list
  if (unverified.length > 0) {
    lines.push(``);
    lines.push(`## Shinylive Not Verified — ${unverified.length} pages`);
    lines.push(``);
    for (const d of unverified) lines.push(`- ${d.path}`);
    lines.push(``);
  }

  writeFileSync(summaryPath, lines.join("\n"));
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const { oldUrl, newUrl, filter, exclude } = parseArgs();

  console.log(`Old build: ${oldUrl}`);
  console.log(`New build: ${newUrl}\n`);

  // Union page lists from both builds so deleted pages are detected
  const [newPages, oldPages] = await Promise.all([getPages(newUrl), getPages(oldUrl)]);
  let pages = [...new Set([...newPages, ...oldPages])];

  if (pages.length === 0) {
    console.error("No pages found — check that llms.txt or sitemap.xml is accessible on at least one build.");
    process.exit(1);
  }

  if (filter) {
    pages = pages.filter((p) => p.includes(filter));
    if (pages.length === 0) {
      console.warn(`Warning: --filter "${filter}" matched no pages.`);
      process.exit(0);
    }
  }

  if (exclude) {
    pages = pages.filter((p) => !p.includes(exclude));
    if (pages.length === 0) {
      console.warn(`Warning: --exclude "${exclude}" removed all pages.`);
      process.exit(0);
    }
  }

  console.log(`Comparing ${pages.length} pages (concurrency: ${CONCURRENCY}, effective browser concurrency: ${CONCURRENCY * 2})...\n`);

  const browser = await chromium.launch();
  let snapshotCount = 0;

  const snapshots = await pooled(
    pages,
    CONCURRENCY,
    async (path) => {
      const [oldSnap, newSnap] = await Promise.all([
        snapshotPage(browser, oldUrl, path),
        snapshotPage(browser, newUrl, path),
      ]);
      // Increment and write atomically within the same microtask to keep count monotonic
      const n = ++snapshotCount;
      process.stdout.write(`\r  ${n}/${pages.length} pages snapshotted`);
      return { path, oldSnap, newSnap };
    },
    (_, i, err) => {
      const msg = err instanceof Error ? err.message : String(err);
      const errSnap: PageSnapshot = { path: "<error>", httpStatus: null, consoleErrors: [], networkErrors: [], observations: { kind: "error", message: msg } };
      return { path: `<error:${i}>`, oldSnap: errSnap, newSnap: errSnap };
    }
  );

  await browser.close();

  // Visual comparison pass — one Claude call per page pair, run serially after browser is done
  console.log(`\n\nRunning visual comparison on ${snapshots.length} page pairs...\n`);
  const diffs: PageDiff[] = [];
  const navChanges: { path: string; description: string }[] = [];
  let visualCount = 0;

  const errorCount = snapshots.filter((s) => s.path.startsWith("<error:")).length;
  const timestamp = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
  const summaryPath = join(__dirname, `compare-versions-${timestamp}.md`);

  for (const { path, oldSnap, newSnap } of snapshots) {
    // Skip sentinel error entries from pooled failures
    if (path.startsWith("<error:")) continue;

    const structuralDiffs = diffSnapshots(path, oldSnap, newSnap);

    let visualChange: string | null = null;
    if (oldSnap.observations.kind === "screenshot" && newSnap.observations.kind === "screenshot") {
      const oldData = oldSnap.observations.data;
      const newData = newSnap.observations.data;
      try {
        visualChange = await withRetry(() => compareScreenshots(oldData, newData));
      } catch (err) {
        visualChange = `Visual comparison error on ${path}: ${err instanceof Error ? err.message : String(err)}`;
      }
    }

    const allDiffs = [...structuralDiffs];
    if (visualChange === "SHINYLIVE_NOT_LOADED") {
      allDiffs.push("Shinylive not verified: did not load in time to be verified");
    } else if (visualChange?.startsWith("NAV_CHANGE:")) {
      // Always collect nav changes separately, even if structural diffs also exist
      navChanges.push({ path, description: visualChange.replace(/^NAV_CHANGE:\s*/, "").trim() });
    } else if (visualChange) {
      allDiffs.push(`Visual change: ${visualChange}`);
    }

    if (allDiffs.length > 0) {
      diffs.push({ path, summary: allDiffs.join("\n  ") });
    }

    const n = ++visualCount;
    process.stdout.write(`\r  ${n}/${snapshots.length} pages compared`);

    writeReport(summaryPath, oldUrl, newUrl, pages, errorCount, diffs, navChanges, [], n, snapshots.length, undefined, undefined);
  }

  const regressions = diffs.filter(
    (d) =>
      d.summary.includes("New console errors") ||
      d.summary.includes("New network errors") ||
      d.summary.includes("HTTP status") ||
      d.summary.includes("Visual change")
  );
  const unverified = diffs.filter((d) => d.summary.includes("Shinylive not verified:"));
  const improvements = diffs.filter(
    (d) =>
      !regressions.includes(d) &&
      !unverified.includes(d) &&
      (d.summary.includes("Resolved console errors") || d.summary.includes("Resolved network errors"))
  );

  // Extract visual changes for clustering
  const visualChanges = diffs
    .filter((d) => d.summary.includes("Visual change:"))
    .map((d) => {
      const match = d.summary.match(/Visual change: (.+?)(?:\n|$)/);
      return { path: d.path, description: match?.[1] ?? d.summary };
    });

  console.log(`\n\nClustering visual changes...`);
  const clusterResult = await clusterVisualChanges(visualChanges);
  const { commonPatterns } = extractCommonPatterns(diffs);

  console.log(`\n\nGenerating executive summary...`);
  const executiveSummary = await generateExecutiveSummary(regressions, commonPatterns, clusterResult);
  writeReport(summaryPath, oldUrl, newUrl, pages, errorCount, diffs, navChanges, commonPatterns, snapshots.length, snapshots.length, executiveSummary, clusterResult);

  console.log(`\n=== COMPARISON REPORT ===`);
  console.log(`Total pages:          ${pages.length}`);
  console.log(`Successfully compared:${pages.length - errorCount}`);
  console.log(`Snapshot errors:      ${errorCount}`);
  console.log(`Regressions:          ${regressions.length}`);
  console.log(`Improvements:         ${improvements.length}`);
  console.log(`Shinylive not verified:${unverified.length}`);
  console.log(`Nav bar changes only: ${navChanges.length}`);
  console.log(`\nFull report: ${summaryPath}`);

  process.exit(regressions.length > 0 ? 1 : 0);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
