import { existsSync, mkdirSync } from "node:fs";
import { homedir } from "node:os";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";

const target =
  process.env.OPB_MATRIX_QA_URL ||
  "http://localhost:3000/auth/dev-login?role=operator&next=/operator/matrix";
const outputDir = resolve(process.cwd(), "../tmp/qa");
const playwrightPackage =
  process.env.OPB_PLAYWRIGHT_PACKAGE ||
  [
    resolve(process.cwd(), "node_modules/playwright/index.mjs"),
    resolve(homedir(), ".npm/_npx/e41f203b7505f1fb/node_modules/playwright/index.mjs"),
    resolve(
      homedir(),
      ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/.pnpm/playwright@1.59.1/node_modules/playwright/index.mjs",
    ),
  ].find((candidate) => existsSync(candidate));

if (!playwrightPackage) {
  throw new Error(
    "Playwright package was not found. Install it once with `npx playwright install chromium`, or set OPB_PLAYWRIGHT_PACKAGE=/path/to/playwright/index.mjs.",
  );
}

function assertLayout(condition, message) {
  if (!condition) {
    throw new Error(`[matrix-render-qa] ${message}`);
  }
}

function gridColumnCount(serializedColumns) {
  if (!serializedColumns || serializedColumns === "none") {
    return 0;
  }
  return serializedColumns.trim().split(/\s+/).length;
}

