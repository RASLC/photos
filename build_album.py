#!/usr/bin/env python3
"""
build_album.py  —  Convert a folder of photos to AVIF (or WebP) and generate the
album code block to paste into your Archive site's index.html.

Handles .arw (Sony RAW), .jpg, .jpeg, .png, .tif/.tiff.
Reads EXIF (camera, lens, focal, aperture, shutter, ISO, date, GPS) and writes it
into the album block. GPS is rounded to ~11 km for privacy. AVIF/WebP output files
do NOT contain EXIF.

USAGE (from a Command Prompt / PowerShell):
    python build_album.py "C:\\path\\to\\photos" --title "Japan 2024" --place "Osaka"

Common options:
    --title    "Album Title"     (required-ish; defaults to the folder name)
    --place    "Default location" (used for the album and as each photo's default)
    --format   avif | webp        (default: avif)
    --quality  0-100              (default: 60 for avif, 82 for webp)
    --max      2000               (longest edge in pixels; default 2000)
    --out      "C:\\path\\to\\site" (where the 'images' folder lives; default: current dir)
    --sort     date | name        (default: date, i.e. chronological by capture time)

OUTPUT:
    <out>\\images\\<album-slug>\\01.avif, 02.avif, ...
    <out>\\<album-slug>_album.txt   (the code block to paste into index.html)

FIRST-TIME SETUP (once):
    pip install pillow pillow-avif-plugin rawpy exifread reverse_geocoder
"""

import argparse, os, re, sys, unicodedata
from fractions import Fraction

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Missing Pillow.  Run:  pip install pillow pillow-avif-plugin rawpy exifread")

# AVIF plugin (registers the AVIF encoder with Pillow)
try:
    import pillow_avif  # noqa: F401
except ImportError:
    pillow_avif = None
try:
    import rawpy
except ImportError:
    rawpy = None
try:
    import exifread
except ImportError:
    exifread = None
try:
    import reverse_geocoder as _rg          # optional: turns GPS into "City, Country"
except ImportError:
    _rg = None

RAW_EXT = {".arw", ".raw", ".nef", ".cr2", ".cr3", ".dng"}
IMG_EXT = {".jpg", ".jpeg", ".png", ".tif", ".tiff"} | RAW_EXT

# ---- friendly camera-model names (extend as you like) --------------------------
MODEL_MAP = {
    "ILCE-7RM5": "Sony \u03b17R V", "ILCE-7RM4A": "Sony \u03b17R IV",
    "ILCE-7RM4": "Sony \u03b17R IV", "ILCE-7RM3A": "Sony \u03b17R III",
    "ILCE-7RM3": "Sony \u03b17R III", "ILCE-7M4": "Sony \u03b17 IV",
}
LENS_MAP = {"A067": "Tamron 50-400mm", "A063": "Tamron 28-200mm", "A036": "Tamron 28-75mm"}
PHONE_MAKES = ("google", "apple", "samsung", "oneplus", "xiaomi", "huawei")

# ISO 3166-1 alpha-2 -> country name (common ones; unknown codes fall back to the code)
COUNTRY = {
 "AR":"Argentina","AT":"Austria","AU":"Australia","BE":"Belgium","BR":"Brazil","CA":"Canada",
 "CH":"Switzerland","CL":"Chile","CN":"China","CO":"Colombia","CZ":"Czechia","DE":"Germany",
 "DK":"Denmark","EG":"Egypt","ES":"Spain","FI":"Finland","FR":"France","GB":"United Kingdom",
 "GR":"Greece","HK":"Hong Kong","HR":"Croatia","HU":"Hungary","ID":"Indonesia","IE":"Ireland",
 "IL":"Israel","IN":"India","IS":"Iceland","IT":"Italy","JP":"Japan","KE":"Kenya","KR":"South Korea",
 "MA":"Morocco","MX":"Mexico","MY":"Malaysia","NL":"Netherlands","NO":"Norway","NZ":"New Zealand",
 "PE":"Peru","PH":"Philippines","PL":"Poland","PT":"Portugal","RO":"Romania","RU":"Russia",
 "SE":"Sweden","SG":"Singapore","TH":"Thailand","TR":"Turkey","TW":"Taiwan","UA":"Ukraine",
 "US":"United States","VN":"Vietnam","ZA":"South Africa",
}
_CITY_SUFFIXES = ("-shi", "-ku", "-cho", "-machi", "-mura", "-gun", "-si", " City")


