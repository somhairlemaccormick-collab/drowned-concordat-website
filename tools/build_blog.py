#!/usr/bin/env python3
"""Build the Dispatches blog for thedrownedconcordat.com.

Reads every post in posts/*.md and writes static HTML into dispatches/:
  dispatches/index.html       the list of posts, newest first
  dispatches/<slug>.html      one page per post (served at /dispatches/<slug>)
  dispatches/feed.xml         an RSS feed

Netlify has no build step for this site, so run this script and commit the
generated files:   python3 tools/build_blog.py

Post format (posts/2026-10-27-some-slug.md):

    ---
    title: The wall is a system
    date: 2026-10-27
    summary: One or two sentences for the list page and link previews.
    image: /images/world/bulwark-storm.jpg
    image_alt: Storm waves breaking against a sea wall
    sources:
      - Outlet name | Article title | https://example.com/article
    ---
    Markdown body...

The slug is the file name without the date prefix. Posts dated in the future
are skipped, so a draft can sit in posts/ until its day.
"""
import datetime as dt
import html
import pathlib
import re
import sys

try:
    import markdown
except ImportError:  # pragma: no cover
    sys.exit("Missing the 'markdown' package: pip install markdown")

ROOT = pathlib.Path(__file__).resolve().parent.parent
POSTS = ROOT / "posts"
OUT = ROOT / "dispatches"
SITE = "https://thedrownedconcordat.com"
AMAZON = "https://www.amazon.com/dp/B0HJLRN48X"


def parse(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        sys.exit(f"{path.name}: missing --- front matter ---")
    meta, body = {}, m.group(2)
    key = None
    for line in m.group(1).splitlines():
        if re.match(r"^\s+-\s+", line) and key:
            meta.setdefault(key, []).append(re.sub(r"^\s+-\s+", "", line).strip())
        elif ":" in line:
            key, val = line.split(":", 1)
            key, val = key.strip(), val.strip()
            meta[key] = val if val else []
    for req in ("title", "date", "summary"):
        if not meta.get(req):
            sys.exit(f"{path.name}: front matter needs '{req}'")
    meta["date"] = dt.date.fromisoformat(meta["date"])
    meta["slug"] = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.stem)
    meta["html"] = markdown.markdown(body, extensions=["smarty"])
    meta.setdefault("image", "/images/world/bulwark-storm.jpg")
    meta.setdefault("image_alt", "")
    srcs = []
    for s in meta.get("sources") or []:
        parts = [p.strip() for p in s.split("|")]
        if len(parts) == 3:
            srcs.append(parts)
    meta["sources"] = srcs
    return meta


def nice_date(d):
    return f"{d.day} {d.strftime('%B %Y')}"


