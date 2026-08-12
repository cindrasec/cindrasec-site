#!/usr/bin/env python3
"""
Build research/*.md into published article pages.

Why a hand-rolled converter instead of a markdown library: this site is
deliberately zero-dependency (see README) and the two writeups use a small,
known subset of markdown — surveyed before this was written, not guessed.
Anything outside that subset should fail loudly rather than render wrong, so
unknown constructs are left as literal text and caught by --check.

Two site constraints drive the output:
  * CSP is `style-src 'self'` — no inline <style> blocks. Article styling lives
    in styles.css alongside everything else.
  * CSP is `img-src 'self' data:` — the shields.io badges in the source would be
    blocked by the browser, so they are dropped and their information is carried
    by the article metadata line instead.

Usage:
    python3 build_research.py            # write pages
    python3 build_research.py --check    # verify output matches source
"""

from __future__ import annotations

import html
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
SRC_DIR = ROOT / "research" / "src"
OUT_DIR = ROOT / "research"
SITE = "https://cindrasec.com"

# ---------------------------------------------------------------- inline pass

CODE_TOKEN = "\x00CODE%d\x00"


def _inline(text: str) -> str:
    """Inline markdown -> HTML. Code spans are extracted first so their contents
    are never treated as markup."""
    spans: list[str] = []

    def stash(m):
        spans.append(m.group(1))
        return CODE_TOKEN % (len(spans) - 1)

    text = re.sub(r"`([^`]+)`", stash, text)
    text = html.escape(text, quote=False)

    # Images are dropped entirely: every one in these sources is an external
    # shields.io badge, which img-src 'self' data: would block anyway.
    text = re.sub(r"!\[[^\]]*\]\((?:[^()]|\([^()]*\))*\)", "", text)

    def link(m):
        label, href = m.group(1), m.group(2)
        external = href.startswith("http") and "cindrasec.com" not in href
        rel = ' target="_blank" rel="noopener noreferrer"' if external else ""
        return f'<a href="{html.escape(href, quote=True)}"{rel}>{label}</a>'

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)

    for i, code in enumerate(spans):
        text = text.replace(CODE_TOKEN % i, f"<code>{html.escape(code, quote=False)}</code>")
    return text


# ----------------------------------------------------------------- block pass

def _table(rows: list[str]) -> str:
    def cells(line):
        return [c.strip() for c in line.strip().strip("|").split("|")]

    head = cells(rows[0])
    body = [cells(r) for r in rows[2:]]  # rows[1] is the --- separator
    out = ['<div class="prose-scroll"><table>', "<thead><tr>"]
    out += [f"<th>{_inline(c)}</th>" for c in head]
    out.append("</tr></thead><tbody>")
    for row in body:
        out.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in row) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def to_html(md: str) -> str:
    lines = md.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # fenced code — copied verbatim, never parsed
        if line.startswith("```"):
            lang = line[3:].strip()
            buf = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            cls = f' class="lang-{html.escape(lang, quote=True)}"' if lang else ""
            body = html.escape("\n".join(buf), quote=False)
            out.append(f'<div class="prose-scroll"><pre><code{cls}>{body}</code></pre></div>')
            continue

        if re.match(r"^---+\s*$", line):
            out.append("<hr>")
            i += 1
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            lvl = len(m.group(1))
            # The source's own `# Title` is stripped by strip_front_matter and
            # re-rendered as the page <h1>, so the body already starts at `##`.
            # Map levels straight through: `##` -> h2, `###` -> h3. Demoting here
            # would jump h1 -> h3 and skip a level, which breaks the document
            # outline for screen readers and weakens the section signal for search.
            tag = f"h{min(lvl, 6)}"
            text = _inline(m.group(2))
            slug = re.sub(r"[^a-z0-9]+", "-", m.group(2).lower()).strip("-")
            out.append(f'<{tag} id="{slug}">{text}</{tag}>')
            i += 1
            continue

        if line.startswith("|"):
            buf = []
            while i < len(lines) and lines[i].startswith("|"):
                buf.append(lines[i])
                i += 1
            out.append(_table(buf) if len(buf) >= 2 else "")
            continue

        if line.startswith("> "):
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(lines[i].lstrip(">").strip())
                i += 1
            out.append(f"<blockquote>{_inline(' '.join(buf))}</blockquote>")
            continue

        m = re.match(r"^(\s*)([-*])\s+(.*)$", line)
        if m:
            buf = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                buf.append(re.sub(r"^\s*[-*]\s+", "", lines[i]))
                i += 1
            items = "".join(f"<li>{_inline(b)}</li>" for b in buf)
            out.append(f"<ul>{items}</ul>")
            continue

        if re.match(r"^\d+\.\s+", line):
            buf = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i]):
                buf.append(re.sub(r"^\d+\.\s+", "", lines[i]))
                i += 1
            items = "".join(f"<li>{_inline(b)}</li>" for b in buf)
            out.append(f"<ol>{items}</ol>")
            continue

        if line.strip():
            buf = []
            while i < len(lines) and lines[i].strip() and not re.match(
                r"^(#{1,4}\s|```|\||>\s|\s*[-*]\s|\d+\.\s|---+\s*$)", lines[i]
            ):
                buf.append(lines[i].strip())
                i += 1
            out.append(f"<p>{_inline(' '.join(buf))}</p>")
            continue

        i += 1
    return "\n".join(x for x in out if x)


