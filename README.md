# thedrownedconcordat.com

The website for *The Drowned Concordat* by Hamish C. Rannoch.

Plain HTML, no build step. Netlify publishes this folder as-is; every push to `main` goes live.
Pages are served without `.html` (Netlify "pretty URLs"), so `world.html` is at `/world`.

- `index.html` – home and about
- `books.html` – the series and novellas
- `cast.html` – cast and factions (spoiler-free)
- `world.html` – world guide (spoiler-free)
- `images/world/` – art for the world guide
- `posts/` – Dispatches blog posts, one Markdown file each (`YYYY-MM-DD-slug.md`)
- `dispatches/` – generated blog pages and RSS feed (don't edit by hand)
- `tools/build_blog.py` – turns `posts/` into `dispatches/`

## Adding a Dispatch

1. Add `posts/YYYY-MM-DD-slug.md` (see the front-matter format at the top of `tools/build_blog.py`).
2. Run `python3 tools/build_blog.py` (needs `pip install markdown`).
3. Commit both the post and the regenerated `dispatches/` folder.

Weekly drafts arrive on a `dispatch/YYYY-MM-DD` branch as a pull request. Merging it publishes the post.

House rules for Dispatches: real news, paraphrased and linked; spoiler-free (nothing past Book One's opening premise); only promote Book One; never mention Business Time.

## Search engines

- Each main page has a description, social-sharing tags, a canonical address and (on Home and The Series)
  structured book data that Google reads.
- `sitemap.xml` is rebuilt by `python3 tools/build_blog.py`, so run that after adding a Dispatch or a page.
  New main pages need adding to `MAIN_PAGES` in that script.
- `robots.txt` points search engines at the sitemap.
