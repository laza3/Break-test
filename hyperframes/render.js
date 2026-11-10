/**
 * Deterministic frame renderer for the HyperFrames composition.
 *   node render.js --gsap <path/to/gsap.min.js> --out out.mp4 [--fps 30]
 *   node render.js --gsap <path> --snaps 0.9,3.2,5.2,7.6,10.8,12.6,14.4 --snapdir /tmp/snaps
 * Seeks window.__timelines.main frame by frame and pipes PNGs into ffmpeg.
 */
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

function arg(name, def) {
  const i = process.argv.indexOf('--' + name);
  return i > -1 ? process.argv[i + 1] : def;
}

const W = 1920, H = 1080;
const FPS = parseInt(arg('fps', '30'), 10);
const DUR = parseFloat(arg('dur', '15'));
const GSAP = arg('gsap');
const OUT = arg('out');
const SNAPS = arg('snaps');
const SNAPDIR = arg('snapdir', '/tmp/snaps');
const HTML = path.join(__dirname, 'index.html');

(async () => {
  const browser = await chromium.launch({
    args: ['--no-sandbox', '--disable-lcd-text', '--hide-scrollbars',
           '--force-color-profile=srgb', '--disable-gpu-vsync', '--font-render-hinting=none'],
  });
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });

  // The composition declares CDN scripts (import contract). Serve them locally for an offline render.
  if (!GSAP || !fs.existsSync(GSAP)) throw new Error('missing --gsap path: ' + GSAP);
  const GSAP_SRC = fs.readFileSync(GSAP, 'utf8');
  await page.route('**/gsap@3.14.2/**', route => {
    return route.fulfill({ status: 200, contentType: 'application/javascript', body: GSAP_SRC });
  });
  await page.route('**/@hyperframes/**', route =>
    route.fulfill({ status: 200, contentType: 'application/javascript', body: '/* runtime stub: this renderer drives the timeline */' }));

  const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });

  await page.goto('file://' + HTML, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready.then(() => true));
  try {
    await page.waitForFunction(() => !!(window.__timelines && window.__timelines.main), { timeout: 30000 });
  } catch (e) {
    console.error('timeline never registered. page errors:\n' + errors.join('\n'));
    throw e;
  }
  if (errors.length) console.error('page errors:\n' + errors.join('\n'));
  await page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));

  const seek = t => page.evaluate(v => { window.__timelines.main.time(v, false); }, t);

  if (SNAPS) {
    fs.mkdirSync(SNAPDIR, { recursive: true });
    for (const s of SNAPS.split(',')) {
      const t = parseFloat(s);
      await seek(t);
      const f = path.join(SNAPDIR, 't' + t.toFixed(2).replace('.', '_') + '.png');
      await page.screenshot({ path: f });
      console.log('snap', t, '->', f);
    }
    await browser.close();
    return;
  }

  const total = Math.round(DUR * FPS);
  const ff = spawn('ffmpeg', ['-y', '-hide_banner', '-loglevel', 'error',
    '-f', 'image2pipe', '-vcodec', 'png', '-framerate', String(FPS), '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p',
    '-r', String(FPS), '-movflags', '+faststart', OUT]);
  ff.stderr.on('data', d => process.stderr.write(d));
  const done = new Promise((res, rej) => ff.on('close', c => (c === 0 ? res() : rej(new Error('ffmpeg ' + c)))));

  for (let i = 0; i < total; i++) {
    await seek(i / FPS);
    const buf = await page.screenshot({ type: 'png' });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 50 === 0) console.log('frame', i, '/', total);
  }
  ff.stdin.end();
  await done;
  await browser.close();
  console.log('done ->', OUT);
})().catch(e => { console.error(e); process.exit(1); });
