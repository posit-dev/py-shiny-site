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

function parseArgs(): { oldUrl: string; newUrl: string; filter?: string } {
  const args = process.argv.slice(2);
  let oldUrl = DEFAULT_OLD;
  let newUrl = DEFAULT_NEW;
  let filter: string | undefined;

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
  }

  return { oldUrl, newUrl, filter };
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
If they look the same, respond with exactly "SAME". Otherwise describe what changed in one sentence.`,
            },
          ],
        },
      ],
    })
  );

  const block = response.content[0];
  const text = block.type === "text" ? block.text.trim() : "SAME";
  return text === "SAME" ? null : text;
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
  if (newConsole.length) diffs.push(`New console errors: ${newConsole.join("; ")}`);
  if (resolvedConsole.length) diffs.push(`Resolved console errors: ${resolvedConsole.join("; ")}`);

  // Network errors (also normalized)
  const oldNetNorm = old.networkErrors.map(normalizeError);
  const newNetNorm = new_.networkErrors.map(normalizeError);
  const newNetwork = newNetNorm.filter((e) => !oldNetNorm.includes(e));
  const resolvedNetwork = oldNetNorm.filter((e) => !newNetNorm.includes(e));
  if (newNetwork.length) diffs.push(`New network errors: ${newNetwork.join("; ")}`);
  if (resolvedNetwork.length) diffs.push(`Resolved network errors: ${resolvedNetwork.join("; ")}`);

  return diffs;
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const { oldUrl, newUrl, filter } = parseArgs();

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
  let visualCount = 0;

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
    if (visualChange) allDiffs.push(`Visual change: ${visualChange}`);

    if (allDiffs.length > 0) {
      diffs.push({ path, summary: allDiffs.join("\n  ") });
    }

    const n = ++visualCount;
    process.stdout.write(`\r  ${n}/${snapshots.length} pages compared`);
  }

  const errorCount = snapshots.filter((s) => s.path.startsWith("<error:")).length;

  // Group by severity
  const regressions = diffs.filter(
    (d) =>
      d.summary.includes("New console errors") ||
      d.summary.includes("New network errors") ||
      d.summary.includes("HTTP status") ||
      d.summary.includes("Visual change")
  );
  const improvements = diffs.filter(
    (d) =>
      !regressions.includes(d) &&
      (d.summary.includes("Resolved console errors") || d.summary.includes("Resolved network errors"))
  );

  // Write markdown summary — timestamp in filename to avoid same-day overwrites
  const timestamp = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
  const summaryPath = join(__dirname, `compare-versions-${timestamp}.md`);
  const lines: string[] = [];

  lines.push(`# Compare Versions Report — ${timestamp}`);
  lines.push(``);
  lines.push(`**Old:** ${oldUrl}`);
  lines.push(`**New:** ${newUrl}`);
  lines.push(`**Model:** claude-sonnet-4-6 via AWS Bedrock`);
  lines.push(``);
  lines.push(`| | |`);
  lines.push(`|---|---|`);
  lines.push(`| Total pages | ${pages.length} |`);
  lines.push(`| Successfully compared | ${pages.length - errorCount} |`);
  lines.push(`| Snapshot errors | ${errorCount} |`);
  lines.push(`| Regressions | ${regressions.length} |`);
  lines.push(`| Improvements | ${improvements.length} |`);

  if (diffs.length === 0 && errorCount === 0) {
    lines.push(``);
    lines.push(`No differences found between old and new builds.`);
  }

  for (const [heading, group] of [["Regressions", regressions], ["Improvements", improvements]] as const) {
    if (group.length === 0) continue;
    lines.push(``);
    lines.push(`## ${heading} (${group.length})`);
    lines.push(``);
    for (const d of group) {
      lines.push(`### ${d.path}`);
      lines.push(``);
      lines.push(d.summary.split("\n").map((l) => `  ${l}`).join("\n"));
      lines.push(``);
    }
  }

  writeFileSync(summaryPath, lines.join("\n"));

  console.log(`\n\n=== COMPARISON REPORT ===`);
  console.log(`Total pages:          ${pages.length}`);
  console.log(`Successfully compared:${pages.length - errorCount}`);
  console.log(`Snapshot errors:      ${errorCount}`);
  console.log(`Regressions:          ${regressions.length}`);
  console.log(`Improvements:         ${improvements.length}`);
  console.log(`\nFull report: ${summaryPath}`);

  process.exit(regressions.length > 0 ? 1 : 0);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
