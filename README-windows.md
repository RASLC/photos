# Photo → AVIF + album code (Windows)

`build_album.py` converts a folder of photos to **AVIF** and prints the **album
code** to paste into your site's `index.html`. It reads each photo's EXIF
(camera, lens, aperture, shutter, ISO, date, GPS) and fills those fields in for
you. It handles Sony **.ARW** RAW files as well as `.jpg / .jpeg / .png / .tif`.

---

## One-time setup

1. **Install Python.** Get it from https://www.python.org/downloads/ and, on the
   first screen of the installer, **tick "Add python.exe to PATH"**, then Install.
2. **Install the packages.** Open **Command Prompt** (press Start, type `cmd`,
   Enter) and run:

   ```
   pip install pillow pillow-avif-plugin rawpy exifread reverse_geocoder
   ```

   That's everything — the AVIF encoder, the RAW decoder, and the offline
   place-name lookup all come bundled in those packages, no extra downloads.
   (`reverse_geocoder` is optional; without it everything still works, you just
   won't get automatic place names on the map.)

3. Put `build_album.py` somewhere easy, e.g. `C:\photos\build_album.py`.

---

## Converting a batch

Open Command Prompt and run (quote paths that contain spaces):

```
python C:\photos\build_album.py "C:\photos\japan-dec-2024" --title "Japan 2024" --place "Osaka"
```

What happens:
- It reads every photo in that folder, converts each to AVIF, and sorts them by
  the date they were taken.
- It creates `images\japan-2024\01.avif, 02.avif, …` next to where you ran it.
- It writes `japan-2024_album.txt` — the album code — and prints it in the window.

### Options

| Option | What it does | Default |
|--------|--------------|---------|
| `--title "..."`  | Album title (also names the folder) | the source folder's name |
| `--place "..."`  | Default location for the album + each photo | blank |
| `--format`       | `avif` or `webp` | `avif` |
| `--quality`      | 0–100 (lower = smaller file) | 60 (avif) / 82 (webp) |
| `--max`          | longest edge in pixels | 2000 |
| `--out "..."`    | folder that contains your `images` folder (your site folder) | current folder |
| `--sort`         | `date` (chronological) or `name` | `date` |
| `--round-gps`    | fuzz GPS to ~11 km in the output for privacy | off (full precision) |

When a photo has GPS, the tool looks up the nearest place offline and adds a
`loc:"City, Country"` field (e.g. `loc:"Portofino, Italy"`) — that's what shows as
the label on the map. GPS is written at full precision by default so the map dot and
its Google-Maps link are accurate; add `--round-gps` if you'd rather blur the exact
spot (the place label and regional map still work either way).

Example writing straight into your site folder:

```
python build_album.py "D:\raw\dolomites" --title "Dolomites 2025" --place "Italy" --out "C:\my-site" --quality 55
```

---

## Adding it to the site

1. Open `index.html` in a text editor (Notepad works; Notepad++ or VS Code are nicer).
2. Find the line **`YOUR ALBUMS GO HERE`**. Just below it your albums are listed.
3. Open the generated `..._album.txt`, copy everything in it, and paste it in as a
   new album — right after an existing album's closing `},` and before the
   `// ADD YOUR OWN ALBUM` comment.
4. **Edit the `name:` fields.** They default to the file name (e.g. `A7R00312`);
   change them to real titles like `"Peak in the clouds"`. Tweak `place:` per photo
   if you like. Everything else (camera, settings, date, map dot) is already filled.
5. Save `index.html`, then upload **both** the changed `index.html` **and** the new
   `images\<album>\` folder to GitHub / Cloudflare.

That's it — the new album shows up automatically.

---

## Notes

- **5 GB at a time is fine.** It processes one photo at a time, so it won't run out
  of memory. RAW (.ARW) is the slow part — expect it to chew through a big RAW batch
  over some minutes; JPEGs fly.
- **Privacy:** the AVIF/WebP files themselves contain **no** EXIF, so your originals'
  timestamps and camera metadata never end up in the published files. GPS coordinates
  *are* written into `index.html` at full precision so the map is accurate — if you'd
  rather not publish exact spots, run with `--round-gps` to blur them to ~11 km.
- **Missing data is skipped.** If a photo has no EXIF (e.g. a re-exported JPEG), the
  camera/settings lines are simply left out for that photo — no errors.
- **Cover photo** = the first photo in the album. To pick a different one, edit the
  `cover:` line to point at any file, e.g. `cover:"images/japan-2024/05.avif"`.
- **Re-running** the same folder overwrites the numbered files, so it's safe to redo.

### If something goes wrong
- `pip is not recognized` → Python wasn't added to PATH; re-run the installer and
  tick that box, or use `py -m pip install ...`.
- `AVIF support missing` → run `pip install pillow-avif-plugin`.
- `rawpy not installed` → run `pip install rawpy` (only needed for RAW files).
