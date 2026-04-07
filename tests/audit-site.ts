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

import { BedrockRuntimeClient, InvokeModelCommand } from "@aws-sdk/client-bedrock-runtime";
import { chromium, type Browser, type ConsoleMessage, type Request } from "playwright";

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const DEFAULT_URL = "http://localhost:1414";
const CONCURRENCY = 3;

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

const bedrock = new BedrockRuntimeClient({ region: process.env.AWS_REGION ?? "us-east-1" });

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
    if (args[i] === "--url" && args[i + 1]) baseUrl = args[++i];
    if (args[i] === "--filter" && args[i + 1]) filter = args[++i];
  }

  return { baseUrl, filter };
}

async function getPages(baseUrl: string): Promise<string[]> {
  const res = await fetch(`${baseUrl}/llms.txt`);
  if (!res.ok) {
    throw new Error(
      `Failed to fetch ${baseUrl}/llms.txt (${res.status}). Is the site being served?`
    );
  }
  const text = await res.text();
  return [...text.matchAll(/\]\((.+?)\.llms\.md\)/g)].map((m) => `/${m[1]}.html`);
}

async function analyzeScreenshot(screenshot: Buffer): Promise<string> {
  const payload = {
    anthropic_version: "bedrock-2023-05-31",
    max_tokens: 300,
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
            text: `You are auditing this documentation page screenshot for visual or functional issues.
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
  };

  const command = new InvokeModelCommand({
    modelId: "us.anthropic.claude-sonnet-4-6",
    contentType: "application/json",
    accept: "application/json",
    body: JSON.stringify(payload),
  });

  const response = await bedrock.send(command);
  const result = JSON.parse(new TextDecoder().decode(response.body));
  return (result.content[0]?.text ?? "OK").trim();
}

async function auditPage(browser: Browser, baseUrl: string, path: string): Promise<PageResult> {
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();

  const consoleErrors: string[] = [];
  const networkErrors: string[] = [];

  page.on("console", (msg: ConsoleMessage) => {
    if (msg.type() === "error") {
      const text = msg.text();
      // Shinylive preload errors are expected on pages with interactive examples
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
    // Wait a bit for JS to settle, but don't wait for networkidle
    // (Shinylive embeds and external iframes may never go idle)
    await page.waitForTimeout(3000);

    if (!response || response.status() >= 400) {
      await context.close();
      return {
        path,
        consoleErrors,
        networkErrors,
        observations: `HTTP ${response?.status() ?? "no response"}`,
        status: "issues",
      };
    }

    const screenshot = await page.screenshot({ fullPage: true });
    const observations = await analyzeScreenshot(screenshot);
    await context.close();

    const hasIssues =
      !observations.startsWith("OK") ||
      consoleErrors.length > 0 ||
      networkErrors.length > 0;

    return {
      path,
      consoleErrors,
      networkErrors,
      observations,
      status: hasIssues ? "issues" : "ok",
    };
  } catch (err) {
    await context.close();
    return {
      path,
      consoleErrors,
      networkErrors,
      observations: `Error: ${err instanceof Error ? err.message : String(err)}`,
      status: "issues",
    };
  }
}

/** Run promises with bounded concurrency. */
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
  const { baseUrl, filter } = parseArgs();

  console.log(`Fetching page list from ${baseUrl}/llms.txt...`);
  let pages = await getPages(baseUrl);

  if (filter) {
    pages = pages.filter((p) => p.includes(filter));
  }

  console.log(`Auditing ${pages.length} pages (concurrency: ${CONCURRENCY})...\n`);

  const browser = await chromium.launch();
  const results = await pooled(pages, CONCURRENCY, (path) => {
    process.stdout.write(`.`);
    return auditPage(browser, baseUrl, path);
  });
  await browser.close();

  // Report
  const issues = results.filter((r) => r.status === "issues");

  console.log(`\n\n=== AUDIT COMPLETE ===`);
  console.log(`Total pages: ${results.length}`);
  console.log(`Pages with issues: ${issues.length}\n`);

  for (const r of issues) {
    console.log(`--- ${r.path} ---`);
    if (r.consoleErrors.length) console.log("  Console errors:", r.consoleErrors);
    if (r.networkErrors.length) console.log("  Network errors:", r.networkErrors);
    if (r.observations !== "OK") console.log("  Observations:", r.observations);
    console.log();
  }

  process.exit(issues.length > 0 ? 1 : 0);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
