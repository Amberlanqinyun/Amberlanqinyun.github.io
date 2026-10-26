/* Renders the CV source pages to the PDFs the About page links to.
   Serve the site first (python3 -m http.server 8791 --directory .), then:
     node scripts/cv_pdf.js [base-url]
   Playwright is resolved from PLAYWRIGHT_PATH, else the social-studio install. */
const path = require('path');
const { execFileSync } = require('child_process');
const pw = require(process.env.PLAYWRIGHT_PATH || path.join(process.env.HOME, '.claude/skills/social-studio/scripts/node_modules/playwright'));

const base = process.argv[2] || 'http://localhost:8791';
const jobs = [['/src/cv/cv-en.html', 'assets/amber-lan-cv.pdf']];

(async () => {
  const browser = await pw.chromium.launch();
  const page = await browser.newPage();
  for (const [src, out] of jobs) {
    await page.goto(base + src, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    await page.pdf({ path: path.join(__dirname, '..', out), format: 'A4', printBackground: true, preferCSSPageSize: true });
    execFileSync('python3', [path.join(__dirname, 'cv_meta.py'), path.join(__dirname, '..', out)]);
    console.log('wrote', out);
  }
  await browser.close();
})();
