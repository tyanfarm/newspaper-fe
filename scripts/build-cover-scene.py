"""Cut the home page out of the original Canva elements of its new design.

    python scripts/build-cover-scene.py

Reads design/update-v1/placements/*.json (scripts/locate-elements.py run on
design/update-v1/homepage-design.webp) and writes:

  src/assets/cover/title.webp         the whole header: "Thắp sáng – Số 2011", "Ấn phẩm của L2T NEWS"
  src/assets/cover/logo-kdc.webp, logo-kdi.webp
  src/assets/cover/card-<slug>.webp   each section's card: the elements in its
                                      folder (design/update-v1/<folder>/) composited
                                      in the design's stacking order
  src/assets/cover/<sea part>.webp    lighthouse, beam, sparkle, wave curls, waves, ship
  src/assets/cover/sky.webp, cloud-1..3.webp
  src/assets/cover/bird-1..3.webp     the three largest birds of the exported flock
  src/assets/effects/butterfly-1..2.webp
  src/coverScene.json                 every part's box in design pixels (3179×4494):
                                      the page lays them out from these numbers
"""
import importlib.util
import json
import os
import unicodedata

import cv2
import numpy as np
from PIL import Image

DESIGN = 'design/update-v1'
OLD = 'design/canva-export/objects-png'
OUT = 'src/assets/cover'

SEA = {  # homepage export → asset name (repeats get -2, -3 …)
    'BÁO TƯỜNG 20.11-7.png': 'lighthouse',
    'BÁO TƯỜNG 20.11-10.png': 'beam',
    'BÁO TƯỜNG 20.11-5.png': 'sparkle',
    'BÁO TƯỜNG 20.11-11.png': 'wave-curl',
    'BÁO TƯỜNG 20.11-8.png': 'waves',
    'BÁO TƯỜNG 20.11-9.png': 'ship',
}
LOGOS = {'Bản sao BÁO TƯỜNG 20.11-8.png': 'logo-kdc', 'Bản sao BÁO TƯỜNG 20.11-9.png': 'logo-kdi'}
CLOUDS = {  # update-v1 export → asset name
    'BÁO TƯỜNG 20.11 (2).png': 'sky',
    'BÁO TƯỜNG 20.11 (1).png': 'cloud-1',
    'BÁO TƯỜNG 20.11.png': 'cloud-2',
    'BÁO TƯỜNG 20.11 (19).png': 'cloud-3',
}
TITLE = 'title-header.png'
TITLE_BOTTOM = 900  # design px: the export also holds a stray speck of light far below the header
CARDS = [  # slug, folder, the card's quarter of the design (the airmail paper is in two folders)
    ('loi-ngo', 'loi_ngo', lambda x, y: x < 1700 and y < 2300),
    ('vung-ky-uc', 'vung_ky_uc', lambda x, y: x >= 1700 and y < 2300),
    ('cung-nhau-lon', 'cung_nhau_lon', lambda x, y: x < 1900 and y >= 2300),
    ('loi-tri-an', 'loi_tri_an', lambda x, y: x >= 1900 and y >= 2300),
]
FLOCK = 'Bản sao của BÁO TƯỜNG 20.11.png'
SCALE = dict(card=0.6, title=0.6, sea=0.6, sparkle=0.35, logo=1.0, cloud=0.35, sky=0.25)

spec = importlib.util.spec_from_file_location('layers', os.path.join(os.path.dirname(__file__), 'build-section-layers.py'))
layers_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(layers_mod)


def nfc(s):
    return unicodedata.normalize('NFC', s)


def load(folder, name):
    path = os.path.join(folder, next(n for n in os.listdir(folder) if nfc(n) == name))
    return np.asarray(Image.open(path).convert('RGBA')).astype(np.float32)


def placements(folder):
    return json.load(open(os.path.join(DESIGN, 'placements', f'{folder}.json')))


