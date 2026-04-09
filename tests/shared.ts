/**
 * Shared utilities for audit-site.ts and compare-versions.ts.
 */

import { type Browser, type ConsoleMessage, type Request } from "playwright";
import { fileURLToPath } from "url";
import { dirname } from "path";

// ---------------------------------------------------------------------------
// ESM __dirname shim
// ---------------------------------------------------------------------------

export const __dirname = dirname(fileURLToPath(import.meta.url));

// ---------------------------------------------------------------------------
// Noise filtering
// ---------------------------------------------------------------------------

const NOISE_PATTERNS = [
  "google-analytics.com",
  "googletagmanager.com",
  "plausible.io/js",
  "plausible.io/api",
  "shinyapps.io",
];

export function isNoise(url: string): boolean {
  return NOISE_PATTERNS.some((p) => url.includes(p));
}

// ---------------------------------------------------------------------------
// Page list discovery
// ---------------------------------------------------------------------------

export async function getPages(baseUrl: string): Promise<string[]> {
  for (const path of ["/llms.txt", "/sitemap.xml"]) {
    try {
      const res = await fetch(`${baseUrl}${path}`);
      if (!res.ok) continue;
      const text = await res.text();

      let pages: string[];
      if (path === "/llms.txt") {
        pages = [...text.matchAll(/\]\((.+?)\.llms\.md\)/g)].map((m) => `/${m[1]}.html`);
      } else {
        pages = [...text.matchAll(/<loc>(.+?)<\/loc>/g)]
          .map((m) => new URL(m[1]).pathname)
          .filter((p) => p.endsWith(".html"));
      }

      // Validate all paths start with "/" to catch malformed matches
      return pages.filter((p) => p.startsWith("/"));
    } catch {
      continue;
    }
  }
  return [];
}

// ---------------------------------------------------------------------------
// Concurrency pool
//
// Safety: `nextIndex++` is a synchronous read-modify-write. This is safe in
// Node.js's single-threaded event loop because workers only yield at `await`.
// Do NOT use this in Worker thread contexts where true parallelism applies.
// ---------------------------------------------------------------------------

export async function pooled<T, R>(
  items: T[],
  concurrency: number,
  fn: (item: T) => Promise<R>,
  onError: (item: T, index: number, err: unknown) => R,
): Promise<R[]> {
  const results: R[] = new Array(items.length);
  let nextIndex = 0;

  async function worker() {
    while (nextIndex < items.length) {
      const i = nextIndex++;
      try {
        results[i] = await fn(items[i]);
      } catch (err) {
        results[i] = onError(items[i], i, err);
      }
    }
  }

  await Promise.all(Array.from({ length: Math.min(concurrency, items.length) }, worker));
  return results;
}

// ---------------------------------------------------------------------------
// Retry wrapper for transient Bedrock errors (throttling, transient 5xx)
// ---------------------------------------------------------------------------

function isRetryable(err: unknown): boolean {
  const msg = err instanceof Error ? err.message : String(err);
  return /429|503|500|timeout|ECONNRESET|ETIMEDOUT/i.test(msg);
}

export async function withRetry<T>(fn: () => Promise<T>, retries = 3, delayMs = 2000): Promise<T> {
  if (retries < 1) throw new Error("retries must be >= 1");
  for (let i = 0; i < retries; i++) {
    try {
      return await fn();
    } catch (err) {
      const isLast = i === retries - 1;
      if (isLast || !isRetryable(err)) throw err;
      await new Promise((r) => setTimeout(r, delayMs * (i + 1)));
    }
  }
  // Unreachable: loop always throws or returns before exhausting retries
  throw new Error("withRetry: exhausted retries");
}

// ---------------------------------------------------------------------------
// Error message normalization (strip dynamic content before comparing)
// ---------------------------------------------------------------------------

export function normalizeError(msg: string): string {
  return msg
    .replace(/https?:\/\/\S+/g, "<url>")          // URLs
    .replace(/^\s*at\s+\S.*$/gm, "")              // stack frame lines (anchored to line start)
    .replace(/[a-f0-9]{8,}/gi, "<id>")            // hex IDs / hashes
    .replace(/\d{4,}/g, "<n>")                    // long numbers (timestamps, ports)
    .trim();
}

// ---------------------------------------------------------------------------
// Shared page capture — handles context lifecycle, event wiring, navigation
// ---------------------------------------------------------------------------

export interface CapturedPage {
  httpStatus: number | null;
  consoleErrors: string[];
  networkErrors: string[];
  /** Release the browser context. Always call this when done. */
  close: () => Promise<void>;
  /** Take a screenshot. Caller is responsible for resizing. */
  screenshot: (options?: { fullPage?: boolean }) => Promise<Buffer>;
}

export async function capturePage(
  browser: Browser,
  url: string
): Promise<CapturedPage | { error: string }> {
  let context;
  const consoleErrors: string[] = [];
  const networkErrors: string[] = [];

  try {
    context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    const page = await context.newPage();

    page.on("console", (msg: ConsoleMessage) => {
      if (msg.type() === "error") {
        const text = msg.text();
        if (!text.startsWith("preload error:")) consoleErrors.push(text);
      }
    });

    page.on("requestfailed", (req: Request) => {
      try {
        const reqUrl = req.url();
        if (!isNoise(reqUrl)) networkErrors.push(`${req.failure()?.errorText}: ${reqUrl}`);
      } catch {
        // Request objects can be in an invalid state when a context is closing;
        // swallow to prevent Playwright's internal ".method" access from crashing the page
      }
    });

    const response = await page.goto(url, {
      waitUntil: "domcontentloaded",
      timeout: 60_000, // 30s caused production timeouts crawling 520 pages with 2 concurrent connections
    });

    // Wait for network to settle; cap at 5s because Shinylive iframes may never go idle
    try {
      await page.waitForLoadState("networkidle", { timeout: 5_000 });
    } catch {
      // expected on pages with persistent WebSocket / Shinylive connections
    }

    const httpStatus = response?.status() ?? null;

    return {
      httpStatus,
      consoleErrors,
      networkErrors,
      close: () => context!.close(),
      screenshot: (options) => page.screenshot({ fullPage: options?.fullPage ?? false }),
    };
  } catch (err) {
    await context?.close();
    return { error: err instanceof Error ? err.message : String(err) };
  }
}
