"""Rebuild the four flat section slides as animatable layers.

    python scripts/build-section-layers.py

Inputs (all under design/canva-export/):
  2.webp … 5.webp            the flat slides exported from Canva
  objects-png/<folder>/      each slide's elements, exported as PNGs
  placements/<folder>.json   where each element sits (scripts/locate-elements.py)

Outputs (under src/assets/sections/):
  <slug>/base.webp           what lies under the elements: the airmail-letter
                             paper with no text or pictures, rebuilt from the four
                             slides (they share one template). Shows behind an
                             element until it has appeared.
  <slug>/top.webp            the slide itself, transparent wherever an element
                             shows through; keeps the text, borders and anything
                             drawn over an element, so the original stacking holds
  <slug>/el-NN.webp          each element exactly as placed (scale, rotation, flip)
  <slug>/layers.json         each element's box as fractions of the slide, in paint
                             order, with a reveal order (top to bottom)

Stacked base → elements → top, each page matches its slide: the script
re-composites the encoded files and prints the error to prove it.
"""
import itertools
import json
import os
import unicodedata

import cv2
import numpy as np
from PIL import Image

SRC = 'design/canva-export'
OUT = 'src/assets/sections'
SECTIONS = [  # slug, flat slide, element folder
    ('loi-ngo', '2.webp', 'loi_ngo'),
    ('vung-ky-uc', '3.webp', 'vung_ky_uc'),
    ('cung-nhau-lon', '4.webp', 'cung_nhau_lon'),
    ('loi-tri-an', '5.webp', 'loi_tri_an'),
]
OUT_SCALE = 0.75  # 3179×4494 slide → 2384×3371: sharp at the popup's 3× zoom
PAPER_SCALE = 0.5  # base.webp: soft paper, half size is plenty
BORDER = 150  # px (at OUT_SCALE) of airmail stripes along each edge
MISMATCH_LO, MISMATCH_HI = 14, 30  # per-channel levels: ramp from "same" to "different"
QUALITY = 84


def nfc(s):
    return unicodedata.normalize('NFC', s)


def element_path(folder, name):
    return os.path.join(folder, next(n for n in os.listdir(folder) if nfc(n) == name))


def over(top_rgb, top_a, under):
    return top_rgb * top_a[..., None] + under * (1 - top_a[..., None])


GRID = 4  # OUT_SCALE = 3/4: every 4 slide pixels map onto exactly 3 output pixels