const { chromium } = await import(pathToFileURL(playwrightPackage).href);
mkdirSync(outputDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
const desktop = await browser.newPage({ viewport: { width: 1240, height: 800 } });
await desktop.goto(target, { waitUntil: "networkidle" });
await desktop.screenshot({ path: resolve(outputDir, "matrix-render-desktop.png") });
await desktop.screenshot({ path: resolve(outputDir, "matrix-render-desktop-full.png"), fullPage: true });

const checks = await desktop.evaluate(() => {
  const styleFor = (selector) => {
    const node = document.querySelector(selector);
    if (!node) {
      return null;
    }
    const computed = window.getComputedStyle(node);
    return {
      display: computed.display,
      gridTemplateColumns: computed.gridTemplateColumns,
      textLength: node.textContent?.trim().length || 0,
    };
  };
  const visiblePanels = [...document.querySelectorAll(".aof-detail-panel")].filter(
    (node) => node.getClientRects().length > 0,
  ).length;
  const firstAofDetails = document.querySelector(".aof-detail-disclosure");

  return {
    pageTitle: document.querySelector("h1")?.textContent || "",
    bodyText: document.body.textContent || "",
    sizingCountLabels: [...document.querySelectorAll(".preflop-sizing-row small")].map(
      (node) => node.textContent?.trim() || "",
    ),
    countLabels: [
      ...document.querySelectorAll(
        ".preflop-aof-row > span:nth-of-type(1), .aof-loss-metrics b:first-child, .matrix-metric-line b:first-child, .position-situation-row:not(.position-situation-head) > span:nth-of-type(1), .fold-exposure-row > span",
      ),
    ].map((node) => node.textContent?.trim() || ""),
    pinnedPills: [...document.querySelectorAll(".pinned-detail-card .pill")].map(
      (node) => node.textContent?.trim() || "",
    ),
    sizingRow: styleFor(".preflop-sizing-row"),
    aofGrid: styleFor(".preflop-aof-grid"),
    aofRow: styleFor(".preflop-aof-row"),
    aofDetailsOpen: firstAofDetails ? firstAofDetails.hasAttribute("open") : null,
    visibleAofDetailPanels: visiblePanels,
    positiveMetrics: document.querySelectorAll(".metric-positive").length,
    negativeMetrics: document.querySelectorAll(".metric-negative").length,
    lossMetricRows: document.querySelectorAll(".aof-loss-metrics").length,
    correctionList: styleFor(".matrix-correction-list"),
    runoutTrend: styleFor(".matrix-noise-tabs"),
    matrixGrid: styleFor(".baseline-matrix-grid"),
    pinnedDetail: styleFor(".matrix-pinned-grid"),
  };
});

assertLayout(checks.pageTitle.includes("Preflop"), "operator Matrix page did not load the expected surface");
assertLayout(checks.sizingRow?.display === "grid", "sizing rows are not rendered as grid rows");
assertLayout(
  gridColumnCount(checks.sizingRow?.gridTemplateColumns) >= 6,
  "sizing rows collapsed instead of keeping table-like columns",
);
assertLayout(!checks.bodyText.includes("n/a 0x"), "empty sizing spots are rendering noisy `n/a 0x` text");
assertLayout(!checks.bodyText.includes("1x jam"), "single jam count is rendering as `1x jam` prose");
assertLayout(!/(^|[\s(])\d+x,/.test(checks.bodyText), "count prose is rendering as `countx,` instead of a noun label");
assertLayout(
  !checks.sizingCountLabels.some((label) => /^\d+x$/.test(label)),
  "sizing table count labels are using `x`, which conflicts with size multipliers",
);
assertLayout(
  !checks.countLabels.some((label) => /^\d+x$/.test(label)),
  "Matrix count labels are using `x`; counts should use nouns like spots, jams, folds, or opens",
);
assertLayout(
  !checks.pinnedPills.some((label) => /·\s*\d+x$/.test(label)),
  "Pinned detail pills are using count-as-x labels",
);
assertLayout(checks.aofGrid?.display === "grid", "AOF section is not rendered as a grid");
assertLayout(checks.aofRow?.display === "grid", "AOF rows are not rendered as grid rows");
assertLayout(
  gridColumnCount(checks.aofRow?.gridTemplateColumns) >= 5,
  "AOF rows collapsed and are no longer table-like",
);
assertLayout(checks.aofDetailsOpen === false, "AOF detail disclosure starts open");
assertLayout(checks.visibleAofDetailPanels === 0, "AOF hover/detail text is visible before interaction");
assertLayout(checks.positiveMetrics > 0, "positive result metrics are not color-coded");
assertLayout(checks.negativeMetrics > 0, "negative result metrics are not color-coded");
assertLayout(checks.lossMetricRows > 0, "AOF big-loss cluster metrics are not split into readable metric chips");
assertLayout(checks.correctionList?.display === "grid", "correction candidates are not rendered as cards/grid");
assertLayout(checks.runoutTrend?.display === "flex", "runout trend tabs are not rendered as tabs");
assertLayout(checks.matrixGrid?.display === "grid", "13x13 matrix is not rendered as a grid");
assertLayout(checks.pinnedDetail?.display === "grid", "pinned detail layout is not rendered as a grid");

const mobile = await browser.newPage({ viewport: { width: 624, height: 1400 } });
await mobile.goto(target, { waitUntil: "networkidle" });
await mobile.screenshot({ path: resolve(outputDir, "matrix-render-mobile-full.png"), fullPage: true });

const mobileChecks = await mobile.evaluate(() => {
  const metricCards = [...document.querySelectorAll(".result-hero > div")].map((node) => {
    const rect = node.getBoundingClientRect();
    return { width: rect.width, scrollWidth: node.scrollWidth };
  });
  const bodyWidth = document.documentElement.clientWidth;
  const overflows = [...document.querySelectorAll(".page-card, .matrix-analysis-card, .preflop-aof-card")].filter(
    (node) => node.getBoundingClientRect().right > bodyWidth + 1,
  ).length;
  return {
    overflows,
    metricOverflow: metricCards.filter((card) => card.scrollWidth > card.width + 1).length,
  };
});

assertLayout(mobileChecks.overflows === 0, "mobile viewport has cards overflowing the page boundary");
assertLayout(mobileChecks.metricOverflow === 0, "mobile metric cards have horizontal text overflow");

await browser.close();

console.log(`[matrix-render-qa] desktop: ${resolve(outputDir, "matrix-render-desktop.png")}`);
console.log(`[matrix-render-qa] desktop-full: ${resolve(outputDir, "matrix-render-desktop-full.png")}`);
console.log(`[matrix-render-qa] mobile-full: ${resolve(outputDir, "matrix-render-mobile-full.png")}`);
console.log("[matrix-render-qa] structural layout assertions passed");
