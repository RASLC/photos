# Archive — your photo album site

Everything lives in **`index.html`**, plus an **`images/`** folder for the photos
in any albums you add. Edit `index.html` in any text editor (or on GitHub with the
pencil icon) and save. Nothing needs to be built.

**What's included:** four built-in albums so you can see it working — *Wildlife*,
*Big Cats*, *Birds & Reptiles*, and *Cold Climates*. Their photos are stored inside
`index.html`, so they work the moment the site is live. Rename or delete any of them
once you've had a look.

> Before you edit: keep a spare copy of `index.html`. If an edit ever breaks the
> page, put the copy back.

---

## 1. Put it online (GitHub Pages)

1. On GitHub, click New to create a repository. Name it e.g. `photos`, set it
   Public, and Create repository.
2. Click Add file -> Upload files, drag in `index.html` AND the whole `images`
   folder, then Commit changes. `index.html` must keep that exact name.
3. Repo Settings -> Pages -> Source "Deploy from a branch" -> branch main,
   folder / (root) -> Save.
4. Wait a minute, refresh, and your link appears: https://YOUR-USERNAME.github.io/photos/

Update later by uploading the changed files again (it offers to replace them).

---

## 2. Change the front-page wording

Open `index.html` and find the block that starts with FRONT-PAGE WORDING. It's one
tidy list -- just edit the text inside the quotes:

    const SITE = {
      eyebrow: "Photographs · 2025-2026",   // small line above the big title
      title:   "Archive",                    // the big title
      intro:   "Animals, mostly ...",        // the sentence under it
      footerLeft:  "Archive",                // bottom-left of the page
      footerRight: "Toronto · 2025-2026"     // bottom-right of the page
    };

That's the only place you need to touch for the main text.

---

## 3. How the images folder is organized

Keep ONE FOLDER PER ALBUM inside `images/`:

    images/
      summer-2026-example/     <- a ready-made example (delete it whenever)
        dock.jpg
        canoe.jpg
        trail.jpg
      iceland-trip/            <- your own album
        glacier.jpg
        waterfall.jpg

File names can't contain spaces -- use dashes (north-shore.jpg). Any of .jpg /
.jpeg / .png work. Resizing photos so the long side is ~1600px keeps the site fast.

---

## 4. Add a new album

There's a ready example folder, `images/summer-2026-example/`, with three placeholder
photos, and a matching commented-out album in `index.html`. To turn it on: find the
"ADD YOUR OWN ALBUM" section and delete the // in front of each line of the example
block. Save -- a new album appears at the bottom of the list.

To make your own from scratch:

1. Create a folder, e.g. `images/iceland-trip/`, and put the photos in.
2. In the "YOUR ALBUMS GO HERE" list, add a block like this:

    {
      title:"Iceland 2026",
      place:"Reykjavik",
      photos:[
        { name:"Glacier",   place:"Vatnajokull", date:"2026-02-10", src:"images/iceland-trip/glacier.jpg" },
        { name:"Waterfall", place:"Skogafoss",   date:"2026-02-11", src:"images/iceland-trip/waterfall.jpg" },
      ]
    },

- title and place show on the album's full-width cover.
- The FIRST photo becomes the cover automatically (or add
  cover:"images/iceland-trip/glacier.jpg" under place to choose one).
- The big photo at the top of the front page uses the FOURTH photo of the first
  album; change which album is listed first to change that hero image.

---

## 5. Add more photos to an album

Drop the file into that album's folder, then add one line to its photos:[ ... ] list:

    { name:"Black sand beach", place:"Vik", date:"2026-02-12", src:"images/iceland-trip/beach.jpg" },

Photos appear in the order they're listed, and fade in as you scroll. Keep the comma
at the end of the line.

---

## Three things that prevent almost every mistake

1. Keep the commas -- every photo line and every album block ends with one.
2. Use straight quotes "like this", never curly quotes.
3. Don't edit the src:"data:image..." values on the built-in albums -- those long
   strings ARE the photos.

If the page goes blank after an edit, undo it (or restore your backup) -- it's almost
always a missing comma or a curly quote.