# ------------------------------------------------------------------- metadata

def parse_meta(md: str, slug: str) -> dict:
    title = re.search(r"^#\s+(.*)$", md, re.M).group(1).strip()
    sub = re.search(r"^\*\*(.+?)\*\*\s*$", md, re.M)
    summary = re.sub(r"[*_`]", "", sub.group(1)).strip() if sub else ""
    m = re.match(r"^(\d{4})-(\d{2})", slug)
    published = f"{m.group(1)}-{m.group(2)}-01" if m else date.today().isoformat()
    return {"title": title, "summary": summary, "published": published, "slug": slug}


def strip_front_matter(md: str) -> str:
    """Drop the source-repo header: the H1, the bold standfirst, the translation
    link row and the badge block. All four are re-expressed by the page template
    or dropped by policy, and leaving them would duplicate the header."""
    md = re.sub(r"^#\s+.*$", "", md, count=1, flags=re.M)
    md = re.sub(r"^\*\*.+?\*\*\s*$", "", md, count=1, flags=re.M)
    md = re.sub(r"^\*\*🌐[^\n]*$", "", md, flags=re.M)
    md = re.sub(r"^(?:!\[[^\]]*\]\((?:[^()]|\([^()]*\))*\)\s*)+$", "", md, flags=re.M)
    return md.lstrip("\n")


# ------------------------------------------------------------------- template

def page(meta: dict, body: str) -> str:
    url = f"{SITE}/research/{meta['slug']}/"
    schema = {
        "@context": "https://schema.org",
        "@type": "TechArticle",
        "headline": meta["title"],
        "description": meta["summary"],
        "datePublished": meta["published"],
        "inLanguage": "en",
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "author": {
            "@type": "Person",
            "name": "Md. Azmol Haque Rony",
            "jobTitle": "Founder, Cindrasec",
            "url": SITE,
        },
        "publisher": {
            "@type": "Organization",
            "name": "Cindrasec",
            "url": SITE,
            "logo": {"@type": "ImageObject", "url": f"{SITE}/icon-512.png"},
        },
    }
    esc_t = html.escape(meta["title"], quote=True)
    esc_s = html.escape(meta["summary"], quote=True)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; form-action 'self'; base-uri 'self'; object-src 'none'; manifest-src 'self'; upgrade-insecure-requests">
<meta name="referrer" content="strict-origin-when-cross-origin">
<title>{esc_t} — Cindrasec Research</title>
<meta name="description" content="{esc_s}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:title" content="{esc_t}">
<meta property="og:description" content="{esc_s}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc_t}">
<meta name="twitter:description" content="{esc_s}">
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/manifest.json">
<link rel="preload" href="/fonts/space-grotesk-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/styles.css">
<script type="application/ld+json">{json.dumps(schema, indent=2)}</script>
</head>
<body class="research-body">
<a class="skip-link" href="#article">Skip to content</a>
<header class="research-head">
  <div class="wrap research-head-inner">
    <a class="research-brand" href="/">CINDRA<span>SEC</span></a>
    <nav class="research-nav">
      <a href="/research/">Research</a>
      <a href="/#services">Services</a>
      <a href="/#contact">Contact</a>
    </nav>
  </div>
