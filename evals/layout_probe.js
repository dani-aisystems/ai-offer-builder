// In-page layout probe for generated offer decks.
// Evaluate this file in the page, navigate to a slide, wait for fonts and the entry animation,
// then call window.__probeSlide({ desktop: true|false }). It measures only the slide that is
// currently displayed: hidden (display:none) slides measure 0x0, so the caller visits each one.
window.__probeSlide = function (opts) {
  const vw = window.innerWidth, vh = window.innerHeight;
  const slides = Array.from(document.querySelectorAll('.slide'));
  const active = slides.find(s => getComputedStyle(s).display !== 'none' && s.getClientRects().length > 0);
  const out = { index: slides.indexOf(active), total: slides.length, issues: [], contrast: [], minFont: null };
  if (!active) { out.issues.push('no visible .slide'); return out; }

  const snippet = el => el.textContent.trim().replace(/\s+/g, ' ').slice(0, 40);
  const visible = el => {
    const cs = getComputedStyle(el);
    return cs.display !== 'none' && cs.visibility !== 'hidden' && parseFloat(cs.opacity) > 0.05 && el.getClientRects().length > 0;
  };
  const hasOwnText = el => Array.from(el.childNodes).some(n => n.nodeType === 3 && n.textContent.trim());
  const inScroller = el => {
    for (let p = el.parentElement; p && p !== document.body; p = p.parentElement) {
      const o = getComputedStyle(p).overflowX;
      if (o === 'auto' || o === 'scroll') return true;
    }
    return false;
  };

  // 1. Does the slide fit? Desktop must not scroll; phones may scroll inside the slide but never clip.
  const sh = active.scrollHeight, ch = active.clientHeight, oy = getComputedStyle(active).overflowY;
  out.slideScroll = { scrollHeight: sh, clientHeight: ch, overflowY: oy };
  if (sh > ch + 2) {
    if (opts.desktop) out.issues.push(`needs scrolling on desktop: content ${sh}px in a ${ch}px slide`);
    else if (!['auto', 'scroll'].includes(oy)) out.issues.push(`content clipped: ${sh}px in a ${ch}px slide (overflow-y:${oy})`);
  }
  for (const el of active.querySelectorAll('*')) {
    if (!visible(el) || !el.textContent.trim()) continue;
    const cs = getComputedStyle(el);
    if (cs.overflowY === 'hidden' && el.clientHeight > 0 && el.scrollHeight > el.clientHeight + 2)
      out.issues.push(`clipped inside <${el.tagName.toLowerCase()}.${String(el.className).split(' ')[0]}>: ${el.scrollHeight}px in ${el.clientHeight}px`);
    if (cs.overflowX === 'hidden' && el.clientWidth > 0 && el.scrollWidth > el.clientWidth + 2)
      out.issues.push(`clipped horizontally inside <${el.tagName.toLowerCase()}.${String(el.className).split(' ')[0]}>`);
  }

  // 2. Page-level horizontal overflow.
  const docW = document.documentElement.scrollWidth;
  if (docW > vw + 1) out.issues.push(`page scrolls horizontally: ${docW}px in a ${vw}px viewport`);

  // 3. Text boxes: off-screen, overlapping each other or the navigation, too small.
  const textEls = Array.from(active.querySelectorAll('*')).filter(el => visible(el) && hasOwnText(el));
  const lines = [];
  for (const el of textEls) {
    const range = document.createRange();
    for (const n of el.childNodes) {
      if (n.nodeType !== 3 || !n.textContent.trim()) continue;
      range.selectNodeContents(n);
      for (const r of range.getClientRects()) if (r.width > 1 && r.height > 1) lines.push({ el, r });
    }
    const rect = el.getBoundingClientRect();
    if ((rect.right > vw + 1 || rect.left < -1) && !inScroller(el)) out.issues.push(`text off-screen horizontally: "${snippet(el)}"`);
    const fs = parseFloat(getComputedStyle(el).fontSize);
    if (out.minFont === null || fs < out.minFont.size) out.minFont = { size: fs, text: snippet(el) };
  }
  const clip = r => ({ l: Math.max(r.left, 0), r: Math.min(r.right, vw), t: Math.max(r.top, 0), b: Math.min(r.bottom, vh) });
  const seen = new Set();
  for (let i = 0; i < lines.length; i++) {
    for (let j = i + 1; j < lines.length; j++) {
      const a = lines[i], b = lines[j];
      if (a.el === b.el || a.el.contains(b.el) || b.el.contains(a.el)) continue;
      const A = clip(a.r), B = clip(b.r);
      const w = Math.min(A.r, B.r) - Math.max(A.l, B.l), h = Math.min(A.b, B.b) - Math.max(A.t, B.t);
      if (w > 2 && h > 2 && w * h > 0.15 * Math.min(a.r.width * a.r.height, b.r.width * b.r.height)) {
        const key = snippet(a.el) + '|' + snippet(b.el);
        if (!seen.has(key)) { seen.add(key); out.issues.push(`text overlap: "${snippet(a.el)}" / "${snippet(b.el)}"`); }
      }
    }
  }
  const navEls = Array.from(document.querySelectorAll('button, nav, [class*="counter"], [id*="counter"], [class*="nav"], [id*="nav"]'))
    .filter(el => !active.contains(el) && !el.contains(active) && visible(el));
  for (const nav of navEls) {
    const n = nav.getBoundingClientRect();
    for (const { el, r } of lines) {
      const w = Math.min(n.right, r.right) - Math.max(n.left, r.left), h = Math.min(n.bottom, r.bottom) - Math.max(n.top, r.top);
      if (w > 2 && h > 2 && r.top < vh && r.bottom > 0) { out.issues.push(`slide text under navigation: "${snippet(el)}"`); break; }
    }
  }
  if (!opts.desktop && out.minFont && out.minFont.size < 12) out.issues.push(`text below 12px on phone: ${out.minFont.size}px "${out.minFont.text}"`);

  // 4. Contrast of every rendered text element against its effective background.
  const parse = c => {
    const m = c && c.match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const p = m[1].split(/[,\s/]+/).filter(Boolean).map(Number);
    return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 };
  };
  const lum = ({ r, g, b }) => {
    const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
  };
  const blend = (fg, bg) => ({ r: fg.r * fg.a + bg.r * (1 - fg.a), g: fg.g * fg.a + bg.g * (1 - fg.a), b: fg.b * fg.a + bg.b * (1 - fg.a), a: 1 });
  const bgOf = el => {
    const layers = [];
    for (let p = el; p; p = p.parentElement) {
      const cs = getComputedStyle(p);
      if (cs.backgroundImage && cs.backgroundImage !== 'none') return { image: true };
      const c = parse(cs.backgroundColor);
      if (c && c.a > 0) { layers.push(c); if (c.a >= 1) break; }
    }
    let bg = { r: 255, g: 255, b: 255, a: 1 };
    for (let i = layers.length - 1; i >= 0; i--) bg = blend(layers[i], bg);
    return bg;
  };
  for (const el of textEls) {
    const cs = getComputedStyle(el);
    const fg = parse(cs.color), bg = bgOf(el);
    if (!fg) continue;
    if (bg.image) { out.contrast.push({ text: snippet(el), ratio: null, note: 'background image or gradient: check visually' }); continue; }
    const f = blend(fg, bg), L1 = lum(f), L2 = lum(bg);
    const ratio = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
    const size = parseFloat(cs.fontSize), weight = parseInt(cs.fontWeight, 10) || 400;
    const need = size >= 24 || (size >= 18.66 && weight >= 700) ? 3 : 4.5;
    if (ratio < need) out.contrast.push({ text: snippet(el), ratio: Math.round(ratio * 100) / 100, need, color: cs.color,
      background: `rgb(${Math.round(bg.r)}, ${Math.round(bg.g)}, ${Math.round(bg.b)})`, fontSize: size });
  }
  out.fontsUsed = Array.from(new Set(textEls.map(el => getComputedStyle(el).fontFamily.split(',')[0].replace(/["']/g, '').trim())));
  out.issues = Array.from(new Set(out.issues));
  return out;
};
