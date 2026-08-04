#!/usr/bin/env python3
"""
Generate the English and Bengali pages from one bilingual source.

WHY THIS EXISTS
---------------
The site used to ship a single index.html carrying both languages inline, as
148 pairs of `<span data-en>…</span><span data-bn hidden lang="bn">…</span>`,
with JavaScript flipping the `hidden` attribute.

That is fine for a reader and useless for a search engine. Google discounts
text hidden at load, so every Bengali sentence on the page earned nothing in
Bengali search — while the businesses Cindrasec actually sells to read Bengali.
Google's documented answer for multilingual sites is separate URLs joined by
reciprocal hreflang, which is what this script produces:

    src/index.src.html  ──build──┬──►  index.html      (lang=en, hreflang→/bn/)
                                 └──►  bn/index.html   (lang=bn, hreflang→/)

Both files come from one source, so the two languages cannot drift: change a
sentence once, rebuild, and both pages update. That is the same reason
build_roe.py exists for the Rules of Engagement PDFs.

INVARIANTS
----------
* Asset paths in the output are root-absolute (/styles.css, not styles.css) so
  the page under /bn/ resolves them identically to the one at /.
* No language's markup survives in the other page's DOM. The BN page contains
  no English spans and vice versa — that is the entire point.
* The `hidden` attribute is stripped from Bengali content in the BN output.
  Shipping it hidden would reproduce the bug this script fixes.
* The language switch is a real <a href>, not a script. A crawler has to be
  able to follow it.

USAGE
-----
    python3 build.py            # writes index.html and bn/index.html
    python3 build.py --check    # verifies the committed output matches source
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "src" / "index.src.html"

# Match the bilingual wrappers by ATTRIBUTE, never by exact string. The source
# carries four variants -- `<span data-en>`, `<span class="en" data-en>` and the
# two Bengali equivalents -- and an exact-string match silently skips the
# class-bearing ones, leaving the other language's text in the output.
OPEN_RE = re.compile(r'<span\b(?P<attrs>[^>]*\bdata-(?P<lang>en|bn)\b[^>]*)>')
CLASS_RE = re.compile(r'\bclass="([^"]*)"')

# Asset references that are relative in the source and must become
# root-absolute so /bn/ does not resolve them against /bn/.
RELATIVE_ASSETS = [
    "icon.svg", "icon-192.png", "icon-512.png", "apple-touch-icon.png",
    "manifest.json", "styles.css", "app.js", "sample-finding.pdf",
    "fonts/inter-var.woff2", "fonts/space-grotesk-var.woff2",
    "fonts/jetbrains-mono-var.woff2",
]


def _span_end(html: str, open_at: int, open_tag: str) -> int:
    """Index just past the </span> that closes the span opening at `open_at`.

    A non-greedy regex is wrong here: three of the bilingual blocks contain a
    nested <span> (the gradient word in the H1, and an inline lang="bn" word in
    an English sentence), and a lazy match would close on the inner tag and
    leave orphaned markup. So walk the tags and count depth.
    """
    depth = 0
    i = open_at
    tag = re.compile(r"<span\b|</span>")
    while True:
        m = tag.search(html, i)
        if m is None:
            raise ValueError(f"unclosed {open_tag} at offset {open_at}")
        if m.group(0) == "</span>":
            depth -= 1
            if depth == 0:
                return m.end()
        else:
            depth += 1
        i = m.end()


def _transform_spans(html: str, keep: str) -> str:
    """Unwrap the kept language's spans; delete the other language's entirely.

    A kept wrapper is dropped completely unless it carries a class, in which
    case the span survives with only that class -- the `data-*`, `hidden` and
    now-redundant `lang` attributes all go, because the page-level <html lang>
    already states the language.
    """
    out = []
    i = 0
    while True:
        m = OPEN_RE.search(html, i)
        if m is None:
            out.append(html[i:])
            return "".join(out)
        lang = m.group("lang")
        end = _span_end(html, m.start(), m.group(0))
        out.append(html[i:m.start()])
        if lang == keep:
            inner = html[m.end():end - len("</span>")]
            cls = CLASS_RE.search(m.group("attrs"))
            out.append(f'<span class="{cls.group(1)}">{inner}</span>' if cls else inner)
        # else: drop the block entirely
        i = end


def _absolutise_assets(html: str) -> str:
    for asset in RELATIVE_ASSETS:
        html = html.replace(f'href="{asset}"', f'href="/{asset}"')
        html = html.replace(f'src="{asset}"', f'src="/{asset}"')
    return html


LANG_TOGGLE_EN = (
    '<span class="active" aria-current="page">EN</span>'
    '<a href="/bn/" hreflang="bn" lang="bn" title="বাংলায় দেখুন">বাং</a>'
)
LANG_TOGGLE_BN = (
    # Tooltip is in the page's own language; the label stays in the target
    # language and carries lang="en" so a Bengali screen reader says "E N",
    # not an attempted Bengali reading of the letters.
    '<a href="/" hreflang="en" lang="en" title="ইংরেজিতে দেখুন">EN</a>'
    '<span class="active" aria-current="page" lang="bn">বাং</span>'
)

TOGGLE_SRC = re.compile(
    r'<button data-lang-btn="en"[^>]*>.*?</button>\s*'
    r'<button data-lang-btn="bn"[^>]*>.*?</button>',
    re.S,
)

HREFLANG = (
    '<link rel="alternate" hreflang="en" href="https://cindrasec.com/">\n'
    '<link rel="alternate" hreflang="bn" href="https://cindrasec.com/bn/">\n'
    '<link rel="alternate" hreflang="x-default" href="https://cindrasec.com/">'
)

LATIN_PRELOADS = (
    '<link rel="preload" href="/fonts/jetbrains-mono-var.woff2" as="font" type="font/woff2" crossorigin>'
)
BN_PRELOAD = (
    '<link rel="preload" href="/fonts/noto-sans-bengali-var.woff2" as="font" type="font/woff2" crossorigin>'
)

IMAGE_ALT_RE = re.compile(r'<meta property="og:image:alt" content="[^"]*">')
BN_IMAGE_ALT = (
    '<meta property="og:image:alt" content="Cindrasec — আগুন ছড়ানোর আগেই আঁচ খুঁজে বের করি। '
    'অ্যাটাক সারফেস ও AI/LLM সিকিউরিটি মনিটরিং।">'
)

BN_TITLE = "Cindrasec — অ্যাটাক সারফেস ও AI/LLM সিকিউরিটি মনিটরিং"
BN_DESC = (
    "ফাউন্ডার ও ছোট ব্যবসার জন্য অটোমেটেড অ্যাটাক-সারফেস এবং AI/LLM সিকিউরিটি "
    "মনিটরিং — বাংলাদেশ ও বিশ্বজুড়ে। প্রমাণ-ভিত্তিক, শুধুমাত্র অনুমোদিত পরীক্ষা। "
    "প্রথম Snapshot ফ্রি।"
)


def _text(fragment: str) -> str:
    """Visible text of an HTML fragment, whitespace-collapsed."""
    t = re.sub(r"<[^>]+>", "", fragment)
    t = (t.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
          .replace("&quot;", '"').replace("&#39;", "'").replace("&nbsp;", " "))
    return re.sub(r"\s+", " ", t).strip()


FAQ_ITEM = re.compile(r"<details\b[^>]*>\s*<summary[^>]*>(.*?)</summary>(.*?)</details>", re.S)
# Scope the scrape to the FAQ section. <details> is a generic disclosure widget and
# the page uses it elsewhere -- the privacy notice is five more of them -- so
# scanning the whole document silently advertised "Just visiting" to Google as a
# frequently asked question.
FAQ_SECTION = re.compile(r'<section[^>]*\bid="faq"[^>]*>(.*?)</section>', re.S)
LD_FAQ = re.compile(
    r'<script type="application/ld\+json">\s*\{[^<]*?"@type":\s*"FAQPage".*?</script>', re.S
)


def _rewrite_faq_jsonld(html: str, lang: str) -> str:
    """Regenerate the FAQPage block from the page's own visible FAQ.

    Google requires FAQ structured data to match the content a visitor sees. The
    source's hand-written block is English, so after the language split the
    Bengali page was advertising English questions against Bengali <details> --
    reintroducing exactly the parity bug commit 6a23962 fixed. Deriving the
    block from the rendered FAQ makes the two incapable of disagreeing: edit a
    question once, rebuild, and the markup follows.
    """
    section = FAQ_SECTION.search(html)
    if not section:
        raise ValueError('no <section id="faq"> found - the markup shape changed')

    items = []
    for summary, body in FAQ_ITEM.findall(section.group(1)):
        q, a = _text(summary), _text(body)
        if q and a:
            items.append({"q": q, "a": a})
    if not items:
        raise ValueError("no FAQ items found - the markup shape changed")

    entities = ",\n    ".join(
        '{{ "@type": "Question", "name": {q}, "acceptedAnswer": {{ "@type": "Answer", "text": {a} }} }}'
        .format(q=json.dumps(i["q"], ensure_ascii=False), a=json.dumps(i["a"], ensure_ascii=False))
        for i in items
    )
    block = (
        '<script type="application/ld+json">\n'
        '{\n  "@context": "https://schema.org",\n  "@type": "FAQPage",\n'
        f'  "inLanguage": "{lang}",\n  "mainEntity": [\n    {entities}\n  ]\n'
        '}\n</script>'
    )
    new, n = LD_FAQ.subn(block, html, count=1)
    if n != 1:
        raise ValueError("FAQPage JSON-LD block not found exactly once")
    return new


ATTR_OVERRIDE = re.compile(r'\sdata-bn-(?P<attr>[a-z-]+)="(?P<value>[^"]*)"')


def _localise_attrs(html: str, lang: str) -> str:
    """Apply `data-bn-<attr>` overrides, then strip them.

    The `<span data-en>/<span data-bn>` mechanism only reaches element CONTENT,
    so attributes stayed English on the Bengali page -- placeholders, aria-labels
    and the skip link, none of which appear in innerText and all of which a
    Bengali reader or screen-reader user meets first. Authors write:

        <input placeholder="Your name" data-bn-placeholder="আপনার নাম">

    and the Bengali build swaps the value in. English simply drops the extras.
    """
    if lang == "bn":
        out = []
        pos = 0
        for m in ATTR_OVERRIDE.finditer(html):
            # find the element this override belongs to and replace its attribute
            start = html.rfind("<", 0, m.start())
            end = html.index(">", m.end())
            tag = html[start:end + 1]
            attr, value = m.group("attr"), m.group("value")
            new_tag = re.sub(rf'\s{attr}="[^"]*"', f' {attr}="{value}"', tag, count=1)
            if new_tag == tag:                      # attribute absent -> add it
                new_tag = tag[:-1] + f' {attr}="{value}">'
            out.append(html[pos:start]); out.append(new_tag); pos = end + 1
        out.append(html[pos:])
        html = "".join(out)
    return ATTR_OVERRIDE.sub("", html)


def build(lang: str, html: str) -> str:
    html = _transform_spans(html, keep=lang)
    html = _absolutise_assets(html)
    html = _localise_attrs(html, lang)
    html = TOGGLE_SRC.sub(LANG_TOGGLE_EN if lang == "en" else LANG_TOGGLE_BN, html, count=1)

    # hreflang goes on both pages, pointing at both pages plus x-default.
    html = html.replace(
        '<link rel="canonical" href="https://cindrasec.com/">',
        HREFLANG if lang == "en"
        else '<link rel="canonical" href="https://cindrasec.com/bn/">\n' + HREFLANG,
        1,
    )
    if lang == "en":
        html = html.replace(
            HREFLANG, '<link rel="canonical" href="https://cindrasec.com/">\n' + HREFLANG, 1
        )

    if lang == "bn":
        html = html.replace('<html lang="en">', '<html lang="bn">', 1)
        html = re.sub(r"<title>.*?</title>", f"<title>{BN_TITLE}</title>", html, count=1, flags=re.S)
        html = re.sub(
            r'<meta name="description" content=".*?">',
            f'<meta name="description" content="{BN_DESC}">', html, count=1, flags=re.S,
        )
        html = html.replace(
            '<meta property="og:url" content="https://cindrasec.com/">',
            '<meta property="og:url" content="https://cindrasec.com/bn/">', 1,
        )
        html = html.replace(
            '<meta property="og:locale" content="en_US">\n'
            '<meta property="og:locale:alternate" content="bn_BD">',
            '<meta property="og:locale" content="bn_BD">\n'
            '<meta property="og:locale:alternate" content="en_US">',
        )
        for prop in ("og:title", "twitter:title"):
            html = re.sub(
                rf'(<meta (?:property|name)="{prop}" content=").*?(">)',
                rf"\g<1>{BN_TITLE}\g<2>", html, count=1,
            )
        for prop in ("og:description", "twitter:description"):
            html = re.sub(
                rf'(<meta (?:property|name)="{prop}" content=").*?(">)',
                rf"\g<1>{BN_DESC}\g<2>", html, count=1, flags=re.S,
            )
        html = IMAGE_ALT_RE.sub(lambda _: BN_IMAGE_ALT, html, count=1)
        # The @font-face unicode-range already stops the English page fetching the
        # Bengali face. Preloading is the other half: on /bn/ that font carries
        # nearly every glyph on the page, so it must not wait for CSS to be parsed
        # and matched. Only this build gets the hint -- preloading it on / would
        # download 73KB the English page never draws with.
        html = html.replace(LATIN_PRELOADS, LATIN_PRELOADS + "\n" + BN_PRELOAD, 1)

    html = _rewrite_faq_jsonld(html, lang)

    banner = (
        "<!-- Generated by build.py from src/index.src.html — do not edit directly. -->\n"
    )
    return html.replace("<!DOCTYPE html>", "<!DOCTYPE html>\n" + banner.rstrip(), 1)


def main() -> int:
    source = SRC.read_text(encoding="utf-8")
    check = "--check" in sys.argv
    targets = {"en": ROOT / "index.html", "bn": ROOT / "bn" / "index.html"}
    stale = []
    for lang, path in targets.items():
        html = build(lang, source)
        if check:
            current = path.read_text(encoding="utf-8") if path.exists() else ""
            if current != html:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(html, encoding="utf-8")
            leftover = OPEN_RE.findall(html)
            other = "bn" if lang == "en" else "en"
            other_script = len(re.findall(r"[\u0980-\u09FF]", html)) if lang == "en" else 0
            print(f"  {path.relative_to(ROOT)}: {len(html):,} bytes  "
                  f"(leftover bilingual spans={len(leftover)}, "
                  f"stray Bengali chars={other_script})")
            assert not leftover, f"bilingual spans survived the build: {leftover[:3]}"
            assert f'data-{other}' not in html, f"{other} markers survived in the {lang} page"
    if check:
        if stale:
            print("STALE — rebuild needed:", ", ".join(stale))
            return 1
        print("output is in sync with src/index.src.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