def clean_city(name):
    for suf in _CITY_SUFFIXES:
        if name.lower().endswith(suf.lower()):
            return name[: -len(suf)]
    return name


def geocode_labels(coords):
    """coords: list of (lat, lon) or None. Returns list of 'City, Country' (or '')."""
    out = [""] * len(coords)
    idx = [i for i, c in enumerate(coords) if c]
    if not idx or _rg is None:
        return out
    try:
        res = _rg.search([coords[i] for i in idx], mode=1)   # mode=1 = single-thread (Windows-safe)
    except Exception as e:
        print(f"  (skipping place labels: {e})")
        return out
    for i, r in zip(idx, res):
        city = clean_city((r.get("name") or "").strip())
        country = COUNTRY.get(r.get("cc", ""), r.get("cc", ""))
        out[i] = ", ".join(p for p in (city, country) if p)
    return out



def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s or "album"


def jsq(s):
    return (s or "").replace('"', "'").strip()


def to_float(x):
    try:
        if isinstance(x, str) and "/" in x:
            return float(Fraction(x))
        return float(x)
    except Exception:
        return None


def read_exif(path):
    """Return a dict of the EXIF tags we care about, via exifread (works for jpg + raw)."""
    if exifread is None:
        return {}
    try:
        with open(path, "rb") as f:
            t = exifread.process_file(f, details=False)
    except Exception:
        return {}
    g = lambda k: str(t[k]) if k in t else None
    return {
        "make": g("Image Make"), "model": g("Image Model"), "lens": g("EXIF LensModel"),
        "focal": g("EXIF FocalLength"), "fnum": g("EXIF FNumber"),
        "exp": g("EXIF ExposureTime"), "iso": g("EXIF ISOSpeedRatings"),
        "date": g("EXIF DateTimeOriginal"), "ebias": g("EXIF ExposureBiasValue"),
        "meter": g("EXIF MeteringMode"), "wb": g("EXIF WhiteBalance"), "flash": g("EXIF Flash"),
        "lat": g("GPS GPSLatitude"), "latref": g("GPS GPSLatitudeRef"),
        "lon": g("GPS GPSLongitude"), "lonref": g("GPS GPSLongitudeRef"),
    }


METER = {0: "Unknown", 1: "Average", 2: "Center-weighted", 3: "Spot",
         4: "Multi-spot", 5: "Multi", 6: "Partial"}


def fmt_shutter(e):
    e = to_float(e)
    if not e or e <= 0:
        return ""
    return f"{e:.0f}s" if e >= 1 else f"1/{round(1/e)}s"


def fmt_fnum(n):
    n = to_float(n)
    return "" if n is None else (f"f/{n:.0f}" if abs(n - round(n)) < 0.05 else f"f/{n:.1f}")


def fmt_focal(f):
    f = to_float(f)
    return "" if f is None else f"{f:.0f}mm"


def parse_gps(v, ref):
    """exifread lat/lon come as '[d, m, s]' strings; return signed decimal or None."""
    if not v:
        return None
    try:
        nums = [to_float(x) for x in re.findall(r"[\d.]+(?:/\d+)?", v)]
        if len(nums) < 3:
            return None
        dec = nums[0] + nums[1] / 60 + nums[2] / 3600
        if ref and ref.strip().upper() in ("S", "W"):
            dec = -dec
        return dec
    except Exception:
        return None


