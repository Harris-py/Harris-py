// node render.mjs stills 3,6,12 dir/ | node render.mjs events events.json | node render.mjs video out.mkv [fps]
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const here = path.dirname(fileURLToPath(import.meta.url));
const [mode, a, b] = process.argv.slice(2);
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1120, height: 720 } });
await page.goto('file://' + path.join(here, 'film.html'));
await page.evaluate(() => document.fonts.load('14px "JetBrains Mono"'));
const shot = async (t) => { await page.evaluate((t) => window.__seek(t), t); return page.screenshot({ type: 'png' }); };
if (mode === 'events') writeFileSync(a, JSON.stringify(await page.evaluate(() => [window.__events(), window.__duration])));
else if (mode === 'stills') { mkdirSync(b, { recursive: true }); for (const t of a.split(',').map(Number)) writeFileSync(path.join(b, `t${t}.png`), await shot(t)); }
else {
  const fps = Number(b || 20), dur = await page.evaluate(() => window.__duration);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-', '-c:v', 'ffv1', a], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < Math.round(dur * fps); i++) { const buf = await shot(i / fps); if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r)); }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
}
await browser.close();
