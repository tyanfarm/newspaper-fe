"""Find where each exported Canva element sits on its flat slide.

    python scripts/locate-elements.py <slide.webp> <elements-dir> <out.json> [--debug overlay.png]

Every PNG in <elements-dir> is located on the slide and written to <out.json>
as a 2x3 affine matrix (element pixel -> slide pixel), so the page can be
rebuilt layer by layer at exactly the original positions.

Textured elements (photos, drawings) are found with SIFT feature matching,
which also recovers scale and rotation and finds repeated copies. Flat or tiny
elements (petals, logos) have too few features; for those, list a search in
FALLBACK below and they are found by masked template matching over
scale/rotation/flip. The last resort is a hand-measured 'fixed' placement.

Each placement is checked by re-drawing the element at that spot and measuring
how well it matches the slide (`match` = share of opaque element pixels within
24 levels of the slide). Placements under MIN_MATCH are reported and dropped.
"""
import json
import os
import sys
import unicodedata

import cv2
import numpy as np
from PIL import Image, ImageDraw

MIN_MATCH = 0.30  # semi-transparent elements (Canva opacity) still score ~0.4+

# Searches for elements SIFT cannot find, keyed by (folder, NFC file name).
# region: slide-pixel box to search; scales/rots/flip/count: search space.
FALLBACK = {
    # loi_tri_an: seven falling petals, all the same drawing (tải 7–13).
    ('loi_tri_an', 'tải (8).png'): dict(region=(0, 2700, 900, 4400), scales=(0.5, 2.0, 14), rots=range(0, 360, 15), flip=True, count=7),
    # homepage: KDC logo (flat colour).
    ('homepage', 'Bản sao BÁO TƯỜNG 20.11-8.png'): dict(region=(2400, 3900, 3179, 4494), scales=(1.2, 1.8, 13), rots=(0,), flip=False, count=1),
    # Hand-measured, then checked by overlay (`--debug`). The thin vine defeats
    # both searches; it was pinned by a brute-force sweep around a hand-picked
    # seed (match 0.86). The beam is a soft glow over the lighthouse, so it
    # cannot be scored pixel-wise: apex on the lamp, rays down to the red band.
    ('loi_tri_an', 'Bản sao của BÁO TƯỜNG 20.11 (8).png'): dict(method='fixed', M=[[1.107, 0, 296], [0, 1.107, 3876]]),
    ('homepage', 'BÁO TƯỜNG 20.11-10.png'): dict(method='fixed', M=[[0.8, 0, 48], [0, 0.8, 2819]]),
}
# The other petal exports are copies of tải (8); its search places all seven.
SKIP = {'tải (7).png', 'tải (9).png', 'tải (10).png', 'tải (11).png', 'tải (12).png', 'tải (13).png'}
# Exported but not on the slide (no position to copy); listed so the run says so.
NOT_ON_SLIDE = {('homepage', 'BÁO TƯỜNG 20.11-5.png'), ('homepage', 'BÁO TƯỜNG 20.11-6.png')}

# The redesigned home page (design/update-v1/homepage-design.webp) reuses the
# homepage exports at partly new places. Entries here replace the ones above
# for that slide only (None = no special search, use SIFT).
SLIDE_OVERRIDES = {
    'homepage-design.webp': dict(
        fallback={
            ('homepage', 'Bản sao BÁO TƯỜNG 20.11-8.png'): dict(region=(2300, 0, 3179, 400), scales=(0.8, 1.3, 11), rots=(0,), flip=False, count=1),
            # Clouds are soft and semi-transparent: no features to match, so
            # placed by eye against the design.
            ('update-v1', 'BÁO TƯỜNG 20.11 (2).png'): dict(method='fixed', M=[[1, 0, -25], [0, 1, -350]]),
            ('update-v1', 'BÁO TƯỜNG 20.11 (1).png'): dict(method='fixed', M=[[1, 0, 900], [0, 1, -350]]),
            ('update-v1', 'BÁO TƯỜNG 20.11.png'): dict(method='fixed', M=[[1, 0, 1500], [0, 1, 1300]]),
            # Tucked behind the Cùng nhau lớn card; only a sliver of its brown
            # outline shows at the card's right edge.
            ('cung_nhau_lon', 'BÁO TƯỜNG 20.11 (11).png'): dict(method='fixed', M=[[1, 0, 1281], [0, 1, 2492]]),
            # Golden sparkles around the lamp: SIFT's best guess (too faint to score).
            ('homepage', 'BÁO TƯỜNG 20.11-5.png'): dict(method='fixed', M=[[1.239, 0, -289], [0, 1.239, 2520]]),
        },
        # The birds in the exported flock are not arranged as on the page, and
        # the light ribbon is not the ring drawn around the lamp.
        not_on_slide={('homepage', 'Bản sao của BÁO TƯỜNG 20.11.png'), ('homepage', 'BÁO TƯỜNG 20.11-6.png')},
    ),
}