def build_fields(ex):
    make = (ex.get("make") or "").strip()
    model = (ex.get("model") or "").strip()
    is_phone = any(p in make.lower() for p in PHONE_MAKES)

    if model in MODEL_MAP:
        camera = MODEL_MAP[model]
    elif is_phone:
        camera = f"{make} {model}".strip()
    elif make and make.lower() not in model.lower():
        camera = f"{make} {model}".strip()
    else:
        camera = model

    lens = (ex.get("lens") or "").strip()
    for code, name in LENS_MAP.items():
        if code in lens:
            lens = name
            break
    gear = camera + (f" \u00b7 {lens}" if lens and not is_phone else "")

    focal, fnum = fmt_focal(ex.get("focal")), fmt_fnum(ex.get("fnum"))
    shutter = fmt_shutter(ex.get("exp"))
    iso = ex.get("iso")
    iso_s = f"ISO {int(to_float(iso))}" if to_float(iso) else ""
    shot_parts = [] if is_phone else [focal]          # drop tiny phone focal length
    shot_parts += [fnum, shutter, iso_s]
    shot = " \u00b7 ".join(p for p in shot_parts if p)

    extra = []
    eb = to_float(ex.get("ebias"))
    if eb is not None:
        extra.append(f"{eb:+.1f} EV" if eb else "0 EV")
    m = to_float(ex.get("meter"))
    if m is not None and int(m) in METER:
        extra.append(METER[int(m)])
    wb = to_float(ex.get("wb"))
    if wb is not None:
        extra.append("WB auto" if int(wb) == 0 else "WB manual")
    fl = to_float(ex.get("flash"))
    if fl is not None:
        extra.append("Flash" if (int(fl) & 1) else "No flash")
    extra = " \u00b7 ".join(extra)

    lat = parse_gps(ex.get("lat"), ex.get("latref"))
    lon = parse_gps(ex.get("lon"), ex.get("lonref"))
    geo = f"{lat:.4f}, {lon:.4f}" if lat is not None and lon is not None else ""

    date = ""
    if ex.get("date"):
        try:
            date = ex["date"].split()[0].replace(":", "-")
        except Exception:
            pass
    return dict(gear=gear.strip(" \u00b7"), shot=shot, extra=extra, geo=geo, date=date)


