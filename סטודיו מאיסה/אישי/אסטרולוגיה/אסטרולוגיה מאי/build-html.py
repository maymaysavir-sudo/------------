#!/usr/bin/env python3
"""Build an RTL Hebrew HTML page from a Markdown file. Keeps .md as single source of truth."""
import io, re, sys, unicodedata
import markdown

SRC = sys.argv[1]
DST = sys.argv[2]
TITLE = sys.argv[3] if len(sys.argv) > 3 else "מסמך"

md_text = io.open(SRC, encoding="utf-8").read()

# Strip the H1 (we render it from the template) and capture it
lines = md_text.split("\n")
h1 = TITLE
for i, l in enumerate(lines):
    if l.startswith("# "):
        h1 = l[2:].strip()
        lines[i] = ""
        break
md_text = "\n".join(lines)

SVGS = []
def _stash(m):
    SVGS.append(m.group(0)); return "@@SVG%d@@" % (len(SVGS)-1)
md_text = re.sub(r"<svg\b.*?</svg>", _stash, md_text, flags=re.S)

html_body = markdown.markdown(
    md_text,
    extensions=["tables", "attr_list", "sane_lists", "md_in_html"],
    output_format="html5",
)

# Wrap tables for horizontal scroll on narrow screens
html_body = re.sub(r"<table>", '<div class="tablewrap"><table>', html_body)
html_body = re.sub(r"</table>", "</table></div>", html_body)

# Auto-isolate bare degree/orb runs so bidi doesn't scramble them
html_body = re.sub(r"(?<!\">)\b(\d+(?:\.\d+)?°(?:\d+[′\']?)?(?:\s*[–-]\s*\d+(?:\.\d+)?°(?:\d+[′\']?)?)?)",
                   r'<span class="deg">\1</span>', html_body)

# Colour-code blockquotes by leading emoji
def tint(m):
    inner = m.group(1)
    cls = ""
    if any(e in inner[:220] for e in ("🟢", "✅", "🌟", "🎯")): cls = " class=\"green\""
    elif any(e in inner[:220] for e in ("🔴", "🚩", "⛔", "🛑")): cls = " class=\"red\""
    elif any(e in inner[:220] for e in ("⚠️", "⚡", "❗")): cls = " class=\"amber\""
    return f"<blockquote{cls}>{inner}</blockquote>"
html_body = re.sub(r"<blockquote>(.*?)</blockquote>", tint, html_body, flags=re.S)

# Build a TOC from h2s
heads = re.findall(r"<h2[^>]*>(.*?)</h2>", html_body, flags=re.S)
def slug(t, n):
    t = re.sub(r"<[^>]+>", "", t)
    return "s%d" % n
toc_items = []
n = 0
def addid(m):
    global n
    n += 1
    inner = m.group(1)
    plain = re.sub(r"<[^>]+>", "", inner).strip()
    toc_items.append((f"s{n}", plain))
    return f'<h2 id="s{n}">{inner}</h2>'
html_body = re.sub(r"<h2[^>]*>(.*?)</h2>", addid, html_body, flags=re.S)
toc = "\n".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in toc_items)

