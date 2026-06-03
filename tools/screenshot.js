// Screenshot helper, for visual QA of a built guide.
//   node tools/screenshot.js <html> <outprefix> [theme] [y1,y2,...]
// y values are pixel offsets or "#section-id" anchors. Set CHROME_PATH to point
// at your browser (defaults to macOS Google Chrome).
const puppeteer = require("puppeteer");
const CHROME =
  process.env.CHROME_PATH ||
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
(async () => {
  const [, , file, prefix, theme = "light", ys = ""] = process.argv;
  const browser = await puppeteer.launch({
    executablePath: CHROME,
    args: ["--no-sandbox"],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1480, height: 960, deviceScaleFactor: 1.5 });
  await page.goto("file://" + file, { waitUntil: "networkidle0" });
  await page.evaluate(() => {
    document.documentElement.style.scrollBehavior = "auto";
  });
  if (theme === "dark") {
    await page.evaluate(() => {
      document.documentElement.className = "theme-dark";
    });
  }
  const positions = ys ? ys.split(",") : ["0"];
  let i = 0;
  for (const y of positions) {
    await page.evaluate((yy) => {
      if (String(yy).startsWith("#")) {
        const el = document.querySelector(yy);
        if (el) el.scrollIntoView();
      } else window.scrollTo(0, Number(yy));
    }, y);
    await new Promise((r) => setTimeout(r, 350));
    await page.screenshot({ path: `${prefix}-${i}.png` });
    i++;
  }
  await browser.close();
  console.log("shot", positions.length, "frames →", prefix);
})();
