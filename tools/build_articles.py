#!/usr/bin/env python3
"""把 articles/ 裡的 Markdown 文章變成網站頁面。

寫文章的人只要做一件事：在 articles/ 放一個 .md 檔，例如 articles/2026-10-07-manager-one-sentence.md

    ---
    title: 主管一句話，可能變成申訴案件？
    date: 2026-10-07
    summary: 霸凌防治法規上路後，HR 最常問我的問題是：主管到底要怎麼講話才不會踩線？
    image: /uploads/articles/2026-10-07.jpg        （選填）
    tags: 職場溝通, 霸凌防治                         （選填）
    ---
    這裡開始是內文，用一般的文字寫就好，空一行就是換段。

這支腳本（GitHub Actions 每次 push 都會自動跑，也可以在本機跑）會：
  1. 每篇 .md → docs/insight/<檔名>.html   乾淨的文章頁：同樣的版頭版尾，沒有留言、沒有 RSS、
     沒有臉書外掛；有 title / description / og:* / canonical，以及給搜尋引擎與 AI 讀的
     JSON-LD（BlogPosting + 作者 Person）。
  2. 重建 docs/insight.html 專欄列表：新文章（.md）＋ 還留在 docs/insight/ 裡的舊 Weebly 文章，
     一律依日期新到舊排。舊文章檔一刪，列表就自動消失，不用另外改。
  3. 更新 docs/sitemap.xml：加入新文章、移除已不存在的頁面。

網址前綴跟 tools/set_site_url.py 一樣，從 docs/robots.txt 的 Sitemap 行讀，所以換網域不用改這支。

用法（repo 根目錄）：
    python3 tools/build_articles.py            # 建置
    python3 tools/build_articles.py --check    # 只檢查 .md 格式，不寫檔
需要套件：pip install markdown
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import markdown  # type: ignore
except ImportError:  # pragma: no cover
    sys.exit("缺少套件 markdown，請先執行：pip install markdown")

ROOT = Path(__file__).resolve().parent.parent
ARTICLES = ROOT / "articles"
DOCS = ROOT / "docs"
INSIGHT_DIR = DOCS / "insight"
TEMPLATES = ROOT / "tools" / "templates"
ROBOTS = DOCS / "robots.txt"
SITEMAP = DOCS / "sitemap.xml"

SITE_NAME = "葉如凡｜企業溝通治理顧問"
AUTHOR = "葉如凡"
AUTHOR_TITLE = "企業溝通治理顧問"
AUTHOR_PAGE = "aboutme.html"
INQUIRY_PAGE = "inquiry.html"
DEFAULT_IMAGE = "uploads/1/0/2/8/102844230/03141523_orig.png"
SITE_KEYWORDS = "企業溝通,職場溝通,組織溝通治理,內部溝通,跨部門協作,霸凌防治,企業溝通顧問,講師,CCOS,葉如凡"

# ----------------------------------------------------------------------------
# 基本工具
# ----------------------------------------------------------------------------


def base_url() -> str:
    m = re.search(r"^Sitemap:\s*(\S+)/sitemap\.xml\s*$", ROBOTS.read_text(encoding="utf-8"), re.M)
    if not m:
        sys.exit(f"{ROBOTS} 裡找不到 'Sitemap: <網址>/sitemap.xml'，無法判斷網址前綴。")
    return m.group(1).rstrip("/")


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def fmt_date_display(d: dt.date) -> str:
    return f"{d.year}/{d.month}/{d.day}"


@dataclass
class Article:
    slug: str                 # 輸出檔名（不含 .html）
    title: str
    date: dt.date
    summary: str
    body_html: str = ""       # 只有新文章有
    image: str = ""           # 相對 docs/ 的路徑，可空
    tags: list[str] = field(default_factory=list)
    legacy: bool = False      # True = 舊 Weebly 文章，不重新產生
    modified: dt.date | None = None

    @property
    def rel_path(self) -> str:
        return f"insight/{self.slug}.html"


# ----------------------------------------------------------------------------
# 讀 Markdown
# ----------------------------------------------------------------------------

FRONT_RE = re.compile(r"\A\s*---\s*\n(.*?)\n---\s*\n?", re.S)


def parse_front_matter(text: str, name: str) -> tuple[dict, str]:
    m = FRONT_RE.match(text)
    if not m:
        raise ValueError(f"{name}：檔案開頭必須是 --- 包起來的標題區（title / date / summary）。")
    meta: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"{name}：標題區這一行看不懂（要是「欄位: 內容」）：{line!r}")
        k, v = line.split(":", 1)
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        meta[k.strip().lower()] = v
    return meta, text[m.end():]


def parse_date(s: str, name: str) -> dt.date:
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"):
        try:
            return dt.datetime.strptime(s.strip(), fmt).date()
        except ValueError:
            pass
    raise ValueError(f"{name}：date 要寫成 2026-10-07 這種格式，現在是 {s!r}")


def normalize_asset_path(p: str, depth: int) -> str:
    """把 /uploads/... 這種從網站根目錄算起的路徑，改成相對於輸出頁的路徑。"""
    p = p.strip()
    if re.match(r"^(https?:)?//", p) or p.startswith("data:"):
        return p
    if p.startswith("/"):
        return "../" * depth + p.lstrip("/")
    return p


def load_markdown_articles() -> list[Article]:
    out: list[Article] = []
    if not ARTICLES.exists():
        return out
    md = markdown.Markdown(extensions=["nl2br", "sane_lists"], output_format="html5")
    for path in sorted(ARTICLES.glob("*.md")):
        if path.name.lower().startswith("readme") or path.name.startswith("_"):
            continue  # README 與 _ 開頭的檔（範例、草稿）不會上架
        name = path.name
        meta, body = parse_front_matter(path.read_text(encoding="utf-8-sig"), name)
        for req in ("title", "date", "summary"):
            if not meta.get(req):
                raise ValueError(f"{name}：標題區缺少 {req}")
        date = parse_date(meta["date"], name)
        slug = meta.get("slug") or path.stem
        slug = re.sub(r"[^\w\-一-鿿]+", "-", slug).strip("-")
        if not slug:
            raise ValueError(f"{name}：無法從檔名產生網址")
        if re.fullmatch(r"\d{8}", slug):
            raise ValueError(f"{name}：檔名不能只有八位數字（會跟舊文章撞名），請用 2026-10-07-主題 這種格式")
        md.reset()
        body_html = md.convert(body.strip())
        # 圖片 / 連結的根路徑改相對
        body_html = re.sub(r'(src|href)="(/[^"]*)"', lambda m: f'{m.group(1)}="{normalize_asset_path(m.group(2), 1)}"', body_html)
        tags = [t.strip() for t in re.split(r"[,，、]", meta.get("tags", "")) if t.strip()]
        image = meta.get("image", "").strip().lstrip("/")
        modified = parse_date(meta["updated"], name) if meta.get("updated") else None
        out.append(Article(slug=slug, title=meta["title"].strip(), date=date, summary=meta["summary"].strip(),
                           body_html=body_html, image=image, tags=tags, modified=modified))
    return out


# ----------------------------------------------------------------------------
# 讀舊的 Weebly 文章（只抓標題、日期、摘要，用來排進列表）
# ----------------------------------------------------------------------------

def load_legacy_articles(new_slugs: set[str]) -> list[Article]:
    out: list[Article] = []
    for path in sorted(INSIGHT_DIR.glob("*.html")):
        if path.stem in new_slugs:
            continue
        s = path.read_text(encoding="utf-8", errors="replace")
        if "generated by tools/build_articles.py" in s or 'class="blog-title-link' not in s:
            continue  # 不是 Weebly 文章頁，或是本腳本產生的頁
        t = re.search(r'<h2 class="blog-title">\s*<a[^>]*>(.*?)</a>', s, re.S)
        d = re.search(r'<span class="date-text">\s*(\d{1,2})/(\d{1,2})/(\d{4})\s*</span>', s)
        desc = re.search(r'<meta property="og:description" content="([^"]*)"', s)
        img = re.search(r'<meta property="og:image" content="([^"]*)"', s)
        if not (t and d):
            continue
        title = html.unescape(re.sub(r"<[^>]+>", "", t.group(1))).strip()
        date = dt.date(int(d.group(3)), int(d.group(1)), int(d.group(2)))
        summary = html.unescape(desc.group(1)).strip() if desc else ""
        image = ""
        if img:
            m = re.search(r"/(uploads/.*)$", html.unescape(img.group(1)))
            image = m.group(1) if m else ""
        out.append(Article(slug=path.stem, title=title, date=date, summary=summary, image=image, legacy=True))
    return out


# ----------------------------------------------------------------------------
# 產生 HTML
# ----------------------------------------------------------------------------

ARTICLE_CSS = """
<style>
#blogTable .blog-post .blog-header h1.blog-title{font-family:"Josefin Sans",sans-serif;font-size:28px;font-weight:300;letter-spacing:.015em;margin:0 0 10px;line-height:1.3}
#blogTable .blog-post .blog-date{float:none;display:block;color:rgba(0,0,0,.6);font-size:15px;margin:0 0 6px}
#blogTable .blog-post .blog-tags{color:rgba(0,0,0,.55);font-size:14px;margin:0 0 20px}
#blogTable .blog-post .blog-tags span{display:inline-block;border:1px solid rgba(0,0,0,.15);border-radius:3px;padding:1px 8px;margin:0 6px 6px 0}
.article-body{color:#2a2a2a;font-size:17px;line-height:1.9;max-width:820px}
.article-body p{margin:0 0 1.2em}
.article-body h2{font-size:22px;font-weight:600;margin:1.8em 0 .6em;line-height:1.4}
.article-body h3{font-size:19px;font-weight:600;margin:1.5em 0 .5em}
.article-body ul,.article-body ol{margin:0 0 1.2em 1.6em}
.article-body li{margin:.3em 0}
.article-body blockquote{border-left:3px solid #c9c9c9;margin:1.2em 0;padding:.6em 1.2em;color:#555;background:rgba(225,228,230,.5);font-family:inherit;font-size:inherit;line-height:inherit}
.article-body blockquote::before{content:none;display:none}
.article-body blockquote p:last-child{margin-bottom:0}
.article-body img{max-width:100%;height:auto;display:block;margin:1.2em auto}
.article-body hr{border:0;border-top:1px solid #ddd;margin:2em 0}
.article-body a{text-decoration:underline}
.article-hero{margin:0 0 24px}
.article-hero img{max-width:100%;height:auto;display:block}
.article-author{border-top:1px solid #e5e5e5;margin-top:48px;padding-top:24px;color:#444;font-size:15px;line-height:1.8}
.article-author strong{font-size:16px;color:#222}
.article-author .author-actions{margin:16px 0 0;display:flex;flex-wrap:wrap;gap:10px}
.article-author a.author-btn{display:inline-block;padding:9px 18px;border:1px solid #8a6a3b;border-radius:4px;color:#8a6a3b;font-weight:600;font-size:15px;line-height:1.4;text-decoration:none;opacity:1;transition:background .15s,color .15s}
.article-author a.author-btn:hover,.article-author a.author-btn:focus{background:#8a6a3b;color:#fff}
.article-author a.author-btn-primary{background:#8a6a3b;color:#fff}
.article-author a.author-btn-primary:hover,.article-author a.author-btn-primary:focus{background:#6f5530;border-color:#6f5530}
.article-nav{margin:32px 0 0;font-size:15px}
.insight-list .blog-post{margin-bottom:44px}
.insight-list .blog-post h2.blog-title{text-transform:none;line-height:1.35}
.insight-list .blog-post .blog-date{float:none;display:block;margin:0 0 10px}
.insight-list .blog-summary{color:#3a3a3a;font-size:16px;line-height:1.8;margin:0 0 8px;max-width:820px}
.insight-list .blog-read-more a{text-decoration:underline;font-size:15px}
.insight-list .blog-post-separator{border-bottom:1px solid #e5e5e5;margin-top:28px}
.insight-intro{color:#444;font-size:16px;line-height:1.8;margin:0 0 36px;max-width:820px}
</style>
"""


def head_meta(title: str, description: str, url: str, image_url: str, keywords: str, extra: str = "") -> str:
    full = f"{title} - {SITE_NAME}"
    return (
        f"<title>{esc(full)}</title>\n"
        f'<meta name="description" content="{esc(description)}" />\n'
        f'<meta name="keywords" content="{esc(keywords)}" />\n'
        f'<meta name="author" content="{esc(AUTHOR)}" />\n'
        f'<meta property="og:site_name" content="{esc(SITE_NAME)}" />\n'
        f'<meta property="og:type" content="article" />\n'
        f'<meta property="og:title" content="{esc(title)}" />\n'
        f'<meta property="og:description" content="{esc(description)}" />\n'
        f'<meta property="og:image" content="{esc(image_url)}" />\n'
        f'<meta property="og:url" content="{esc(url)}" />\n'
        f'<meta name="twitter:card" content="summary_large_image" />\n'
        f'<link rel="canonical" href="{esc(url)}" />\n'
        f"{extra}"
    )


def jsonld(obj: dict) -> str:
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>"


def render_article(a: Article, base: str, shell: str) -> str:
    url = f"{base}/{a.rel_path}"
    image_url = f"{base}/{a.image or DEFAULT_IMAGE}"
    keywords = ", ".join(a.tags) + (", " if a.tags else "") + SITE_KEYWORDS
    ld = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": a.title,
        "description": a.summary,
        "datePublished": a.date.isoformat(),
        "dateModified": (a.modified or a.date).isoformat(),
        "inLanguage": "zh-Hant",
        "image": image_url,
        "url": url,
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "author": {"@type": "Person", "name": AUTHOR, "jobTitle": AUTHOR_TITLE, "url": f"{base}/{AUTHOR_PAGE}"},
        "publisher": {"@type": "Person", "name": AUTHOR, "url": f"{base}/"},
        "isPartOf": {"@type": "Blog", "name": f"{AUTHOR} 洞察 Insight", "url": f"{base}/insight.html"},
    }
    if a.tags:
        ld["keywords"] = ", ".join(a.tags)
    hero = f'<div class="article-hero"><img src="../{esc(a.image)}" alt="{esc(a.title)}" /></div>' if a.image else ""
    tags = ""
    if a.tags:
        tags = '<p class="blog-tags">' + "".join(f"<span>{esc(t)}</span>" for t in a.tags) + "</p>"
    content = f"""<!-- generated by tools/build_articles.py from articles/{esc(a.slug)}.md — 不要手動改這個檔，改 .md -->
<article class="blog-post" itemscope itemtype="https://schema.org/BlogPosting">
  <div class="blog-header">
    <h1 class="blog-title" itemprop="headline">{esc(a.title)}</h1>
    <p class="blog-date"><time datetime="{a.date.isoformat()}" itemprop="datePublished">{fmt_date_display(a.date)}</time>　{esc(AUTHOR)}</p>
    {tags}
  </div>
  {hero}
  <div class="blog-content article-body" itemprop="articleBody">
{a.body_html}
  </div>
  <div class="article-author">
    <strong>{esc(AUTHOR)}｜{esc(AUTHOR_TITLE)}</strong><br />
    以 CCOS 企業溝通營運系統協助企業建立可持續運作的內部溝通治理架構。
    <p class="author-actions">
      <a class="author-btn author-btn-primary" href="../{INQUIRY_PAGE}">洽詢課程與顧問服務 →</a>
      <a class="author-btn" href="../{AUTHOR_PAGE}">關於如凡 →</a>
    </p>
  </div>
  <p class="article-nav"><a href="../insight.html">← 回到洞察 Insight 文章列表</a></p>
</article>"""
    page = shell.replace("{{HEAD_META}}", head_meta(a.title, a.summary, url, image_url, keywords, jsonld(ld)))
    page = page.replace("{{EXTRA_HEAD}}", ARTICLE_CSS)
    page = page.replace("{{CONTENT}}", content)
    return page


def render_listing(items: list[Article], base: str, shell: str) -> str:
    url = f"{base}/insight.html"
    title = "洞察 Insight"
    desc = f"{AUTHOR}的專欄文章：企業溝通治理、職場溝通、霸凌防治與組織文化的觀點與實務。"
    posts = []
    for a in items:
        posts.append(f"""<div class="blog-post">
  <div class="blog-header">
    <h2 class="blog-title"><a class="blog-title-link blog-link" href="{esc(a.rel_path)}">{esc(a.title)}</a></h2>
    <p class="blog-date"><time datetime="{a.date.isoformat()}">{fmt_date_display(a.date)}</time></p>
  </div>
  <p class="blog-summary">{esc(a.summary)}</p>
  <p class="blog-read-more"><a href="{esc(a.rel_path)}" class="blog-link">閱讀全文 →</a></p>
  <div class="blog-post-separator"></div>
</div>""")
    if not posts:
        posts.append('<p class="insight-intro">文章整理中，敬請期待。</p>')
    ld = {
        "@context": "https://schema.org",
        "@type": "Blog",
        "name": f"{AUTHOR} 洞察 Insight",
        "url": url,
        "description": desc,
        "inLanguage": "zh-Hant",
        "author": {"@type": "Person", "name": AUTHOR, "jobTitle": AUTHOR_TITLE, "url": f"{base}/{AUTHOR_PAGE}"},
        "blogPost": [{"@type": "BlogPosting", "headline": a.title, "url": f"{base}/{a.rel_path}", "datePublished": a.date.isoformat()} for a in items],
    }
    content = ('<!-- generated by tools/build_articles.py — 不要手動改這個檔 -->\n<div class="insight-list">\n'
               + "\n".join(posts) + "\n</div>")
    page = shell.replace("{{HEAD_META}}", head_meta(title, desc, url, f"{base}/{DEFAULT_IMAGE}", SITE_KEYWORDS, jsonld(ld)).replace('og:type" content="article"', 'og:type" content="website"'))
    page = page.replace("{{EXTRA_HEAD}}", ARTICLE_CSS)
    page = page.replace("{{CONTENT}}", content)
    return page


# ----------------------------------------------------------------------------
# sitemap
# ----------------------------------------------------------------------------

def update_sitemap(base: str, items: list[Article]) -> int:
    locs: list[str] = []
    if SITEMAP.exists():
        locs = re.findall(r"<loc>(.*?)</loc>", SITEMAP.read_text(encoding="utf-8"))
    keep: list[str] = []
    for loc in locs:
        rel = loc[len(base):].lstrip("/") if loc.startswith(base) else None
        if rel is None:
            keep.append(loc)      # 不是本站前綴的就原樣保留（理論上不會有）
            continue
        target = DOCS / (rel or "index.html")
        if target.is_dir():
            target = target / "index.html"
        if target.exists():
            keep.append(loc)
    for a in items:
        u = f"{base}/{a.rel_path}"
        if u not in keep:
            keep.append(u)
    seen: set[str] = set()
    uniq = [u for u in keep if not (u in seen or seen.add(u))]
    body = "\n".join(f"  <url><loc>{esc(u)}</loc></url>" for u in uniq)
    SITEMAP.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "\n</urlset>\n", encoding="utf-8")
    return len(uniq)


# ----------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="只檢查 articles/*.md 的格式，不產生檔案")
    args = ap.parse_args()

    try:
        new = load_markdown_articles()
    except ValueError as e:
        print(f"❌ {e}")
        return 1
    if args.check:
        for a in new:
            print(f"✔ {a.slug}  {a.date}  {a.title}")
        print(f"{len(new)} 篇文章格式正確。")
        return 0

    base = base_url()
    legacy = load_legacy_articles({a.slug for a in new})
    items = sorted(new + legacy, key=lambda a: (a.date, a.slug), reverse=True)

    art_shell = (TEMPLATES / "article_shell.html").read_text(encoding="utf-8")
    lst_shell = (TEMPLATES / "listing_shell.html").read_text(encoding="utf-8")

    INSIGHT_DIR.mkdir(parents=True, exist_ok=True)
    for a in new:
        (INSIGHT_DIR / f"{a.slug}.html").write_text(render_article(a, base, art_shell), encoding="utf-8")
        print(f"文章  insight/{a.slug}.html  ({a.date}  {a.title})")
    (DOCS / "insight.html").write_text(render_listing(items, base, lst_shell), encoding="utf-8")
    n = update_sitemap(base, new)
    print(f"列表  insight.html（新文章 {len(new)} 篇 + 舊文章 {len(legacy)} 篇）")
    print(f"sitemap.xml  共 {n} 個網址")
    return 0


if __name__ == "__main__":
    sys.exit(main())
