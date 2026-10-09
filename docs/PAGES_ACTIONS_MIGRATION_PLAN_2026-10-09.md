# TAX AI Web — GitHub Pages Actions Migration Plan

Date: 2026-10-09
Status: **AUTHORIZED — MIGRATE FROM BRANCH SOURCE TO GITHUB ACTIONS**

## Goal

Replace GitHub Pages `Deploy from a branch` with a repo-owned GitHub Actions deployment, following the proven pattern in `taipei-tax-lab/tpctax-1999-ai-web/.github/workflows/pages.yml`.

Desired path:

`approved main change → Actions → tests/package verification → Pages artifact → deploy-pages`

Pages URL remains `https://taipei-tax-lab.github.io/tax-helper/`.

## Required workflow

Create `.github/workflows/pages.yml` with:
- relevant `main` push trigger plus `workflow_dispatch`;
- `actions/checkout@v4`;
- fail-closed Pages source guard requiring `build_type=workflow`;
- `actions/configure-pages@v5`;
- lightweight deterministic tests;
- deterministic package build using `tools/package_web.py`;
- build twice and require byte-identical ZIPs;
- extract only verified runtime package;
- `actions/upload-pages-artifact@v3`;
- deploy job with `pages: write` and `id-token: write`;
- `actions/deploy-pages@v5`;
- `github-pages` environment;
- `concurrency: group: pages`, no overlapping unsafe deploys.

## Runtime artifact rule

Do **not** publish repository root. Continue using the existing `tools/package_web.py` runtime allowlist (14 runtime files) plus generated `MANIFEST.json`. Do not expose tests/docs/tools/STATE/TASK/generated CSV/user files as Pages content.

Generated ZIP may remain uncommitted; the Actions artifact is the release artifact.

## Trigger policy

Auto-deploy when relevant runtime/release files on `main` change: runtime HTML/JS/CSS/data files, `assets/tax-ai/**`, `tools/package_web.py`, relevant tests, or the workflow itself. Documentation-only commits do not need to redeploy.

Keep `workflow_dispatch` for intentional manual redeploys.

## Pages setting

Repository owner must set:

`Settings → Pages → Build and deployment → Source → GitHub Actions`

The workflow must fail clearly if Source is still `Deploy from a branch`. Do not use undocumented admin/API workarounds if current GitHub credentials cannot change Pages settings.

## First migration release

After workflow is committed:
1. switch Pages Source to GitHub Actions;
2. dispatch or make a relevant main push;
3. capture run ID/source SHA/deployed SHA/artifact;
4. require build and deploy PASS;
5. verify hosted runtime bytes match the deployed package/manifest;
6. verify repo-internal exclusions are not published;
7. then perform normal trusted-browser TAX AI smoke.

Ignore the currently queued old dynamic branch-source run as evidence for the new deployment model.

## Scope / rollback

This task changes deployment automation only. Do not modify CX, Agent, Flow, Data Store, Messenger binding, FAQ content, search logic, or UI.

Deployment automation rollback: revert workflow and only switch Pages Source back to branch mode if explicitly approved. Product rollback remains `liveEnabled=false` while Quick Search stays available.

## Completion states

- `ACTIONS WORKFLOW READY / PAGES SOURCE SWITCH PENDING`
- `TAX AI PAGES ACTIONS DEPLOYMENT ACTIVE`
- after trusted-browser CX acceptance: `TAX AI WEB + FAQ FLOW LIVE / USABLE`

## Maintenance rule

After migration, normal releases are automatic from approved relevant `main` changes. Do not manually rerun old dynamic branch-source Pages builds. Use `workflow_dispatch` only for intentional redeploy/recovery.

## Implementation progress（2026-10-09）

repo-owned pages.yml與verify_package.py已依本計畫實作；offline Python27／Node34／syntax10 PASS，兩ZIP相同、fresh15檔、runtime14不改。
詳見PAGES_ACTIONS_TEST_EVIDENCE_2026-10-09.json及PAGES_DEPLOYMENT_2026-10-09.md；實際Source與first deployment仍須新run證據。
未變更管理設定／CX／產品，不再重跑舊dynamicjob。
