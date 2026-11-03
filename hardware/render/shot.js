const { chromium } = require('playwright');
(async () => {
  const [, , out, query, w = 1600, h = 900, dpr = 1] = process.argv;
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: +dpr });
  p.on('console', m => console.log('page:', m.text())); p.on('pageerror', e => console.log('ERR', e.message));
  await p.goto(`http://localhost:8765/render/index.html?w=${w}&h=${h}&dpr=1&${query || ''}`);
  await p.waitForFunction('window.DONE === true', null, { timeout: 180000 });
  await (await p.$('canvas')).screenshot({ path: out });
  await b.close();
})();