CSS = """
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400&family=Space+Grotesk:wght@300;400;500;600&display=swap');
* { margin: 0; padding: 0; box-sizing: border-box; }
:root {
  --bg-deep: #05060a; --bg-panel: #0b0e16; --line: rgba(255,255,255,0.08);
  --text-main: #e8e6df; --text-dim: #8b8f9c; --accent: #7fd8ff;
  --accent-warm: #d9a86c; --accent-glow: rgba(127, 216, 255, 0.35);
}
html { scroll-behavior: smooth; }
body { background: var(--bg-deep); color: var(--text-main); font-family: 'Space Grotesk', sans-serif; overflow-x: hidden; position: relative; }
.stars { position: fixed; inset: 0; pointer-events: none; z-index: 0; opacity: 0.45;
  background-image: radial-gradient(1px 1px at 20px 30px, #fff, transparent), radial-gradient(1px 1px at 140px 80px, #fff, transparent),
  radial-gradient(1.5px 1.5px at 300px 150px, #fff, transparent), radial-gradient(1px 1px at 520px 220px, #fff, transparent),
  radial-gradient(1.5px 1.5px at 640px 40px, #fff, transparent), radial-gradient(1px 1px at 880px 100px, #fff, transparent),
  radial-gradient(1px 1px at 1000px 300px, #fff, transparent);
  background-size: 1100px 500px; }
.glow-orb { position: fixed; border-radius: 50%; filter: blur(90px); z-index: 0; pointer-events: none;
  width: 480px; height: 480px; background: var(--accent-glow); top: -160px; right: -120px; opacity: 0.7; }
header, main, footer { position: relative; z-index: 1; }
header { display: flex; justify-content: space-between; align-items: center; padding: 32px 6vw; border-bottom: 1px solid var(--line); }
.pen-name { font-family: 'Cormorant Garamond', serif; font-style: italic; font-size: 1rem; letter-spacing: 0.08em; color: var(--text-dim); text-decoration: none; }
nav a { color: var(--text-dim); text-decoration: none; font-size: 0.85rem; letter-spacing: 0.12em; text-transform: uppercase; margin-left: 36px; transition: color 0.25s ease; }
nav a:hover, nav a[aria-current] { color: var(--accent); }
nav a.nav-buy { color: var(--accent); }
nav a { white-space: nowrap; }
@media (max-width: 1400px) and (min-width: 801px) { nav a { margin-left: 22px; font-size: 0.8rem; } }
@media (max-width: 1200px) and (min-width: 801px) { nav { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 8px 20px; } nav a { margin-left: 0; } }
.section-tag { font-size: 0.78rem; letter-spacing: 0.3em; text-transform: uppercase; color: var(--accent-warm); margin-bottom: 18px; }
.page-head { text-align: center; padding: 110px 6vw 60px; max-width: 760px; margin: 0 auto; }
.page-head h1 { font-family: 'Cormorant Garamond', serif; font-weight: 500; font-size: clamp(3rem, 8vw, 5.8rem); line-height: 0.95;
  background: linear-gradient(180deg, #ffffff 0%, #b9c2cf 60%, #6f7889 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }
.page-head p { margin-top: 24px; color: var(--text-dim); font-weight: 300; line-height: 1.7; font-size: clamp(1rem, 1.5vw, 1.15rem); }
.page-head em { color: var(--accent-warm); font-style: italic; }
.feed-link { display: inline-block; margin-top: 22px; font-size: 0.72rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--accent); text-decoration: none; }
.feed-link:hover { text-decoration: underline; }

.post-list { max-width: 960px; margin: 0 auto; padding: 0 6vw 120px; display: grid; gap: 28px; }
.post-card { display: grid; grid-template-columns: 300px 1fr; background: linear-gradient(160deg, var(--bg-panel), #05060a);
  border: 1px solid var(--line); border-radius: 4px; overflow: hidden; text-decoration: none; color: inherit;
  transition: transform 0.35s ease, border-color 0.35s ease; }
.post-card:hover { transform: translateY(-6px); border-color: rgba(127,216,255,0.4); }
.post-card img { width: 100%; height: 100%; min-height: 200px; object-fit: cover; display: block; }
.post-card .body { padding: 28px 30px; }
.post-card time, .post-meta time { font-size: 0.72rem; letter-spacing: 0.16em; text-transform: uppercase; color: var(--accent); }
.post-card h2 { font-family: 'Cormorant Garamond', serif; font-weight: 500; font-size: 1.8rem; line-height: 1.15; margin-top: 10px; }
.post-card p { margin-top: 12px; color: var(--text-dim); font-weight: 300; line-height: 1.65; font-size: 0.95rem; }
.post-card .more { margin-top: 16px; display: inline-block; font-size: 0.75rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--accent-warm); }
.empty { text-align: center; color: var(--text-dim); padding: 40px 0 120px; font-style: italic; }

article.post { max-width: 720px; margin: 0 auto; padding: 100px 6vw 40px; }
.post-meta { text-align: center; }
article.post h1 { font-family: 'Cormorant Garamond', serif; font-weight: 500; font-size: clamp(2.4rem, 6vw, 4rem); line-height: 1.05; text-align: center; margin-top: 16px; }
.post-dek { text-align: center; margin: 22px auto 0; color: var(--text-dim); font-weight: 300; line-height: 1.7; font-size: 1.08rem; max-width: 600px; }
.post-hero { margin: 50px 0 46px; border: 1px solid var(--line); border-radius: 4px; overflow: hidden; box-shadow: 0 30px 80px rgba(0,0,0,0.55), 0 0 60px rgba(127,216,255,0.06); }
.post-hero img { display: block; width: 100%; height: auto; max-height: 460px; object-fit: cover; }
.prose p, .prose li { color: #c9c8c2; line-height: 1.85; font-weight: 300; font-size: 1.04rem; }
.prose p { margin-bottom: 20px; }
.prose h2 { font-family: 'Cormorant Garamond', serif; font-weight: 500; font-size: 1.9rem; line-height: 1.15; margin: 48px 0 16px; color: var(--text-main); }
.prose h3 { font-size: 0.8rem; letter-spacing: 0.24em; text-transform: uppercase; color: var(--accent-warm); margin: 40px 0 12px; font-weight: 500; }
.prose a { color: var(--accent); text-decoration: none; border-bottom: 1px solid rgba(127,216,255,0.35); }
.prose a:hover { border-bottom-color: var(--accent); }
.prose strong { color: var(--text-main); font-weight: 500; }
.prose em { color: var(--accent-warm); }
.prose ul, .prose ol { margin: 0 0 20px 22px; }
.prose blockquote { border-left: 2px solid var(--accent); padding: 4px 0 4px 22px; margin: 28px 0; font-family: 'Cormorant Garamond', serif; font-size: 1.35rem; font-style: italic; color: var(--text-main); }
.prose blockquote p { font-size: inherit; color: inherit; margin: 0; }
.prose hr { border: 0; border-top: 1px solid var(--line); margin: 44px 0; }
.sources { margin-top: 54px; padding-top: 28px; border-top: 1px solid var(--line); }
.sources h2 { font-size: 0.75rem; letter-spacing: 0.24em; text-transform: uppercase; color: var(--text-dim); font-weight: 500; margin-bottom: 14px; }
.sources ol { margin-left: 20px; }
.sources li { color: var(--text-dim); font-size: 0.88rem; line-height: 1.6; margin-bottom: 8px; font-weight: 300; }
.sources a { color: var(--accent); text-decoration: none; }
.sources a:hover { text-decoration: underline; }
.post-cta { max-width: 720px; margin: 0 auto 110px; padding: 40px 6vw 0; text-align: center; }
.post-cta p { color: var(--text-dim); font-weight: 300; line-height: 1.7; }
.post-cta em { color: var(--accent-warm); }
.cta-row { margin-top: 26px; display: flex; flex-wrap: wrap; gap: 16px; justify-content: center; }
.btn { padding: 14px 30px; border-radius: 2px; font-size: 0.78rem; letter-spacing: 0.14em; text-transform: uppercase; text-decoration: none; transition: all 0.3s ease; display: inline-block; }
.btn-primary { background: var(--accent); color: #05060a; font-weight: 600; box-shadow: 0 0 30px var(--accent-glow); }
.btn-primary:hover { transform: translateY(-2px); }
.btn-ghost { border: 1px solid var(--line); color: var(--text-main); }
.btn-ghost:hover { border-color: var(--accent); color: var(--accent); }

footer { padding: 60px 6vw 40px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px; border-top: 1px solid var(--line); }
.footer-mark { font-family: 'Cormorant Garamond', serif; font-style: italic; color: var(--text-dim); font-size: 0.9rem; }
.socials { display: flex; gap: 22px; }
.socials a { color: var(--text-dim); text-decoration: none; font-size: 0.78rem; letter-spacing: 0.1em; text-transform: uppercase; }
.socials a:hover { color: var(--accent); }

@media (max-width: 800px) {
  header { flex-wrap: wrap; gap: 14px; }
  nav { display: flex; flex-wrap: wrap; gap: 10px 18px; }
  nav a { margin-left: 0; }
  .post-card { grid-template-columns: 1fr; }
  .post-card img { min-height: 0; aspect-ratio: 16/9; height: auto; }
  .post-card .body { padding: 22px 22px 26px; }
  article.post { padding-top: 70px; }
}
"""

