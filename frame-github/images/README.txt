images/  —  where your photo files live
=======================================

Organize one FOLDER PER ALBUM inside here. For example:

  images/
    summer-2026-example/     <- a ready-made example (safe to delete)
      dock.jpg
      canoe.jpg
      trail.jpg
    iceland-trip/            <- your own album, e.g.
      glacier.jpg
      waterfall.jpg

Then, in index.html, point each photo's  src:  at its path, e.g.
  src:"images/iceland-trip/glacier.jpg"

Tips:
- Any common image type works (.jpg, .jpeg, .png).
- Big photos load slowly. Resizing so the longest side is ~1600px is plenty.
- File names can't have spaces — use dashes:  north-shore.jpg  (not "north shore.jpg").

Note: the four built-in albums (Wildlife, Big Cats, Birds & Reptiles, Cold
Climates) are stored inside index.html itself, so they don't need this folder.
This folder is for the NEW albums you add.