CSS = """
:root{--bg:#fbfaf8;--fg:#1c1b19;--muted:#6b6660;--line:#e3ded6;--card:#fff;
--accent:#7a5c3e;--accent-soft:#f3ece3;--green:#2e7d52;--green-bg:#eaf5ee;
--red:#b4342c;--red-bg:#fdeceb;--amber:#9a6b12;--amber-bg:#fdf3e0;--maxw:58rem}
@media (prefers-color-scheme:dark){:root{--bg:#16151a;--fg:#eae7e2;--muted:#9d968d;
--line:#302d36;--card:#1e1d24;--accent:#c9a87c;--accent-soft:#282430;
--green:#6cc496;--green-bg:#172a21;--red:#f08a80;--red-bg:#2e1a18;
--amber:#dcae5a;--amber-bg:#2b2317}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);
font-family:-apple-system,'SF Hebrew','Arial Hebrew','Segoe UI',Tahoma,'Noto Sans Hebrew',sans-serif;
font-size:17px;line-height:1.85;text-align:right;direction:rtl}
.wrap{max-width:var(--maxw);margin:0 auto;padding:3rem 1.5rem 6rem}
h1,h2,h3,h4{line-height:1.35;margin:0 0 .6em;font-weight:700;letter-spacing:-.01em}
h1{font-size:2.1rem;margin-top:0}
h2{font-size:1.45rem;margin-top:2.9em;padding-bottom:.35em;border-bottom:2px solid var(--line);scroll-margin-top:1rem}
h3{font-size:1.15rem;margin-top:2em;color:var(--accent)}
h4{font-size:1.02rem;margin-top:1.6em;color:var(--muted)}
p{margin:0 0 1.05em}em{color:var(--muted)}
a{color:var(--accent);text-underline-offset:3px}
hr{border:0;border-top:1px solid var(--line);margin:2.6rem 0}
ul,ol{margin:0 0 1.15em;padding-inline-start:0;padding-inline-end:1.4em}
li{margin:.4em 0}
blockquote{margin:1.5em 0;padding:1em 1.2em;background:var(--card);
border:1px solid var(--line);border-inline-start:5px solid var(--accent);border-radius:.5rem}
blockquote>:last-child{margin-bottom:0}
blockquote.green{border-inline-start-color:var(--green);background:var(--green-bg)}
blockquote.red{border-inline-start-color:var(--red);background:var(--red-bg)}
blockquote.amber{border-inline-start-color:var(--amber);background:var(--amber-bg)}
.wheel{margin:2rem 0;padding:1rem .5rem;background:var(--card);border:1px solid var(--line);
border-radius:.5rem;color:var(--fg)}
.wheel svg{color:var(--fg)}
.tablewrap{overflow-x:auto;margin:1.4em 0;-webkit-overflow-scrolling:touch}
table{border-collapse:collapse;width:100%;min-width:32rem;direction:rtl;font-size:.94rem;
background:var(--card);border:1px solid var(--line);border-radius:.5rem;overflow:hidden}
th,td{text-align:right;padding:.65em .85em;border-bottom:1px solid var(--line);
vertical-align:top;line-height:1.6}
th{background:var(--accent-soft);font-weight:700}
tbody tr:last-child td{border-bottom:0}
tbody tr:nth-child(even){background:color-mix(in srgb,var(--accent-soft) 40%,transparent)}
.deg{unicode-bidi:isolate}
.lede{color:var(--muted);font-size:.97rem;line-height:1.7}
.toc{background:var(--card);border:1px solid var(--line);border-radius:.6rem;
padding:1.1em 1.5em;margin:2.2rem 0 3rem}
.toc h3{margin:0 0 .5em;color:var(--fg);font-size:.95rem;letter-spacing:.03em}
.toc ol{padding-inline-end:1.3em;margin:0;font-size:.93rem;columns:2;column-gap:2rem}
.toc li{margin:.25em 0;break-inside:avoid}
.toc a{text-decoration:none}.toc a:hover{text-decoration:underline}
@media print{body{background:#fff;color:#000;font-size:10.5pt}
.toc{break-inside:avoid}h2{break-after:avoid}table,blockquote{break-inside:avoid}
.wrap{padding:0;max-width:none}}
@media (max-width:680px){body{font-size:16px}.wrap{padding:2rem 1rem 4rem}
h1{font-size:1.65rem}h2{font-size:1.25rem}.toc ol{columns:1}}
"""

out = f"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{h1}</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<h1>{h1}</h1>
<div class="toc">
<h3>תוכן</h3>
<ol>
{toc}
</ol>
</div>
{html_body}
</div>
</body>
</html>
"""
for _i, _sv in enumerate(SVGS):
    out = out.replace("@@SVG%d@@" % _i, _sv)
assert "@@SVG" not in out
io.open(DST, "w", encoding="utf-8").write(out)
print(f"built {DST}  ({len(out):,} bytes, {len(toc_items)} sections)")
