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
  status: "ok" | "needs-investigation" | "likely-false-alarm" | "network-errors";
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function parseArgs(): { baseUrl: string; filter?: string; exclude?: string } {
  const args = process.argv.slice(2);
  let baseUrl = DEFAULT_URL;
  let filter: string | undefined;
  let exclude: string | undefined;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--url" && args[i + 1]) {
      baseUrl = args[++i];
      try { new URL(baseUrl); } catch { console.error(`Invalid --url: ${baseUrl}`); process.exit(1); }
    }
    if (args[i] === "--filter" && args[i + 1]) filter = args[++i];
    if (args[i] === "--exclude" && args[i + 1]) exclude = args[++i];
  }

  return { baseUrl, filter, exclude };
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
If the ONLY issue is a Shinylive app showing a loading spinner or placeholder (grey dotted circular pattern), respond with exactly "LIKELY_FALSE_ALARM: Shinylive did not load in time to be verified".
If there are real issues, list each one in a single line with its location on the page.`,
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
    return { path, consoleErrors: [], networkErrors: [], observations: `Error: ${captured.error}`, status: "needs-investigation" };
  }

  const { httpStatus, consoleErrors, networkErrors, close, screenshot } = captured;

  try {
    if (httpStatus === null || httpStatus >= 400) {
      return { path, consoleErrors, networkErrors, observations: `HTTP ${httpStatus ?? "no response"}`, status: "needs-investigation" };
    }

    const raw = await screenshot();

    const observations = await analyzeScreenshot(raw);

    if (observations.startsWith("LIKELY_FALSE_ALARM:")) {
      return { path, consoleErrors, networkErrors, observations: observations.replace(/^LIKELY_FALSE_ALARM:\s*/, ""), status: "likely-false-alarm" };
    }

    const hasVisualOrConsole = !observations.startsWith("OK") || consoleErrors.length > 0;
    if (hasVisualOrConsole) return { path, consoleErrors, networkErrors, observations, status: "needs-investigation" };
    if (networkErrors.length > 0) return { path, consoleErrors, networkErrors, observations, status: "network-errors" };
    return { path, consoleErrors, networkErrors, observations, status: "ok" };
  } finally {
    await close();
  }
}

// ---------------------------------------------------------------------------
// Executive summary
// ---------------------------------------------------------------------------

async function generateExecutiveSummary(results: PageResult[]): Promise<string> {
  const needsInvestigation = results.filter((r) => r.status === "needs-investigation");
  if (needsInvestigation.length === 0) return "No issues requiring investigation were found.";

  const findingsList = needsInvestigation.map((r) => {
    const parts = [`Page: ${r.path}`];
    if (r.consoleErrors.length) parts.push(`Console errors: ${r.consoleErrors.join("; ")}`);
    if (r.networkErrors.length) parts.push(`Network errors: ${r.networkErrors.join("; ")}`);
    if (r.observations && r.observations !== "OK") parts.push(`Observations: ${r.observations}`);
    return parts.join("\n  ");
  }).join("\n\n");

  const response = await withRetry(() =>
    bedrock.messages.create({
      model: "us.anthropic.claude-sonnet-4-6",
      max_tokens: 400,
      messages: [{
        role: "user",
        content: `You are reviewing the results of a documentation site audit. Here are the flagged pages:\n\n${findingsList}\n\nWrite a brief executive summary of the most likely actual issues in order of priority. Be concise — use bullet points, 1 sentence each. Skip anything that sounds like a tool or rendering artifact rather than a real site problem.`,
      }],
    })
  );

  const block = response.content[0];
  const text = block.type === "text" ? block.text.trim() : "";
  return text.replace(/^##?\s*Executive Summary\s*\n+/i, "").trim();
}

// ---------------------------------------------------------------------------
// Observation clustering
// ---------------------------------------------------------------------------

interface ObsCluster {
  theme: string;
  pages: string[];
}
interface ObsClusterResult {
  clusters: ObsCluster[];
  unclustered: { path: string; observation: string }[];
}

async function clusterObservations(
  items: { path: string; observation: string }[]
): Promise<ObsClusterResult> {
  if (items.length === 0) return { clusters: [], unclustered: [] };
  if (items.length === 1) return { clusters: [], unclustered: items };

  const list = items.map((i) => `- ${i.path}: ${i.observation}`).join("\n");

  let raw: string;
  try {
    const response = await withRetry(() =>
      bedrock.messages.create({
        model: "us.anthropic.claude-sonnet-4-6",
        max_tokens: 2048,
        messages: [{
          role: "user",
          content: `Group these page observations from a site audit by theme. Only group pages whose observations describe the same underlying issue. Minimum cluster size is 2. Pages with unique issues go in "unclustered".

