# Frame — your photo album site

Everything lives in one file: **`index.html`**. To change anything, open that
file in any text editor (Notepad, TextEdit, or edit it right on GitHub with the
pencil ✏️ icon), make your change, and save. Nothing needs to be built.

> **Before you edit:** keep a copy of `index.html` somewhere safe. If a change
> ever breaks the page, you can just put the old copy back.

---

## 1. Put it online (GitHub Pages)

1. On GitHub, click **New** to create a repository. Name it something like
   `photos`, set it to **Public**, and click **Create repository**.
2. Click **Add file → Upload files**, drag in `index.html`, then **Commit changes**.
   The file must be named exactly `index.html`.
3. Go to the repo's **Settings → Pages**. Under *Build and deployment*, set
   **Source = Deploy from a branch**, branch **main**, folder **/ (root)**, and **Save**.
4. Wait a minute, refresh, and your live link appears:
   `https://YOUR-USERNAME.github.io/photos/`

To update the site later, repeat step 2 (upload the new `index.html`; it will
offer to replace the old one).

---

## 2. Change the main titles and text

Open `index.html` and look near the top of the page section (around line 109):

| What you see on the page        | Find this line              | Change the text between the tags |
|---------------------------------|-----------------------------|----------------------------------|
| The big title **Frame**         | `<h1>Frame</h1>`            | `<h1>My Photos</h1>`             |
| The intro sentence under it     | `<p class="lede">A collection of photo albums…</p>` | Write your own sentence |
| The year in **Updated 2026**    | `<span>Updated <b>2026</b></span>` | Change `2026` |
| The footer (bottom of page)     | `<span>Frame — built with GitHub Pages</span>` and the line under it | Write your own |

The small label above the title (**Photo Albums** / **Album**) is set in the
script lower down. To change it, find these two lines and edit the words in quotes:

```js
document.getElementById("eyebrow").textContent = "Photo Albums";   // shown on the album list
document.getElementById("eyebrow").textContent = "Album";          // shown inside an album
```

---

## 3. Change a photo's name, location, or date

Scroll to the section marked **`YOUR ALBUMS GO HERE`**. Each photo is one entry
that looks like this:

```js
{ name:"White tiger", place:"Toronto Zoo, ON", date:"2025-08-12",
  src:"data:image/jpeg;base64,......" },
```

Edit the text inside the quotes for `name`, `place`, and `date`. Leave `src`
alone — that is the photo itself. Dates are written `YYYY-MM-DD` (e.g.
`2026-07-01`) and get formatted automatically (like *Jul 01, 2026*).

---

## 4. Add more photos to an album

1. Make a folder called **`images`** in the repo, next to `index.html`
   (Add file → Upload files lets you drag a whole folder in).
2. Put your photo files in it, e.g. `images/beach.jpg`.
3. In the album's `photos:[ ... ]` list, add a line for each new photo:

```js
{ name:"Beach at sunset", place:"Tofino, BC", date:"2026-08-01", src:"images/beach.jpg" },
```

Keep the comma at the end of each line. The photos show in the order you list them.

> The existing **Wildlife** photos are stored inside `index.html` itself, so they
> already work. New photos you add use the `images/` folder instead — that is the
> normal, simpler way. Both work side by side.

---

## 5. Add a whole new album

In the same `YOUR ALBUMS GO HERE` section, add a new block **after** the Wildlife
one (there is already a commented-out example in the file you can copy):

```js
{
  title:"Summer 2026",
  place:"Muskoka, ON",
  photos:[
    { name:"Dock at dawn", place:"Muskoka, ON", date:"2026-07-01", src:"images/summer/dock.jpg" },
    { name:"Canoe",        place:"Muskoka, ON", date:"2026-07-02", src:"images/summer/canoe.jpg" },
  ]
},
```

- `title` and `place` show on the album's cover card.
- The **first photo** in the list becomes the album's cover automatically.
  (To pick a different cover, add `cover:"images/summer/dock.jpg"` under `place`.)
- Put that album's photos in their own folder, e.g. `images/summer/`.

---

## Three small things that prevent 99% of mistakes

1. **Keep the commas.** Every photo line and every album block ends with a comma.
2. **Use straight quotes** `"like this"`, not curly quotes `“like this”`. Some
   word processors auto-change them — a plain text editor won't.
3. **Don't touch the `src:"data:image..."` values** on the Wildlife photos; they
   are the images themselves and are meant to be long.

If the page ever looks blank after an edit, undo your last change (or restore your
backup copy) — it's almost always a missing comma or a curly quote.
