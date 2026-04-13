# Design: Monthly Site Audit CI Workflow

**Date:** 2026-04-13
**Scope:** `.github/workflows/audit-site.yml`

## Problem

The `audit-site` script runs manually today. There's no automated check that catches regressions on production between explicit runs, and running it requires a local environment with Playwright and AWS credentials configured.

## Goal

A monthly GitHub Actions workflow that audits the production site, opens a GitHub issue when issues are found, and closes the previous audit issue so there's never more than one open at a time.

## Out of Scope

- `compare-versions` CI job — runs locally only
- Audit of non-production environments
- Slack or email notifications

## Workflow File

**Path:** `.github/workflows/audit-site.yml`

**Triggers:**
- `schedule`: cron `0 6 1 * *` (1st of each month, 6am UTC)
- `workflow_dispatch`: manual trigger for on-demand runs (e.g., post-deploy, after dependency updates)

**Job:** `audit` on `ubuntu-latest`

**Permissions:**
```yaml
permissions:
  contents: read
  issues: write
```

## Steps

1. `actions/checkout@v3`
2. `actions/setup-node@v4` with Node 20
3. `npm ci` in `tests/`
4. `npx playwright install chromium --with-deps` (installs Playwright + system deps for Ubuntu)
5. Run audit with `continue-on-error: true`:
   ```bash
   npm run audit -- --url https://shiny.posit.co/py
   ```
   Exit code 0 = clean, exit code 1 = issues found.
6. Upload `tests/audit-site-*.md` as a workflow artifact (runs regardless of audit outcome)
7. If audit outcome was `failure`:
   a. Find all open issues labeled `site-audit` and close each with comment "Superseded by newer audit."
   b. Open a new issue with the full report as the body

## Issue Format

- **Label:** `site-audit` (must be created in the repo once before the workflow runs)
- **Title:** `Monthly site audit — YYYY-MM-DD`
- **Body:** Full content of the generated `audit-site-*.md` report
- **On clean run:** No issue opened; any previously open `site-audit` issue is left open (still valid)

## AWS Credentials Setup

The audit script uses `@anthropic-ai/bedrock-sdk`. Add two repository secrets (Settings → Secrets and variables → Actions):

| Secret | Value |
|---|---|
| `AWS_ACCESS_KEY_ID` | IAM user access key ID |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret access key |

The IAM user needs this policy:
```json
{
  "Effect": "Allow",
  "Action": "bedrock:InvokeModel",
  "Resource": "arn:aws:bedrock:us-east-1::foundation-model/us.anthropic.claude-sonnet-4-6"
}
```

Region is hardcoded to `us-east-1` in `tests/audit-site.ts`; no secret needed for it.

The workflow exposes them as:
```yaml
env:
  AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
  AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
  AWS_REGION: us-east-1
```
