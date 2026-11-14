"""Cut the home page's sea scene out of the original Canva elements.

    python scripts/build-cover-scene.py

Reads design/canva-export/placements/homepage.json (scripts/locate-elements.py)
and writes, for each element, src/assets/cover/<name>.webp drawn exactly as on
slide 1 (scale, rotation), plus src/coverScene.json: each element's box in
slide-1 pixels and its stacking order. The home page lays the scene out in
those same coordinates, so the lighthouse, its beam, the waves, the ship and
the logos keep their arrangement from the slide.

Birds come from the exported flock: its three largest birds become
bird-1..3.webp (the flock itself is not on slide 1 as one piece).

Also writes the two butterflies (objects-png/effects) that fly out when a
section opens: src/assets/effects/butterfly-1.webp, butterfly-2.webp.
"""
import importlib.util
import json
import os
import unicodedata

import cv2
import numpy as np
from PIL import Image

SRC = 'design/canva-export'
OUT = 'src/assets/cover'
SCALE = 0.5  # slide-1 pixels → image pixels (the scene never shows larger)
NAMES = {  # export file → asset name (repeats get -2, -3 …)
    'BÁO TƯỜNG 20.11-7.png': 'lighthouse',
    'BÁO TƯỜNG 20.11-10.png': 'beam',
    'BÁO TƯỜNG 20.11-11.png': 'wave-curl',
    'BÁO TƯỜNG 20.11-8.png': 'waves',
    'BÁO TƯỜNG 20.11-9.png': 'ship',
    'Bản sao BÁO TƯỜNG 20.11-9.png': 'logo-kdi',
    'Bản sao BÁO TƯỜNG 20.11-8.png': 'logo-kdc',
}
FLOCK = 'Bản sao của BÁO TƯỜNG 20.11.png'

spec = importlib.util.spec_from_file_location('layers', os.path.join(os.path.dirname(__file__), 'build-section-layers.py'))
layers_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(layers_mod)


def nfc(s):
    return unicodedata.normalize('NFC', s)


def load(folder, name):
    path = os.path.join(folder, next(n for n in os.listdir(folder) if nfc(n) == name))
    return np.asarray(Image.open(path).convert('RGBA')).astype(np.float32)


def draw(E, M, width, height):
    """E drawn where M puts it, clipped to the slide's left and bottom edges
    (the page's left and bottom edges); returns (x0, y0, full-res crop)."""
    M = np.float64(M)
    s = float(np.hypot(M[0, 0], M[1, 0]))
    if s < 1:
        E = cv2.resize(E, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
        M = np.hstack([M[:, :2] / s, M[:, 2:]])
    eh, ew = E.shape[:2]
    corners = cv2.transform(np.float32([[[0, 0], [ew, 0], [ew, eh], [0, eh]]]), np.float32(M))[0]
    x0, y0 = np.floor(corners.min(0)).astype(int)
    x1, y1 = np.ceil(corners.max(0)).astype(int)
    x0, y1 = max(x0, 0), min(y1, height)
    A = M.copy()
    A[:, 2] -= [x0, y0]
    crop = cv2.warpAffine(E, np.float32(A), (int(x1 - x0), int(y1 - y0)), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    ys, xs = np.nonzero(crop[..., 3] > 2)
    return int(x0 + xs.min()), int(y0 + ys.min()), crop[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def save(crop, path, scale=SCALE):
    im = Image.fromarray(crop.round().clip(0, 255).astype(np.uint8), 'RGBA').convert('RGBa')
    size = (max(1, round(im.width * scale)), max(1, round(im.height * scale)))
    im.resize(size, Image.LANCZOS).convert('RGBA').save(path, 'WEBP', quality=84, method=6, exact=False)


def main():
    folder = os.path.join(SRC, 'objects-png', 'homepage')
    placements = json.load(open(os.path.join(SRC, 'placements', 'homepage.json')))
    width, height = placements['size']
    O = np.asarray(Image.open(os.path.join(SRC, placements['slide'])).convert('RGB')).astype(np.float32)

    drawn, names, seen = [], [], {}
    for p in placements['placements']:
        base = NAMES[p['file']]
        seen[base] = seen.get(base, 0) + 1
        names.append(base if seen[base] == 1 else f'{base}-{seen[base]}')
        drawn.append(draw(load(folder, p['file']), p['M'], width, height))

    # Stacking order as on the slide (the beam over the lighthouse, the ship
    # over the big wave …). The background under them does not matter here.
    order = layers_mod.paint_order(O, drawn, cv2.GaussianBlur(O, (0, 0), 25))

    scene = []
    for z, i in enumerate(order):
        x0, y0, crop = drawn[i]
        save(crop, os.path.join(OUT, f'{names[i]}.webp'))
        scene.append(dict(name=names[i], x=x0, y=y0, w=crop.shape[1], h=crop.shape[0], z=z))
        print(f'{names[i]:12s} x={x0:5d} y={y0:5d} w={crop.shape[1]:5d} h={crop.shape[0]:5d} z={z}')

    flock = load(folder, FLOCK)
    n, labels, stats, _ = cv2.connectedComponentsWithStats((flock[..., 3] > 20).astype(np.uint8))
    biggest = sorted(range(1, n), key=lambda i: -stats[i, cv2.CC_STAT_AREA])[:3]
    for k, i in enumerate(sorted(biggest, key=lambda i: stats[i, cv2.CC_STAT_LEFT])):
        x, y, w, h = stats[i, :4]
        bird = flock[y:y + h, x:x + w].copy()
        bird[..., 3] *= labels[y:y + h, x:x + w] == i
        save(bird, os.path.join(OUT, f'bird-{k + 1}.webp'), scale=1)
        print(f'bird-{k + 1}       {w}×{h}')

    effects = os.path.join(SRC, 'objects-png', 'effects')
    os.makedirs('src/assets/effects', exist_ok=True)
    for k, name in enumerate(['bướm 1.png', 'bướm 2.png']):
        E = load(effects, name)
        ys, xs = np.nonzero(E[..., 3] > 2)
        E = E[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        save(E, f'src/assets/effects/butterfly-{k + 1}.webp', scale=min(1, 240 / max(E.shape[:2])))
        print(f'butterfly-{k + 1}  from {name}')

    with open('src/coverScene.json', 'w') as fh:
        json.dump(dict(width=width, height=height, elements=scene), fh, indent=1)


if __name__ == '__main__':
    main()