def load_pixels(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in RAW_EXT:
        if rawpy is None:
            raise RuntimeError("rawpy not installed - needed for RAW files")
        with rawpy.imread(path) as raw:
            rgb = raw.postprocess(use_camera_wb=True, no_auto_bright=False, output_bps=8)
        return Image.fromarray(rgb)
    im = Image.open(path)
    return ImageOps.exif_transpose(im)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", help="Folder containing your photos")
    ap.add_argument("--title", default=None)
    ap.add_argument("--place", default="")
    ap.add_argument("--format", choices=["avif", "webp"], default="avif")
    ap.add_argument("--quality", type=int, default=None)
    ap.add_argument("--max", type=int, default=2000)
    ap.add_argument("--out", default=".")
    ap.add_argument("--sort", choices=["date", "name"], default="date")
    ap.add_argument("--round-gps", action="store_true",
                    help="fuzz GPS to ~11 km in the output for privacy (labels/map still work)")
    args = ap.parse_args()

    if args.format == "avif" and pillow_avif is None:
        sys.exit("AVIF support missing.  Run:  pip install pillow-avif-plugin")
    quality = args.quality if args.quality is not None else (60 if args.format == "avif" else 82)
    title = args.title or os.path.basename(os.path.abspath(args.folder))
    slug = slugify(title)
    ext_out = ".avif" if args.format == "avif" else ".webp"
    fmt_pil = "AVIF" if args.format == "avif" else "WEBP"

    files = [os.path.join(args.folder, f) for f in os.listdir(args.folder)
             if os.path.splitext(f)[1].lower() in IMG_EXT]
    if not files:
        sys.exit(f"No images found in {args.folder}")

    # read EXIF first so we can sort chronologically
    items = []
    for p in files:
        ex = read_exif(p)
        items.append((p, ex, build_fields(ex)))
    if args.sort == "date":
        items.sort(key=lambda it: (it[2]["date"] or "9999", os.path.basename(it[0])))
    else:
        items.sort(key=lambda it: os.path.basename(it[0]).lower())

    # reverse-geocode GPS -> "City, Country" (needs the reverse_geocoder package)
    def parse_latlon(g):
        try:
            a, b = [float(x) for x in g.split(",")]
            return (a, b)
        except Exception:
            return None
    if args.round_gps:
        for it in items:
            ll = parse_latlon(it[2]["geo"])
            if ll:
                it[2]["geo"] = f"{ll[0]:.1f}, {ll[1]:.1f}"
    labels = geocode_labels([parse_latlon(it[2]["geo"]) for it in items])
    for it, lab in zip(items, labels):
        it[2]["loc"] = lab
    if _rg is None and any(it[2]["geo"] for it in items):
        print("  (tip: `pip install reverse_geocoder` to auto-add place names to the map)")

    outdir = os.path.join(args.out, "images", slug)
    os.makedirs(outdir, exist_ok=True)

    lines, total = [], 0
    for i, (p, ex, fields) in enumerate(items, 1):
        im = load_pixels(p).convert("RGB")
        ow, oh = im.size
        im.thumbnail((args.max, args.max))
        out = os.path.join(outdir, f"{i:02d}{ext_out}")
        save_kw = {"quality": quality}
        if fmt_pil == "WEBP":
            save_kw["method"] = 6
        im.save(out, fmt_pil, **save_kw)
        total += os.path.getsize(out)
        dims = f"{ow} \u00d7 {oh} \u00b7 {round(ow*oh/1e6)} MP"

        name = jsq(os.path.splitext(os.path.basename(p))[0])   # placeholder = filename; edit later
        place = jsq(args.place)
        parts = [f'name:"{name}"', f'place:"{place}"', f'date:"{fields["date"]}"']
        for k in ("gear", "shot", "extra"):
            if fields[k]:
                parts.append(f'{k}:"{jsq(fields[k])}"')
        parts.append(f'dims:"{dims}"')
        if fields["geo"]:
            parts.append(f'geo:"{fields["geo"]}"')
            if fields.get("loc"):
                parts.append(f'loc:"{jsq(fields["loc"])}"')
        parts.append(f'src:"images/{slug}/{i:02d}{ext_out}"')
        lines.append("      { " + ", ".join(parts) + " },")
        print(f"  [{i:>3}/{len(items)}] {os.path.basename(p):32.32}  ->  {i:02d}{ext_out}  "
              f"{os.path.getsize(out)//1024} KB")

    block = (f'  {{\n    title:"{jsq(title)}",\n    place:"{jsq(args.place)}",\n'
             f'    cover:"images/{slug}/01{ext_out}",\n    photos:[\n'
             + "\n".join(lines) + "\n    ]\n  },")

    txt = os.path.join(args.out, f"{slug}_album.txt")
    with open(txt, "w", encoding="utf-8") as f:
        f.write(block + "\n")

    print("\n" + "=" * 64)
    print(f"Converted {len(items)} photos  ({round(total/1024/1024, 1)} MB total)")
    print(f"Images:      {outdir}")
    print(f"Album code:  {txt}   (also printed below)")
    print("=" * 64 + "\n")
    print(block)
    print("\nNEXT: paste the block above into index.html between the lines")
    print('      "YOUR ALBUMS GO HERE" and the "// ADD YOUR OWN ALBUM" comment,')
    print("      edit the name/place fields, and upload the new images folder.")


if __name__ == "__main__":
    main()