Return valid JSON only, no prose, no markdown code fences:
{"clusters":[{"theme":"short description of the shared issue","pages":["/path1","/path2"]}],"unclustered":[{"path":"/path3","observation":"original observation"}]}

Observations:
${list}`,
        }],
      })
    );
    const block = response.content[0];
    raw = block.type === "text" ? block.text.trim().replace(/^```(?:json)?\n?/, "").replace(/\n?```$/, "") : "{}";
  } catch {
    return { clusters: [], unclustered: items };
  }

  try {
    const parsed = JSON.parse(raw) as ObsClusterResult;
    return {
      clusters: parsed.clusters ?? [],
      unclustered: parsed.unclustered ?? [],
    };
  } catch {
    return { clusters: [], unclustered: items };
  }
}

// ---------------------------------------------------------------------------
// Report writing
// ---------------------------------------------------------------------------

function writeAuditReport(summaryPath: string, baseUrl: string, results: PageResult[], total: number, executiveSummary?: string, clusterResult?: ObsClusterResult): void {
  const needsInvestigation = results.filter((r) => r.status === "needs-investigation");
  const likelyFalseAlarms = results.filter((r) => r.status === "likely-false-alarm");
  const networkErrors = results.filter((r) => r.status === "network-errors");
  const timestamp = summaryPath.match(/audit-site-(.+)\.md$/)?.[1] ?? "";
  const lines: string[] = [];

  lines.push(`# Audit Report — ${timestamp}`);
  lines.push(``);
  lines.push(`**URL:** ${baseUrl}`);
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
  lines.push(`| Total pages | ${total} |`);
  lines.push(`| Audited | ${results.length}/${total} |`);
  lines.push(`| Requires further investigation | ${needsInvestigation.length} |`);
  lines.push(`| Likely false alarms | ${likelyFalseAlarms.length} |`);
  lines.push(`| Network errors only | ${networkErrors.length} |`);
  lines.push(`| Clean | ${results.filter((r) => r.status === "ok").length} |`);

  // Issues — clustered if clusterResult provided, else per-page fallback
  if (needsInvestigation.length > 0) {
    lines.push(``);
    lines.push(`## Issues`);
    if (clusterResult && (clusterResult.clusters.length > 0 || clusterResult.unclustered.length > 0)) {
      for (const { theme, pages: clusterPages } of clusterResult.clusters) {
        lines.push(``);
        lines.push(`### ${theme} — ${clusterPages.length} pages`);
        lines.push(``);
        for (const p of clusterPages) lines.push(`- ${p}`);
      }
      if (clusterResult.unclustered.length > 0) {
        lines.push(``);
        lines.push(`### Individual page issues`);
        lines.push(``);
        for (const { path, observation } of clusterResult.unclustered) {
          lines.push(`**\`${path}\`**: ${observation}`);
          lines.push(``);
        }
      }
    } else {
      // Fallback: per-page entries (used during incremental writes before clustering is done)
      for (const r of needsInvestigation) {
        lines.push(``);
        lines.push(`### ${r.path}`);
        lines.push(``);
        if (r.consoleErrors.length) lines.push(`**Console errors:** ${r.consoleErrors.join("; ")}`);
        if (r.networkErrors.length) lines.push(`**Network errors:** ${r.networkErrors.join("; ")}`);
        if (r.observations !== "OK") lines.push(`**Observations:** ${r.observations}`);
        lines.push(``);
      }
    }
  }

  // Likely False Alarms — grouped by reason
  if (likelyFalseAlarms.length > 0) {
    lines.push(``);
    lines.push(`## Likely False Alarms — ${likelyFalseAlarms.length} pages`);
    const byReason = new Map<string, string[]>();
    for (const r of likelyFalseAlarms) {
      const reason = r.observations || "Unknown reason";
      if (!byReason.has(reason)) byReason.set(reason, []);
      byReason.get(reason)!.push(r.path);
    }
    for (const [reason, paths] of byReason) {
      lines.push(``);
      lines.push(`### ${reason} — ${paths.length} pages`);
      lines.push(``);
      for (const p of paths) lines.push(`- ${p}`);
    }
    lines.push(``);
  }

  // Network errors only — compact list
  if (networkErrors.length > 0) {
    lines.push(``);
    lines.push(`## Network Errors Only — ${networkErrors.length} pages`);
    lines.push(``);
    for (const r of networkErrors) lines.push(`- ${r.path}`);
    lines.push(``);
  }

  writeFileSync(summaryPath, lines.join("\n"));
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const { baseUrl, filter, exclude } = parseArgs();

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

  if (exclude) {
    pages = pages.filter((p) => !p.includes(exclude));
    if (pages.length === 0) {
      console.warn(`Warning: --exclude "${exclude}" removed all pages.`);
      process.exit(0);
    }
  }

  console.log(`Auditing ${pages.length} pages (concurrency: ${CONCURRENCY})...\n`);

  const browser = await chromium.launch();
  const timestamp = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
  const summaryPath = join(__dirname, `audit-site-${timestamp}.md`);
  const completedResults: PageResult[] = [];

  await pooled(
    pages,
    CONCURRENCY,
    async (path) => {
      const result = await auditPage(browser, baseUrl, path);
      process.stdout.write(result.status === "ok" ? "." : result.status === "likely-false-alarm" ? "?" : result.status === "network-errors" ? "n" : "x");
      completedResults.push(result);
      writeAuditReport(summaryPath, baseUrl, completedResults, pages.length);
      return result;
    },
    (_, i, err) => {
      const msg = err instanceof Error ? err.message : String(err);
      process.stdout.write("x");
      const result: PageResult = { path: pages[i] ?? "<error>", consoleErrors: [], networkErrors: [], observations: `Error: ${msg}`, status: "needs-investigation" as const };
      completedResults.push(result);
      writeAuditReport(summaryPath, baseUrl, completedResults, pages.length);
      return result;
    }
  );

  await browser.close();

  const needsInvestigation = completedResults.filter((r) => r.status === "needs-investigation");
  const likelyFalseAlarms = completedResults.filter((r) => r.status === "likely-false-alarm");
  const networkErrorsOnly = completedResults.filter((r) => r.status === "network-errors");

  console.log(`\n\nGenerating executive summary...`);
  const executiveSummary = await generateExecutiveSummary(completedResults);

  // Cluster observations for grouped report
  const obsItems = completedResults
    .filter((r) => r.status === "needs-investigation" && r.observations && r.observations !== "OK")
    .map((r) => ({ path: r.path, observation: r.observations }));

  console.log(`\nClustering observations...`);
  const clusterResult = await clusterObservations(obsItems);
  writeAuditReport(summaryPath, baseUrl, completedResults, pages.length, executiveSummary, clusterResult);

  console.log(`\n=== AUDIT COMPLETE ===`);
  console.log(`Total pages:                   ${pages.length}`);
  console.log(`Requires further investigation: ${needsInvestigation.length}`);
  console.log(`Likely false alarms:            ${likelyFalseAlarms.length}`);
  console.log(`Network errors only:            ${networkErrorsOnly.length}`);
  console.log(`\nFull report: ${summaryPath}`);

  process.exit(needsInvestigation.length > 0 ? 1 : 0);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
