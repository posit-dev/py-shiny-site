/**
 * Compares two builds of the site (old vs new) by crawling every page
 * and reporting differences in errors, network failures, and visual rendering.
 *
 * Requires ANTHROPIC_API_KEY in environment.
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

import Anthropic from "@anthropic-ai/sdk";
import { chromium, type Browser, type ConsoleMessage, type Request } from "playwright";

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const DEFAULT_OLD = "http://localhost:1414";
const DEFAULT_NEW = "http://localhost:1415";
const CONCURRENCY = 2;

const NOISE_PATTERNS = [
  "google-analytics.com",
  "googletagmanager.com",
  "plausible.io/js",
  "plausible.io/api",
  "shinyapps.io",
];

function isNoise(url: string): boolean {
  return NOISE_PATTERNS.some((p) => url.includes(p));
}

const hasApiKey = !!process.env.ANTHROPIC_API_KEY;
const anthropic = hasApiKey ? new Anthropic() : null;

interface PageSnapshot {
  path: string;
  httpStatus: number | null;
  consoleErrors: string[];
  networkErrors: string[];
  observations: string;
}

interface PageDiff {
  path: string;
  old: PageSnapshot;
  new: PageSnapshot;
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
    if (args[i] === "--old" && args[i + 1]) oldUrl = args[++i];
    if (args[i] === "--new" && args[i + 1]) newUrl = args[++i];
    if (args[i] === "--filter" && args[i + 1]) filter = args[++i];
  }

  return { oldUrl, newUrl, filter };
}

async function getPages(baseUrl: string): Promise<string[]> {
  // Try llms.txt first (available on new build), fall back to sitemap
  for (const path of ["/llms.txt", "/sitemap.xml"]) {
    try {
      const res = await fetch(`${baseUrl}${path}`);
      if (!res.ok) continue;
      const text = await res.text();

      if (path === "/llms.txt") {
        return [...text.matchAll(/\]\((.+?)\.llms\.md\)/g)].map((m) => `/${m[1]}.html`);
      }
      // sitemap.xml fallback
      return [...text.matchAll(/<loc>(.+?)<\/loc>/g)]
        .map((m) => new URL(m[1]).pathname)
        .filter((p) => p.endsWith(".html"));
    } catch {
      continue;
    }
  }
  throw new Error(`Could not find page list from either build. Are both servers running?`);
}

async function describeScreenshot(screenshot: Buffer): Promise<string> {
  if (!anthropic) return "(visual analysis skipped — no ANTHROPIC_API_KEY)";

  const response = await anthropic.messages.create({
    model: "claude-sonnet-4-6-20250514",
    max_tokens: 200,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "image",
            source: { type: "base64", media_type: "image/png", data: screenshot.toString("base64") },
          },
          {
            type: "text",
            text: `Describe the visual state of this documentation page in 2-3 sentences.
Note: the page layout, whether content is visible, if code blocks render,
if navigation/sidebar works, and any broken images or empty sections.
Be factual and concise.`,
          },
        ],
      },
    ],
  });

  const block = response.content[0];
  return block.type === "text" ? block.text.trim() : "";
}

async function snapshotPage(
  browser: Browser,
  baseUrl: string,
  path: string
): Promise<PageSnapshot> {
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();

  const consoleErrors: string[] = [];
  const networkErrors: string[] = [];

  page.on("console", (msg: ConsoleMessage) => {
    if (msg.type() === "error") {
      const text = msg.text();
      if (!text.startsWith("preload error:")) consoleErrors.push(text);
    }
  });

  page.on("requestfailed", (req: Request) => {
    const url = req.url();
    if (!isNoise(url)) {
      networkErrors.push(`${req.failure()?.errorText}: ${url}`);
    }
  });

  try {
    const response = await page.goto(`${baseUrl}${path}`, {
      waitUntil: "domcontentloaded",
      timeout: 30_000,
    });
    await page.waitForTimeout(3000);

    const httpStatus = response?.status() ?? null;

    if (!response || httpStatus === null || httpStatus >= 400) {
      await context.close();
      return { path, httpStatus, consoleErrors, networkErrors, observations: `HTTP ${httpStatus}` };
    }

    const screenshot = await page.screenshot({ fullPage: true });
    const observations = await describeScreenshot(screenshot);
    await context.close();

    return { path, httpStatus, consoleErrors, networkErrors, observations };
  } catch (err) {
    await context.close();
    return {
      path,
      httpStatus: null,
      consoleErrors,
      networkErrors,
      observations: `Error: ${err instanceof Error ? err.message : String(err)}`,
    };
  }
}

function diffSnapshots(old: PageSnapshot, new_: PageSnapshot): PageDiff | null {
  const diffs: string[] = [];

  // HTTP status change
  if (old.httpStatus !== new_.httpStatus) {
    diffs.push(`HTTP status: ${old.httpStatus} -> ${new_.httpStatus}`);
  }

  // New console errors
  const newConsoleErrors = new_.consoleErrors.filter((e) => !old.consoleErrors.includes(e));
  if (newConsoleErrors.length) {
    diffs.push(`New console errors: ${newConsoleErrors.join("; ")}`);
  }

  // New network errors
  const newNetworkErrors = new_.networkErrors.filter((e) => !old.networkErrors.includes(e));
  if (newNetworkErrors.length) {
    diffs.push(`New network errors: ${newNetworkErrors.join("; ")}`);
  }

  // Resolved errors (improvements)
  const resolvedConsole = old.consoleErrors.filter((e) => !new_.consoleErrors.includes(e));
  if (resolvedConsole.length) {
    diffs.push(`Resolved console errors: ${resolvedConsole.join("; ")}`);
  }

  // Visual differences (compare observations)
  if (old.observations !== new_.observations) {
    diffs.push(`Visual change:\n    Old: ${old.observations}\n    New: ${new_.observations}`);
  }

  if (diffs.length === 0) return null;

  return {
    path: old.path,
    old,
    new: new_,
    summary: diffs.join("\n  "),
  };
}

async function pooled<T, R>(items: T[], concurrency: number, fn: (item: T) => Promise<R>): Promise<R[]> {
  const results: R[] = [];
  let index = 0;

  async function worker() {
    while (index < items.length) {
      const i = index++;
      results[i] = await fn(items[i]);
    }
  }

  await Promise.all(Array.from({ length: Math.min(concurrency, items.length) }, worker));
  return results;
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const { oldUrl, newUrl, filter } = parseArgs();

  console.log(`Old build: ${oldUrl}`);
  console.log(`New build: ${newUrl}\n`);

  // Get pages from whichever build has them
  let pages: string[];
  try {
    pages = await getPages(newUrl);
  } catch {
    pages = await getPages(oldUrl);
  }

  if (filter) {
    pages = pages.filter((p) => p.includes(filter));
  }

  console.log(`Comparing ${pages.length} pages (concurrency: ${CONCURRENCY})...\n`);

  const browser = await chromium.launch();

  const diffs: PageDiff[] = [];
  let completed = 0;

  await pooled(pages, CONCURRENCY, async (path) => {
    const [oldSnap, newSnap] = await Promise.all([
      snapshotPage(browser, oldUrl, path),
      snapshotPage(browser, newUrl, path),
    ]);

    const diff = diffSnapshots(oldSnap, newSnap);
    if (diff) diffs.push(diff);

    completed++;
    process.stdout.write(`\r  ${completed}/${pages.length} pages compared`);
  });

  await browser.close();

  // Report
  console.log(`\n\n=== COMPARISON REPORT ===`);
  console.log(`Total pages: ${pages.length}`);
  console.log(`Pages with differences: ${diffs.length}\n`);

  if (diffs.length === 0) {
    console.log("No differences found between old and new builds.");
    return;
  }

  // Group by severity
  const regressions = diffs.filter(
    (d) =>
      d.summary.includes("New console errors") ||
      d.summary.includes("New network errors") ||
      d.summary.includes("HTTP status")
  );
  const visualChanges = diffs.filter((d) => !regressions.includes(d));

  if (regressions.length) {
    console.log(`\n## Regressions (${regressions.length})\n`);
    for (const d of regressions) {
      console.log(`  ${d.path}`);
      console.log(`  ${d.summary}\n`);
    }
  }

  if (visualChanges.length) {
    console.log(`\n## Visual Changes (${visualChanges.length})\n`);
    for (const d of visualChanges) {
      console.log(`  ${d.path}`);
      console.log(`  ${d.summary}\n`);
    }
  }

  process.exit(regressions.length > 0 ? 1 : 0);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