def nfc(s):
    return unicodedata.normalize('NFC', s)


def load_rgba(path):
    return np.array(Image.open(path).convert('RGBA')).astype(np.float32)


def warp(E, M, shape):
    h, w = shape
    return cv2.warpAffine(E, np.float32(M), (w, h), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))


def match_score(O, E, M):
    """Share of the element's solid pixels that agree with the slide.

    Canva bakes element transparency into the PNG alpha (e.g. 153/255), so the
    element is composited over a local estimate of what lies beneath it.
    """
    W = warp(E, M, O.shape[:2])
    a = W[..., 3] / 255
    solid = a > 0.9 * a.max()
    if int(solid.sum()) < 50:
        return 0.0
    outside = (a < 0.02).astype(np.float32)
    under = cv2.GaussianBlur(O * outside[..., None], (0, 0), 40) / np.maximum(
        cv2.GaussianBlur(outside, (0, 0), 40)[..., None], 1e-3)
    pred = W[..., :3] * a[..., None] + under * (1 - a[..., None])
    d = np.abs(O[solid] - pred[solid]).max(axis=1)
    return float((d < 24).mean())


def sift_locate(O, gray, E, sift, kp_s, des_s):
    a = E[..., 3]
    comp = E[..., :3] * (a[..., None] / 255) + np.array([225, 210, 185]) * (1 - a[..., None] / 255)
    g = cv2.cvtColor(comp.astype(np.uint8), cv2.COLOR_RGB2GRAY)
    kp_e, des_e = sift.detectAndCompute(g, (a > 128).astype(np.uint8) * 255)
    if des_e is None or len(kp_e) < 4:
        return []
    knn = cv2.BFMatcher(cv2.NORM_L2).knnMatch(des_e, des_s, k=2)
    pts_s = np.float32([k.pt for k in kp_s])
    alive = np.ones(len(kp_s), bool)
    found = []
    while len(found) < 8:
        good = [p[0] for p in knn if len(p) == 2 and alive[p[0].trainIdx] and p[0].distance < 0.8 * p[1].distance]
        if len(good) < 8:
            break
        src = np.float32([kp_e[m.queryIdx].pt for m in good])
        dst = np.float32([kp_s[m.trainIdx].pt for m in good])
        M, inl = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=6, maxIters=5000)
        if M is None or int(inl.sum()) < 10:
            break
        scale = float(np.hypot(M[0, 0], M[1, 0]))
        if not 0.2 < scale < 5:
            break
        found.append(dict(M=M.tolist(), method='sift', inliers=int(inl.sum())))
        mask = warp(a[..., None].repeat(4, 2), M, gray.shape)[..., 0]
        ix = np.clip(pts_s.astype(int), 0, [gray.shape[1] - 1, gray.shape[0] - 1])
        alive &= mask[ix[:, 1], ix[:, 0]] < 64
    return found