def place(E, M, full_size, out_size):
    """Draw element E (RGBA float) where M puts it on the full-size slide, then
    shrink it exactly as the slide itself was shrunk (Lanczos on the same pixel
    grid), so an exact-copy element reproduces the slide pixel for pixel.

    Returns (x0, y0, crop) in output pixels.
    """
    M = np.float64(M)
    s = float(np.hypot(M[0, 0], M[1, 0]))
    if s < 1:  # shrink with area averaging first; warpAffine would alias
        E = cv2.resize(E, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
        M = np.hstack([M[:, :2] / s, M[:, 2:]])
    eh, ew = E.shape[:2]
    corners = cv2.transform(np.float32([[[0, 0], [ew, 0], [ew, eh], [0, eh]]]), np.float32(M))[0]
    W, H = full_size
    x0, y0 = (np.floor(corners.min(0) / GRID) * GRID).astype(int).clip(0, [W, H])
    x1, y1 = (np.ceil(corners.max(0) / GRID) * GRID).astype(int).clip(0, [W, H])
    A = M.copy()
    A[:, 2] -= [x0, y0]
    full = cv2.warpAffine(E, np.float32(A), (int(x1 - x0), int(y1 - y0)), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    ox, oy = round(x0 * OUT_SCALE), round(y0 * OUT_SCALE)
    ow = min(round((x1 - x0) * OUT_SCALE), out_size[0] - ox)
    oh = min(round((y1 - y0) * OUT_SCALE), out_size[1] - oy)
    small = Image.fromarray(full.round().clip(0, 255).astype(np.uint8), 'RGBA').convert('RGBa')
    crop = np.asarray(small.resize((ow, oh), Image.LANCZOS).convert('RGBA')).astype(np.float32)
    ys, xs = np.nonzero(crop[..., 3] > 2)  # trim to what is actually drawn
    return int(ox + xs.min()), int(oy + ys.min()), crop[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def region(L):
    x0, y0, c = L
    return np.s_[y0:y0 + c.shape[0], x0:x0 + c.shape[1]]


def clean_paper(slides):
    """The letter background shared by all slides, with text and pictures removed.

    Along the striped border, a pixel is taken where two slides agree (and the
    colour is paper or a stripe). Inside, any slide showing plain paper there
    donates it (the one closest to the paper colour). Pixels no slide shows
    clean are filled in from their surroundings.
    """
    n, h, w, _ = slides.shape
    light = slides[slides.mean(axis=3) > 200]
    paper = np.median(light, axis=0)
    yy, xx = np.mgrid[0:h, 0:w]
    edge = np.minimum(np.minimum(xx, w - 1 - xx), np.minimum(yy, h - 1 - yy)) < BORDER

    # Stripe colours: the two dominant non-paper colours of the top border.
    strip = slides[:, :BORDER // 2].reshape(-1, 3)
    strip = strip[np.abs(strip - paper).max(axis=1) > 60]
    _, _, centers = cv2.kmeans(np.float32(strip), 2, None, (cv2.TERM_CRITERIA_EPS, 20, 1.0), 3, cv2.KMEANS_PP_CENTERS)
    allowed = np.vstack([paper, centers])

    out = np.zeros((h, w, 3), np.float32)
    done = np.zeros((h, w), bool)
    best_lum = np.full((h, w), -1.0, np.float32)
    for i, j in itertools.combinations(range(n), 2):
        m = (slides[i] + slides[j]) / 2
        ok = (np.abs(slides[i] - slides[j]).max(axis=2) < 10) & edge
        ok &= np.min([np.abs(m - c).max(axis=2) for c in allowed], axis=0) < 45
        lum = m.mean(axis=2)
        take = ok & (lum > best_lum)
        out[take], best_lum[take], done[take] = m[take], lum[take], True

    dist = np.abs(slides - paper).max(axis=3)  # n × h × w
    pick = dist.argmin(axis=0)
    ok = (np.take_along_axis(dist, pick[None], 0)[0] < 28) & ~edge
    chosen = np.take_along_axis(slides, pick[None, ..., None].repeat(3, axis=3), 0)[0]
    out[ok], done[ok] = chosen[ok], True

    return cv2.inpaint(out.round().astype(np.uint8), (~done).astype(np.uint8) * 255, 5, cv2.INPAINT_TELEA).astype(np.float32)


def paint_order(O, layers, B):
    """Order elements so each one drawn over another in the slide paints later."""
    n = len(layers)
    above = {i: set() for i in range(n)}  # i -> elements that sit above i
    for i in range(n):
        for j in range(i + 1, n):
            (xi, yi, ci), (xj, yj, cj) = layers[i], layers[j]
            x0, y0 = max(xi, xj), max(yi, yj)
            x1 = min(xi + ci.shape[1], xj + cj.shape[1])
            y1 = min(yi + ci.shape[0], yj + cj.shape[0])
            if x1 <= x0 or y1 <= y0:
                continue
            pi = ci[y0 - yi:y1 - yi, x0 - xi:x1 - xi]
            pj = cj[y0 - yj:y1 - yj, x0 - xj:x1 - xj]
            ai, aj = pi[..., 3] / 255, pj[..., 3] / 255
            both = (ai > 0.5) & (aj > 0.5)
            if both.sum() < 200:
                continue
            o, b = O[y0:y1, x0:x1], B[y0:y1, x0:x1]
            err_i = np.abs(o - over(pi[..., :3], ai, over(pj[..., :3], aj, b)))[both].mean()
            err_j = np.abs(o - over(pj[..., :3], aj, over(pi[..., :3], ai, b)))[both].mean()
            if err_i < err_j:
                above[j].add(i)
            else:
                above[i].add(j)
    order, placed = [], set()
    while len(order) < n:
        ready = [i for i in range(n) if i not in placed and not any(
            i in above[j] for j in range(n) if j not in placed)]
        i = ready[0] if ready else min(set(range(n)) - placed)  # cycle: keep listing order
        order.append(i)
        placed.add(i)
    return order


def save(img, path, **kw):
    img.save(path, 'WEBP', quality=QUALITY, method=6, **kw)


def section_base(O, cover, paper):
    """What lies under this slide's elements: plain paper, except next to large
    non-paper areas (the video frame, pictures that were not exported), where
    the slide's own surroundings are filled in instead."""
    h, w = O.shape[:2]
    k = PAPER_SCALE / OUT_SCALE
    sw, sh = round(w * k), round(h * k)
    small = cv2.resize(O, (sw, sh), interpolation=cv2.INTER_AREA)
    foot = cv2.resize((cover > 0.01).astype(np.uint8), (sw, sh), interpolation=cv2.INTER_NEAREST)
    foot = cv2.dilate(foot, np.ones((7, 7), np.uint8))
    filled = cv2.inpaint(small.round().astype(np.uint8), foot * 255, 6, cv2.INPAINT_TELEA).astype(np.float32)
    paper_small = cv2.resize(paper, (sw, sh), interpolation=cv2.INTER_AREA)
    other = (np.abs(small - paper_small).max(axis=2) > 45).astype(np.uint8) & (1 - foot)
    other = cv2.morphologyEx(other, cv2.MORPH_OPEN, np.ones((15, 15), np.uint8))  # drop text strokes
    near = cv2.dilate(other, np.ones((91, 91), np.uint8)).astype(np.float32)
    # ...and only where the filled-in colour really differs from paper.
    differs = np.clip((np.abs(filled - paper_small).max(axis=2) - 30) / 30, 0, 1)
    near = cv2.GaussianBlur(near * differs, (0, 0), 3)
    base = paper_small * (1 - near[..., None]) + filled * near[..., None]
    return base.round().clip(0, 255).astype(np.uint8)


def build_section(slug, O, folder, spec, paper):
    h, w = O.shape[:2]
    out_dir = os.path.join(OUT, slug)
    os.makedirs(out_dir, exist_ok=True)
    for f in os.listdir(out_dir):
        os.remove(os.path.join(out_dir, f))

    cache, layers = {}, []
    for p in spec['placements']:
        if p['file'] not in cache:
            cache[p['file']] = np.asarray(Image.open(element_path(folder, p['file'])).convert('RGBA')).astype(np.float32)
        layers.append(place(cache[p['file']], p['M'], spec['size'], (w, h)))

    cover = np.zeros((h, w), np.float32)  # share of each pixel covered by some element
    for L in layers:
        r = region(L)
        cover[r] = 1 - (1 - cover[r]) * (1 - L[2][..., 3] / 255)

    base_file = os.path.join(out_dir, 'base.webp')
    save(Image.fromarray(section_base(O, cover, paper)), base_file)
    # Composite against the base as the browser will see it (decoded, upscaled).
    B = np.asarray(Image.open(base_file).convert('RGB').resize((w, h), Image.BILINEAR)).astype(np.float32)

    order = paint_order(O, layers, B)
    S = B.copy()
    for i in order:
        r, c = region(layers[i]), layers[i][2]
        S[r] = over(c[..., :3], c[..., 3] / 255, S[r])

    # Where the stack already reproduces the slide, the top layer turns clear.
    # Compare slightly blurred copies: sub-pixel resampling differences along
    # sharp edges vanish, while text (absent from the stack) still stands out.
    diff = np.abs(cv2.GaussianBlur(O, (0, 0), 1.5) - cv2.GaussianBlur(S, (0, 0), 1.5)).max(axis=2)
    mismatch = np.clip((diff - MISMATCH_LO) / (MISMATCH_HI - MISMATCH_LO), 0, 1)
    # Hairline differences (where two pictures' edges meet) are not content;
    # anything drawn on top, even the dot of a diacritic, is at least 3 px wide.
    solid = cv2.morphologyEx((mismatch > 0.5).astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    mismatch *= cv2.dilate(solid, np.ones((5, 5), np.uint8))
    mismatch = cv2.dilate(mismatch, np.ones((5, 5), np.uint8))  # keep text edges whole
    mismatch = cv2.GaussianBlur(mismatch, (0, 0), 1)
    # Clear the whole footprint, feathered edges included, so nothing of an
    # element lingers on the page before it appears.
    footprint = np.clip((cover - 0.01) / 0.05, 0, 1)
    top_alpha = 1 - footprint * (1 - mismatch)
    top = np.dstack([O, top_alpha * 255]).round().clip(0, 255).astype(np.uint8)
    save(Image.fromarray(top, 'RGBA'), os.path.join(out_dir, 'top.webp'), exact=False)

    elements = []
    for rank, i in enumerate(order):
        x0, y0, c = layers[i]
        a = c[..., 3] / 255
        seen = float(((1 - top_alpha[region(layers[i])]) * a).sum() / max(a.sum(), 1))
        name = f'el-{rank + 1:02d}.webp'
        save(Image.fromarray(c.round().clip(0, 255).astype(np.uint8), 'RGBA'), os.path.join(out_dir, name), exact=False)
        elements.append(dict(src=name, file=spec['placements'][i]['file'], px=(x0, y0),
                             x=x0 / w, y=y0 / h, w=c.shape[1] / w, h=c.shape[0] / h, seen=seen))

    # Reveal top to bottom, left to right; paint order is unchanged.
    for n, e in enumerate(sorted(elements, key=lambda e: (round(e['y'], 2), e['x']))):
        e['reveal'] = n
    meta = dict(width=spec['size'][0], height=spec['size'][1],
                elements=[dict(src=e['src'], x=round(e['x'], 5), y=round(e['y'], 5), w=round(e['w'], 5),
                               h=round(e['h'], 5), reveal=e['reveal']) for e in elements])
    with open(os.path.join(out_dir, 'layers.json'), 'w') as fh:
        json.dump(meta, fh, indent=1)

    # Proof: re-composite the encoded files and compare with the slide.
    R = B.copy()
    for e in elements:
        im = np.asarray(Image.open(os.path.join(out_dir, e['src'])).convert('RGBA')).astype(np.float32)
        x0, y0 = e['px']
        R[y0:y0 + im.shape[0], x0:x0 + im.shape[1]] = over(im[..., :3], im[..., 3] / 255, R[y0:y0 + im.shape[0], x0:x0 + im.shape[1]])
    T = np.asarray(Image.open(os.path.join(out_dir, 'top.webp')).convert('RGBA')).astype(np.float32)
    R = over(T[..., :3], T[..., 3] / 255, R)
    err = np.abs(R - O)
    kb = sum(os.path.getsize(os.path.join(out_dir, f)) for f in os.listdir(out_dir)) // 1024
    print(f'{slug}: {len(elements)} elements, mean error {err.mean():.2f}/255, '
          f'pixels off by >24: {(err.max(axis=2) > 24).mean() * 100:.2f}%, {kb} KB')
    for e in elements:
        print(f"  {e['src']}  visible {e['seen'] * 100:3.0f}%  {e['file']}")


def main():
    slides = []
    for _, flat, _ in SECTIONS:
        im = Image.open(os.path.join(SRC, flat)).convert('RGB')
        size = (round(im.width * OUT_SCALE), round(im.height * OUT_SCALE))
        slides.append(np.asarray(im.resize(size, Image.LANCZOS)).astype(np.float32))
    slides = np.stack(slides)

    paper = clean_paper(slides)
    for (slug, _, folder), O in zip(SECTIONS, slides):
        spec = json.load(open(os.path.join(SRC, 'placements', f'{folder}.json')))
        build_section(slug, O, os.path.join(SRC, 'objects-png', folder), spec, paper)


if __name__ == '__main__':
    main()
