"""Extract the cover's elements from the flattened Canva export into web assets.

Usage:
    python scripts/extract-cover.py design/canva-export/1.webp src/assets/cover [--sheet preview.png]

Needs Pillow, numpy and rembg (see scripts/README.md). Every output has a fixed
file name, so any of them can later be replaced by a clean Canva export of the
same element without touching the code.
"""

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps
from rembg import new_session, remove

# Boxes are measured on a 795px-wide preview of the cover and scaled to the
# real image. (left, top, right, bottom)
PREVIEW_WIDTH = 795
BOXES = {
    "title": (15, 32, 770, 205),
    "lighthouse": (0, 600, 200, 1040),
    "ship": (195, 925, 425, 1124),
    "bird": (0, 255, 110, 320),
    "logos": (545, 1052, 795, 1124),
    "sea": (418, 985, 545, 1124),
    "paper": (362, 250, 445, 465),
}
CARDS = {
    "loi-ngo": (105, 226, 362, 574),
    "vung-ky-uc": (443, 220, 712, 574),
    "cung-nhau-lon": (186, 580, 452, 928),
    "loi-tri-an": (493, 568, 782, 930),
}
# Long-edge caps in px: ("w" = cap width, "h" = cap height)
CAPS = {
    "title": ("w", 2400),
    "lighthouse": ("h", 1600),
    "ship": ("w", 1200),
    "bird": ("w", 400),
    "card": ("w", 900),
}


def crop(im: Image.Image, box: tuple[int, int, int, int]) -> Image.Image:
    k = im.width / PREVIEW_WIDTH
    return im.crop(tuple(round(v * k) for v in box))


def trim(im: Image.Image) -> Image.Image:
    """Drop fully transparent margins so CSS sizes map to the visible object."""
    bbox = im.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
    return im.crop(bbox) if bbox else im


def cap(im: Image.Image, kind: str) -> Image.Image:
    axis, limit = CAPS[kind]
    size = im.width if axis == "w" else im.height
    if size <= limit:
        return im
    scale = limit / size
    return im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)


def card_cutout(region: Image.Image, session) -> Image.Image:
    """Solid inside the airmail border, rembg matte outside it.

    rembg alone erases the card's paper (it reads as background), but it does
    keep the butterflies, lilies and photos that overhang the border.
    """
    a = np.asarray(region).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = (r > 170) & (g < 125) & (b < 125)
    blue = (b > 120) & (r < 130) & (b - r > 40) & (g < 150)
    stripe = red | blue
    cols = np.where(stripe.mean(axis=0) > 0.18)[0]
    rows = np.where(stripe.mean(axis=1) > 0.18)[0]
    if cols.size == 0 or rows.size == 0:
        raise SystemExit("Could not find the card's airmail border; adjust CARDS boxes.")
    x0, x1, y0, y1 = cols.min(), cols.max(), rows.min(), rows.max()
    alpha = np.asarray(remove(region, session=session, only_mask=True)).astype(np.uint8)
    alpha[y0 : y1 + 1, x0 : x1 + 1] = 255
    out = region.convert("RGBA")
    out.putalpha(Image.fromarray(alpha))
    return out


def title_cutout(region: Image.Image, session) -> Image.Image:
    out = remove(region, session=session)
    a = np.asarray(out.getchannel("A")).astype(float)
    # Faded copies (the "Ấn phẩm…" line, the drop shadow) come back half
    # transparent; keep only the solid lettering.
    a = np.clip((a - 150) * 255 / 105, 0, 255)
    h, w = a.shape
    a[int(h * 0.83) :, int(w * 0.6) :] = 0  # strip where the subtitle sat
    out.putalpha(Image.fromarray(a.astype(np.uint8)))
    return out


def mirrored_strip(im: Image.Image) -> Image.Image:
    """im followed by its mirror: tiles horizontally without a seam."""
    out = Image.new("RGB", (im.width * 2, im.height))
    out.paste(im, (0, 0))
    out.paste(ImageOps.mirror(im), (im.width, 0))
    return out


def save(im: Image.Image, path: Path) -> None:
    im.save(path, "WEBP", quality=85, method=6)
    print(f"{path.name:28} {im.width}x{im.height}  {path.stat().st_size / 1024:7.1f} KB")


def preview_sheet(paths: list[Path], dest: Path) -> None:
    tiles = []
    for p in paths:
        im = Image.open(p).convert("RGBA")
        im.thumbnail((300, 300))
        bg = Image.new("RGBA", im.size, (235, 235, 235, 255))
        for y in range(0, im.height, 16):
            for x in range((y // 16) % 2 * 16, im.width, 32):
                bg.paste((200, 200, 200, 255), (x, y, x + 16, y + 16))
        bg.alpha_composite(im)
        tiles.append(bg)
    width = 1500
    x = y = row_h = 10
    placed = []
    for t in tiles:
        if x + t.width > width:
            x, y, row_h = 10, y + row_h + 10, 10
        placed.append((t, x, y))
        x += t.width + 10
        row_h = max(row_h, t.height)
    sheet = Image.new("RGB", (width, y + row_h + 10), (60, 60, 60))
    for t, px, py in placed:
        sheet.paste(t.convert("RGB"), (px, py))
    sheet.save(dest)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cover", type=Path)
    ap.add_argument("out_dir", type=Path)
    ap.add_argument("--sheet", type=Path, help="write a checkerboard preview of every output here")
    args = ap.parse_args()

    im = Image.open(args.cover).convert("RGB")
    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)
    session = new_session("isnet-general-use")
    written: list[Path] = []

    def emit(name: str, image: Image.Image) -> None:
        path = out / f"{name}.webp"
        save(image, path)
        written.append(path)

    emit("title", cap(trim(title_cutout(crop(im, BOXES["title"]), session)), "title"))
    for name in ("lighthouse", "ship", "bird"):
        emit(name, cap(trim(remove(crop(im, BOXES[name]), session=session)), name))
    for slug, box in CARDS.items():
        emit(f"card-{slug}", cap(trim(card_cutout(crop(im, box), session)), "card"))
    emit("logos", crop(im, BOXES["logos"]))
    emit("sea-tile", mirrored_strip(crop(im, BOXES["sea"])))
    paper = mirrored_strip(crop(im, BOXES["paper"]))
    emit("paper-tile", Image.fromarray(np.vstack([np.asarray(paper), np.asarray(ImageOps.flip(paper))])))

    total = sum(p.stat().st_size for p in written)
    print(f"{len(written)} files, {total / 1024 / 1024:.2f} MB")
    if args.sheet:
        preview_sheet(written, args.sheet)


if __name__ == "__main__":
    main()