def template_locate(O, E, region, scales, rots, flip, count, ds=0.5):
    x0, y0, x1, y1 = region
    sub = cv2.resize(O[y0:y1, x0:x1], None, fx=ds, fy=ds, interpolation=cv2.INTER_AREA)
    h, w = E.shape[:2]
    cands = []
    for fl in ((False, True) if flip else (False,)):
        for rot in rots:
            for s in np.geomspace(scales[0], scales[1], scales[2]):
                # element pixel -> slide pixel (before translation)
                F = np.array([[-1, 0, w], [0, 1, 0], [0, 0, 1]], float) if fl else np.eye(3)
                R = np.vstack([cv2.getRotationMatrix2D((w / 2, h / 2), rot, s), [0, 0, 1]])
                A = (R @ F)[:2]
                corners = cv2.transform(np.float32([[[0, 0], [w, 0], [w, h], [0, h]]]), A)[0]
                A[:, 2] -= corners.min(0)
                tw, th = (corners.max(0) - corners.min(0)).astype(int) + 1
                S = np.array([[ds, 0, 0], [0, ds, 0]])
                T = cv2.warpAffine(E, S @ np.vstack([A, [0, 0, 1]]), (max(3, int(tw * ds)), max(3, int(th * ds))),
                                   flags=cv2.INTER_AREA, borderValue=(0, 0, 0, 0))
                if T.shape[0] >= sub.shape[0] or T.shape[1] >= sub.shape[1]:
                    continue
                m = (T[..., 3:4] > 128).astype(np.float32).repeat(3, 2)
                if m.sum() < 30:
                    continue
                r = cv2.matchTemplate(sub, np.ascontiguousarray(T[..., :3]), cv2.TM_SQDIFF, mask=m) / m.sum()
                for _ in range(count * 2):
                    v, _, loc, _ = cv2.minMaxLoc(r)
                    M = A.copy()
                    M[:, 2] += [x0 + loc[0] / ds, y0 + loc[1] / ds]
                    cands.append((v, M, (x0 + (loc[0] + T.shape[1] / 2) / ds, y0 + (loc[1] + T.shape[0] / 2) / ds), min(tw, th)))
                    cv2.rectangle(r, (loc[0] - T.shape[1] // 2, loc[1] - T.shape[0] // 2),
                                  (loc[0] + T.shape[1] // 2, loc[1] + T.shape[0] // 2), float(1e12), -1)
    cands.sort(key=lambda c: c[0])
    picked = []
    for v, M, c, size in cands:
        if any(np.hypot(c[0] - p[2][0], c[1] - p[2][1]) < size * 0.6 for p in picked):
            continue
        picked.append((v, M, c, size))
        if len(picked) == count:
            break
    return [dict(M=M.tolist(), method='template', sqdiff=round(float(v), 1)) for v, M, _, _ in picked]


def snap(M):
    """Most exports are at the slide's own resolution: make those exact copies.

    A fitted scale within 0.4% of 1 with no rotation is noise, and rounding the
    offset to whole pixels lets the element reproduce the slide pixel for pixel.
    """
    M = np.float64(M)
    scale = np.hypot(M[0, 0], M[1, 0])
    angle = np.degrees(np.arctan2(M[1, 0], M[0, 0]))
    if abs(scale - 1) < 0.004 and abs(angle) < 0.2 and M[0, 0] > 0:
        return [[1.0, 0.0, float(round(M[0, 2]))], [0.0, 1.0, float(round(M[1, 2]))]]
    return M.tolist()


def main():
    slide_path, folder, out_path = sys.argv[1:4]
    debug = sys.argv[sys.argv.index('--debug') + 1] if '--debug' in sys.argv else None
    O = np.array(Image.open(slide_path).convert('RGB')).astype(np.float32)
    gray = cv2.cvtColor(O.astype(np.uint8), cv2.COLOR_RGB2GRAY)
    sift = cv2.SIFT_create(contrastThreshold=0.02)
    kp_s, des_s = sift.detectAndCompute(gray, None)

    group = os.path.basename(os.path.normpath(folder))
    override = SLIDE_OVERRIDES.get(os.path.basename(slide_path), {})
    fallback = {**FALLBACK, **override.get('fallback', {})}
    not_on_slide = override.get('not_on_slide', NOT_ON_SLIDE)
    placements = []
    for name in sorted(os.listdir(folder), key=nfc):
        key = nfc(name)
        if key in SKIP or not key.lower().endswith('.png'):
            continue
        if (group, key) in not_on_slide:
            print(f'not on slide: {key}', file=sys.stderr)
            continue
        E = load_rgba(os.path.join(folder, name))
        fb = fallback.get((group, key))
        if fb and fb.get('method') == 'fixed':
            found = [dict(M=fb['M'], method='fixed')]
        elif fb:
            found = template_locate(O, E, **fb)
        else:
            found = sift_locate(O, gray, E, sift, kp_s, des_s)
        kept = 0
        for f in found:
            f['M'] = snap(f['M'])
            f['match'] = round(match_score(O, E, f['M']), 3)
            ok = f['match'] >= MIN_MATCH or f['method'] == 'fixed'
            print(f"{'ok ' if ok else 'DROP'} {key[:40]:40s} {f['method']:8s} match={f['match']:.2f} "
                  f"scale={np.hypot(f['M'][0][0], f['M'][1][0]):.3f} t=({f['M'][0][2]:.0f},{f['M'][1][2]:.0f})", file=sys.stderr)
            if ok:
                placements.append(dict(file=key, **f))
                kept += 1
        if not kept:
            print(f'MISSING {key}', file=sys.stderr)

    with open(out_path, 'w') as fh:
        json.dump(dict(slide=os.path.basename(slide_path), size=[O.shape[1], O.shape[0]], placements=placements),
                  fh, ensure_ascii=False, indent=1)

    if debug:
        img = Image.open(slide_path).convert('RGB')
        dr = ImageDraw.Draw(img)
        for i, p in enumerate(placements):
            E = Image.open(os.path.join(folder, next(n for n in os.listdir(folder) if nfc(n) == p['file'])))
            a = np.array(E.getchannel('A'))
            mask = warp(a[..., None].astype(np.float32).repeat(4, 2), p['M'], O.shape[:2])[..., 0] > 128
            cnts, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            col = [(255, 0, 0), (0, 160, 0), (0, 0, 255), (255, 0, 255), (0, 170, 170), (230, 120, 0)][i % 6]
            for c in cnts:
                dr.line([tuple(pt[0]) for pt in c] + [tuple(c[0][0])], fill=col, width=10)
            ys, xs = np.nonzero(mask)
            if len(xs):
                dr.text((int(xs.mean()), int(ys.mean())), str(i), fill=col, font_size=90)
        img.thumbnail((1000, 1400))
        img.save(debug)


if __name__ == '__main__':
    main()