def draw(E, M, size, clip=False):
    """E drawn where M puts it; returns (x0, y0, full-res crop). With `clip`,
    cut at the design's left and bottom edges (the page's left and bottom)."""
    width, height = size
    M = np.float64(M)
    s = float(np.hypot(M[0, 0], M[1, 0]))
    if s < 1:
        E = cv2.resize(E, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
        M = np.hstack([M[:, :2] / s, M[:, 2:]])
    eh, ew = E.shape[:2]
    corners = cv2.transform(np.float32([[[0, 0], [ew, 0], [ew, eh], [0, eh]]]), np.float32(M))[0]
    x0, y0 = np.floor(corners.min(0)).astype(int)
    x1, y1 = np.ceil(corners.max(0)).astype(int)
    if clip:
        x0, y1 = max(x0, 0), min(y1, height)
    A = M.copy()
    A[:, 2] -= [x0, y0]
    crop = cv2.warpAffine(E, np.float32(A), (int(x1 - x0), int(y1 - y0)), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    ys, xs = np.nonzero(crop[..., 3] > 2)
    return int(x0 + xs.min()), int(y0 + ys.min()), crop[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def save(crop, name, scale, folder=OUT):
    im = Image.fromarray(crop.round().clip(0, 255).astype(np.uint8), 'RGBA').convert('RGBa')
    size = (max(1, round(im.width * scale)), max(1, round(im.height * scale)))
    im.resize(size, Image.LANCZOS).convert('RGBA').save(os.path.join(folder, f'{name}.webp'), 'WEBP', quality=84, method=6, exact=False)


def box(name, x, y, crop, **extra):
    print(f'{name:14s} x={x:5d} y={y:5d} w={crop.shape[1]:5d} h={crop.shape[0]:5d}')
    return dict(name=name, x=x, y=y, w=crop.shape[1], h=crop.shape[0], **extra)


def composite(parts):
    """Stack (x0, y0, crop) parts in order into one image; returns (x0, y0, image)."""
    x0 = min(p[0] for p in parts)
    y0 = min(p[1] for p in parts)
    x1 = max(p[0] + p[2].shape[1] for p in parts)
    y1 = max(p[1] + p[2].shape[0] for p in parts)
    rgb = np.zeros((y1 - y0, x1 - x0, 3), np.float32)  # premultiplied
    a = np.zeros((y1 - y0, x1 - x0), np.float32)
    for x, y, c in parts:
        r = (slice(y - y0, y - y0 + c.shape[0]), slice(x - x0, x - x0 + c.shape[1]))
        ca = c[..., 3] / 255
        rgb[r] = c[..., :3] * ca[..., None] + rgb[r] * (1 - ca[..., None])
        a[r] = ca + a[r] * (1 - ca)
    out = np.dstack([rgb / np.maximum(a, 1e-6)[..., None], a * 255])
    return x0, y0, out


def main():
    O = np.asarray(Image.open(os.path.join(DESIGN, 'homepage-design.webp')).convert('RGB')).astype(np.float32)
    size = (O.shape[1], O.shape[0])
    B = cv2.GaussianBlur(O, (0, 0), 25)  # stand-in for whatever lies under the elements
    scene = dict(width=size[0], height=size[1])

    # Title, logos, clouds.
    top = placements('update-v1')
    for p in top['placements']:
        E = load(DESIGN, p['file'])
        if p['file'] == TITLE:
            x0, y0, crop = draw(E, p['M'], size)
            n, labels, stats, _ = cv2.connectedComponentsWithStats((crop[..., 3] > 20).astype(np.uint8))
            keep = [i for i in range(1, n) if y0 + stats[i, cv2.CC_STAT_TOP] < TITLE_BOTTOM]
            crop[..., 3] *= np.isin(labels, keep)
            ys, xs = np.nonzero(crop[..., 3] > 2)
            crop = crop[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
            x0, y0 = int(x0 + xs.min()), int(y0 + ys.min())
            save(crop, 'title', SCALE['title'])
            scene['title'] = box('title', x0, y0, crop)
        else:
            name = CLOUDS[p['file']]
            x0, y0, crop = draw(E, p['M'], size)
            save(crop, name, SCALE['sky' if name == 'sky' else 'cloud'])
            scene.setdefault('clouds', []).append(box(name, x0, y0, crop))

    # Cards: each folder's elements, stacked as in the design.
    scene['cards'] = []
    for slug, folder, inside in CARDS:
        parts = []
        for p in placements(folder)['placements']:
            E = load(os.path.join(DESIGN, folder), p['file'])
            h, w = E.shape[:2]
            cx, cy = np.float64(p['M']) @ [w / 2, h / 2, 1]
            if inside(cx, cy):
                parts.append(draw(E, p['M'], size))
        order = layers_mod.paint_order(O, parts, B)
        x0, y0, card = composite([parts[i] for i in order])
        save(card, f'card-{slug}', SCALE['card'])
        scene['cards'].append(box(slug, x0, y0, card))
    xs = [c['x'] for c in scene['cards']] + [c['x'] + c['w'] for c in scene['cards']]
    ys = [c['y'] for c in scene['cards']] + [c['y'] + c['h'] for c in scene['cards']]
    scene['board'] = dict(x=min(xs), y=min(ys), w=max(xs) - min(xs), h=max(ys) - min(ys))

    # Sea scene and logos (homepage exports).
    folder = os.path.join(OLD, 'homepage')
    drawn, names, seen = [], [], {}
    scene['logos'] = []
    for p in placements('homepage')['placements']:
        E = load(folder, p['file'])
        if p['file'] in LOGOS:
            x0, y0, crop = draw(E, p['M'], size)
            save(crop, LOGOS[p['file']], SCALE['logo'])
            scene['logos'].append(box(LOGOS[p['file']], x0, y0, crop))
            continue
        base = SEA[p['file']]
        seen[base] = seen.get(base, 0) + 1
        names.append(base if seen[base] == 1 else f'{base}-{seen[base]}')
        drawn.append(draw(E, p['M'], size, clip=True))
    scene['logos'].sort(key=lambda l: l['x'])
    # Stacking order as in the design (the beam over the lighthouse, the ship
    # over the big wave …).
    order = layers_mod.paint_order(O, drawn, B)
    scene['sea'] = []
    for z, i in enumerate(order):
        x0, y0, crop = drawn[i]
        save(crop, names[i], SCALE['sparkle' if names[i] == 'sparkle' else 'sea'])
        scene['sea'].append(box(names[i], x0, y0, crop, z=z))

    flock = load(folder, FLOCK)
    n, labels, stats, _ = cv2.connectedComponentsWithStats((flock[..., 3] > 20).astype(np.uint8))
    biggest = sorted(range(1, n), key=lambda i: -stats[i, cv2.CC_STAT_AREA])[:3]
    for k, i in enumerate(sorted(biggest, key=lambda i: stats[i, cv2.CC_STAT_LEFT])):
        x, y, w, h = stats[i, :4]
        bird = flock[y:y + h, x:x + w].copy()
        bird[..., 3] *= labels[y:y + h, x:x + w] == i
        save(bird, f'bird-{k + 1}', 1)

    effects = os.path.join(OLD, 'effects')
    os.makedirs('src/assets/effects', exist_ok=True)
    for k, name in enumerate(['bướm 1.png', 'bướm 2.png']):
        E = load(effects, name)
        ys, xs = np.nonzero(E[..., 3] > 2)
        E = E[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        save(E, f'butterfly-{k + 1}', min(1, 240 / max(E.shape[:2])), folder='src/assets/effects')

    with open('src/coverScene.json', 'w') as fh:
        json.dump(scene, fh, indent=1)


if __name__ == '__main__':
    main()