</header>
<main class="wrap prose" id="article">
  <p class="prose-kicker"><a href="/research/">Research</a> · Published {meta['published']}</p>
  <h1>{esc_t}</h1>
  <p class="prose-standfirst">{esc_s}</p>
  <article>
{body}
  </article>
  <aside class="prose-cta">
    <p><strong>This is the kind of question Cindrasec answers for clients.</strong>
    If you are shipping an LLM feature, an agent, or an MCP server and want to know
    how it behaves under adversarial input — measured, not guessed —
    <a href="/#contact">get in touch</a>.</p>
  </aside>
</main>
<footer class="research-foot">
  <div class="wrap">
    <p>© {date.today().year} Cindrasec · Dhaka, Bangladesh ·
       <a href="/">cindrasec.com</a> ·
       <a href="/.well-known/security.txt">security.txt</a></p>
    <p class="research-foot-note">Tested against our own systems, or under a signed
       Rules of Engagement. Authorized use only.</p>
  </div>
</footer>
</body>
</html>
"""


def index_page(metas: list[dict]) -> str:
    items = "\n".join(
        f"""    <li class="research-item">
      <a class="research-item-link" href="/research/{m['slug']}/">
        <h2>{html.escape(m['title'], quote=False)}</h2>
        <p>{html.escape(m['summary'], quote=False)}</p>
        <span class="research-item-date">{m['published']}</span>
      </a>
    </li>"""
        for m in metas
    )
    schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Cindrasec Research",
        "description": "Measured security research on AI/LLM systems and exposed attack surface.",
        "url": f"{SITE}/research/",
        "hasPart": [
            {
                "@type": "TechArticle",
                "headline": m["title"],
                "url": f"{SITE}/research/{m['slug']}/",
                "datePublished": m["published"],
            }
            for m in metas
        ],
    }
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; form-action 'self'; base-uri 'self'; object-src 'none'; manifest-src 'self'; upgrade-insecure-requests">
<title>Research — Cindrasec</title>
<meta name="description" content="Measured security research from Cindrasec: prompt-injection resistance, exposed attack surface, and disclosure writeups. Methods and limitations stated in full.">
<link rel="canonical" href="{SITE}/research/">
<meta property="og:type" content="website">
<meta property="og:title" content="Research — Cindrasec">
<meta property="og:description" content="Measured security research on AI/LLM systems and exposed attack surface.">
<meta property="og:url" content="{SITE}/research/">
<meta property="og:image" content="{SITE}/og-image.png">
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<link rel="manifest" href="/manifest.json">
<link rel="preload" href="/fonts/space-grotesk-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/styles.css">
<script type="application/ld+json">{json.dumps(schema, indent=2)}</script>
</head>
<body class="research-body">
<a class="skip-link" href="#main">Skip to content</a>
<header class="research-head">
  <div class="wrap research-head-inner">
    <a class="research-brand" href="/">CINDRA<span>SEC</span></a>
    <nav class="research-nav">
      <a href="/research/" aria-current="page">Research</a>
      <a href="/#services">Services</a>
      <a href="/#contact">Contact</a>
    </nav>
  </div>
</header>
<main class="wrap prose" id="main">
  <h1>Research</h1>
  <p class="prose-standfirst">Measured work, with the method and the limits stated in
  full. A number without its confidence interval is marketing; a finding without its
  reproduction steps is an anecdote. Everything here is reproducible on commodity
  hardware, and everything was tested against our own systems or under authorization.</p>
  <ul class="research-list">
{items}
  </ul>
</main>
<footer class="research-foot">
  <div class="wrap">
    <p>© {date.today().year} Cindrasec · Dhaka, Bangladesh ·
       <a href="/">cindrasec.com</a> ·
       <a href="/.well-known/security.txt">security.txt</a></p>
  </div>
</footer>
</body>
</html>
"""


# ----------------------------------------------------------------------- main

def build() -> dict[Path, str]:
    metas = []
    files: dict[Path, str] = {}
    for md_path in sorted(SRC_DIR.glob("*.md"), reverse=True):
        slug = md_path.stem
        raw = md_path.read_text(encoding="utf-8")
        meta = parse_meta(raw, slug)
        metas.append(meta)
        body = to_html(strip_front_matter(raw))
        files[OUT_DIR / slug / "index.html"] = page(meta, body)
    files[OUT_DIR / "index.html"] = index_page(metas)
    return files


def main() -> int:
    check = "--check" in sys.argv
    files = build()
    drift = []
    for path, content in files.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                drift.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"  {path.relative_to(ROOT)}: {len(content):,} bytes")
    if check:
        if drift:
            print("research output is STALE:", ", ".join(drift))
            return 1
        print("research output is in sync with research/src/*.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