NAV = """  <header>
    <a class="pen-name" href="/">Hamish C. Rannoch</a>
    <nav>
      <a href="/">Home</a>
      <a href="/books">The Series</a>
      <a href="/books#novellas">Novellas</a>
      <a href="/cast">Cast &amp; Factions</a>
      <a href="/world">The World</a>
      <a href="/dispatches/" aria-current="page">Dispatches</a>
      <a href="/#about">About</a>
      <a class="nav-buy" href="{amazon}" target="_blank" rel="noopener">Buy Book One</a>
    </nav>
  </header>""".format(amazon=AMAZON)

FOOTER = """  <footer>
    <div class="footer-mark">Hamish C. Rannoch — The Drowned Concordat</div>
    <div class="socials">
      <a href="/dispatches/feed.xml">RSS</a>
      <a href="https://www.instagram.com/hamish.c.rannoch/" target="_blank" rel="noopener">Instagram</a>
      <a href="https://www.tiktok.com/@hamish.c.rannoch" target="_blank" rel="noopener">TikTok</a>
      <a href="mailto:hamish.c.rannoch@gmail.com">Contact</a>
    </div>
  </footer>"""


def page(title, description, url, image, body):
    e = html.escape
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{SITE}{url}">
<link rel="alternate" type="application/rss+xml" title="Dispatches — The Drowned Concordat" href="/dispatches/feed.xml">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:image" content="{SITE}{image}">
<meta property="og:url" content="{SITE}{url}">
<meta property="og:type" content="article">
<meta name="twitter:card" content="summary_large_image">
<style>{CSS}</style>
</head>
<body>
  <div class="stars"></div><div class="glow-orb"></div>
{NAV}
  <main>
{body}
  </main>
{FOOTER}
</body>
</html>
"""


def build():
    today = dt.date.today()
    posts = [parse(p) for p in sorted(POSTS.glob("*.md"))]
    posts = [p for p in posts if p["date"] <= today]
    posts.sort(key=lambda p: (p["date"], p["slug"]), reverse=True)
    OUT.mkdir(exist_ok=True)
    e = html.escape

    # Remove pages for posts that no longer exist.
    keep = {f"{p['slug']}.html" for p in posts} | {"index.html", "feed.xml"}
    for f in OUT.glob("*"):
        if f.name not in keep:
            f.unlink()

    for p in posts:
        srcs = ""
        if p["sources"]:
            items = "\n".join(
                f'          <li>{e(o)}: <a href="{e(u)}" target="_blank" rel="noopener">{e(t)}</a></li>'
                for o, t, u in p["sources"]
            )
            srcs = f"""      <aside class="sources">
        <h2>Sources</h2>
        <ol>
{items}
        </ol>
      </aside>"""
        body = f"""    <article class="post">
      <div class="post-meta"><div class="section-tag">Dispatch</div><time datetime="{p['date'].isoformat()}">{nice_date(p['date'])}</time></div>
      <h1>{e(p['title'])}</h1>
      <p class="post-dek">{e(p['summary'])}</p>
      <figure class="post-hero"><img src="{e(p['image'])}" alt="{e(p['image_alt'])}" width="1280" height="720"></figure>
      <div class="prose">
{p['html']}
      </div>
{srcs}
    </article>
    <section class="post-cta">
      <p>The world behind the wall is fiction. <em>The Rise of the Covenant</em>, Book One of The Drowned Concordat, is out now on Kindle.</p>
      <div class="cta-row">
        <a class="btn btn-primary" href="{AMAZON}" target="_blank" rel="noopener">Buy Book One</a>
        <a class="btn btn-ghost" href="/dispatches/">More Dispatches</a>
      </div>
    </section>"""
        (OUT / f"{p['slug']}.html").write_text(
            page(f"{p['title']} — Dispatches", p["summary"], f"/dispatches/{p['slug']}", p["image"], body),
            encoding="utf-8",
        )

    if posts:
        cards = "\n".join(
            f"""      <a class="post-card" href="/dispatches/{p['slug']}">
        <img src="{e(p['image'])}" alt="{e(p['image_alt'])}" loading="lazy" width="640" height="360">
        <div class="body">
          <time datetime="{p['date'].isoformat()}">{nice_date(p['date'])}</time>
          <h2>{e(p['title'])}</h2>
          <p>{e(p['summary'])}</p>
          <span class="more">Read the dispatch →</span>
        </div>
      </a>"""
            for p in posts
        )
        listing = f'    <div class="post-list">\n{cards}\n    </div>'
    else:
        listing = '    <p class="empty">The first dispatch is on its way.</p>'
    index_body = f"""    <section class="page-head">
      <div class="section-tag">Dispatches</div>
      <h1>News from Above the Waterline</h1>
      <p>Every week, the real-world stories that sound like they came from behind the wall: rising seas, the defences built against them, and the future of what we eat.</p>
      <a class="feed-link" href="/dispatches/feed.xml">Follow by RSS</a>
    </section>
{listing}"""
    (OUT / "index.html").write_text(
        page(
            "Dispatches — The Drowned Concordat",
            "Weekly real-world news on rising seas, flood defences and the future of food, from the author of The Drowned Concordat.",
            "/dispatches/",
            "/images/world/bulwark-coast.jpg",
            index_body,
        ),
        encoding="utf-8",
    )

    items = "\n".join(
        f"""    <item>
      <title>{e(p['title'])}</title>
      <link>{SITE}/dispatches/{p['slug']}</link>
      <guid>{SITE}/dispatches/{p['slug']}</guid>
      <pubDate>{dt.datetime.combine(p['date'], dt.time(9)).strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>
      <description>{e(p['summary'])}</description>
    </item>"""
        for p in posts[:20]
    )
    (OUT / "feed.xml").write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Dispatches — The Drowned Concordat</title>
    <link>{SITE}/dispatches/</link>
    <description>Weekly real-world news on rising seas, flood defences and the future of food, from Hamish C. Rannoch.</description>
    <language>en</language>
{items}
  </channel>
</rss>
""",
        encoding="utf-8",
    )
    print(f"Built {len(posts)} post(s) into {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    build()
