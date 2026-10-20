import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1080 } });
await p.goto('file://' + process.argv[2]); await p.screenshot({ path: process.argv[3] }); await b.close();
