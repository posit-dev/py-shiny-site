/**
 * Audits the built Quarto site for errors by crawling every page
 * listed in llms.txt using Playwright screenshots + Claude vision.
 *
 * Uses AWS Bedrock for Claude vision (no ANTHROPIC_API_KEY needed).
 *
 * Usage:
 *   # Serve the site first (e.g. on port 1414)
 *   make serve
 *
 *   # In another terminal
 *   cd tests && npm run audit -- --url http://localhost:1414
 *
 *   # Filter to specific section
 *   cd tests && npm run audit -- --url http://localhost:1414 --filter docs/
 */

import AnthropicBedrock from "@anthropic-ai/bedrock-sdk";
import sharp from "sharp";
import { chromium, type Browser } from "playwright";
import { writeFileSync } from "fs";
import { join } from "path";
import { __dirname, capturePage, getPages, pooled, withRetry } from "./shared.js";

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const DEFAULT_URL = "http://localhost:1414";
const CONCURRENCY = 3;

const bedrock = new AnthropicBedrock({ awsRegion: process.env.AWS_REGION ?? "us-east-1" });

interface PageResult {
  path: string;
  consoleErrors: string[];
  networkErrors: string[];
  observations: string;
  status: "ok" | "issues";
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function parseArgs(): { baseUrl: string; filter?: string } {
  const args = process.argv.slice(2);
  let baseUrl = DEFAULT_URL;
  let filter: string | undefined;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--url" && args[i + 1]) {
      baseUrl = args[++i];
      try { new URL(baseUrl); } catch { console.error(`Invalid --url: ${baseUrl}`); process.exit(1); }
    }
    if (args[i] === "--filter" && args[i + 1]) filter = args[++i];
  }

  return { baseUrl, filter };
}

async function analyzeScreenshot(screenshot: Buffer): Promise<string> {
  const resized = await sharp(screenshot).resize(640).toBuffer();

  const response = await withRetry(() =>
    bedrock.messages.create({
      model: "us.anthropic.claude-sonnet-4-6",
      max_tokens: 300,
      messages: [
        {
          role: "user",
          content: [
            {
              type: "image",
              source: { type: "base64", media_type: "image/png", data: resized.toString("base64") },
            },
            {
              type: "text",
              text: `You are auditing this documentation page viewport screenshot for visual or functional issues.
Note: this is viewport-only (top of the page), not a full-page scroll.
Check for:
- Broken layouts or overlapping elements
- Missing images or icons (broken image placeholders)
- Empty sections that should have content
- Navigation elements that look broken or missing
- Code blocks that aren't rendering properly
- Sidebar or header rendering issues

Be concise. If everything looks fine, respond with exactly "OK".
If there are issues, list each one in a single line with its location on the page.`,
            },
          ],
        },
      ],
    })
  );

  const block = response.content[0];
  return block.type === "text" ? block.text.trim() : "OK";
}

async function auditPage(browser: Browser, baseUrl: string, path: string): Promise<PageResult> {
  const captured = await capturePage(browser, `${baseUrl}${path}`);

  if ("error" in captured) {
    return { path, consoleErrors: [], networkErrors: [], observations: `Error: ${captured.error}`, status: "issues" };
  }

  const { httpStatus, consoleErrors, networkErrors, close, screenshot } = captured;

  try {
    if (httpStatus === null || httpStatus >= 400) {
      return { path, consoleErrors, networkErrors, observations: `HTTP ${httpStatus ?? "no response"}`, status: "issues" };
    }

    const raw = await screenshot({ fullPage: true });
    const observations = await analyzeScreenshot(raw);
    const hasIssues = !observations.startsWith("OK") || consoleErrors.length > 0 || networkErrors.length > 0;

    return { path, consoleErrors, networkErrors, observations, status: hasIssues ? "issues" : "ok" };
  } finally {
    await close();
  }
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const { baseUrl, filter } = parseArgs();

  console.log(`Fetching page list from ${baseUrl}...`);
  let pages = await getPages(baseUrl);

  if (pages.length === 0) {
    console.error("No pages found — check that llms.txt or sitemap.xml is accessible.");
    process.exit(1);
  }

  if (filter) {
    pages = pages.filter((p) => p.includes(filter));
    if (pages.length === 0) {
      console.warn(`Warning: --filter "${filter}" matched no pages.`);
      process.exit(0);
    }
  }

  console.log(`Auditing ${pages.length} pages (concurrency: ${CONCURRENCY})...\n`);

  const browser = await chromium.launch();
  let completed = 0;

  const results = await pooled(
    pages,
    CONCURRENCY,
    async (path) => {
      const result = await auditPage(browser, baseUrl, path);
      process.stdout.write(result.status === "ok" ? "." : "x");
      completed++;
      return result;
    },
    (_, i, err) => {
      const msg = err instanceof Error ? err.message : String(err);
      process.stdout.write("x");
      return { path: pages[i] ?? "<error>", consoleErrors: [], networkErrors: [], observations: `Error: ${msg}`, status: "issues" as const };
    }
  );

  await browser.close();

  const issues = results.filter((r) => r.status === "issues");

  // Write markdown report
  const timestamp = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
  const summaryPath = join(__dirname, `audit-site-${timestamp}.md`);
  const lines: string[] = [];

  lines.push(`# Audit Report — ${timestamp}`);
  lines.push(``);
  lines.push(`**URL:** ${baseUrl}`);
  lines.push(`**Model:** claude-sonnet-4-6 via AWS Bedrock`);
  lines.push(``);
  lines.push(`| | |`);
  lines.push(`|---|---|`);
  lines.push(`| Total pages | ${results.length} |`);
  lines.push(`| Pages with issues | ${issues.length} |`);
  lines.push(`| Clean | ${results.length - issues.length} |`);

  if (issues.length > 0) {
    lines.push(``);
    lines.push(`## Issues (${issues.length})`);
    lines.push(``);
    for (const r of issues) {
      lines.push(`### ${r.path}`);
      lines.push(``);
      if (r.consoleErrors.length) lines.push(`**Console errors:** ${r.consoleErrors.join("; ")}`);
      if (r.networkErrors.length) lines.push(`**Network errors:** ${r.networkErrors.join("; ")}`);
      if (r.observations !== "OK") lines.push(`**Observations:** ${r.observations}`);
      lines.push(``);
    }
  }

  writeFileSync(summaryPath, lines.join("\n"));

  console.log(`\n\n=== AUDIT COMPLETE ===`);
  console.log(`Total pages:      ${results.length}`);
  console.log(`Pages with issues: ${issues.length}`);
  console.log(`\nFull report: ${summaryPath}`);

  process.exit(issues.length > 0 ? 1 : 0);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
