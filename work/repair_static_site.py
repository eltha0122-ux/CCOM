#!/usr/bin/env python3
"""Repair the archived Weebly site for standalone GitHub Pages hosting."""

from __future__ import annotations

import argparse
import html
import os
import re
import urllib.request
from pathlib import Path
from urllib.parse import quote, urlparse


DEFAULT_BASE_URL = "https://www.fanfanyeh.net/"
SOURCE_ORIGIN = "https://www.fanfanyeh.net"

SLIDESHOW_BLOCK_RE = re.compile(
    r"<div id=['\"]\d+-slideshow['\"]></div>\s*"
    r"<script type=['\"]text/javascript['\"]>.*?wSlideshow\.render\(.*?</script>",
    re.DOTALL,
)
SLIDESHOW_URL_RE = re.compile(r'["\']url["\']\s*:\s*["\']([^"\']+)["\']')
COMMENT_RE = re.compile(
    r'<h2 id="commentReplyTitle">.*?</iframe>\s*</div>\s*</div>\s*</div>',
    re.DOTALL,
)
MALFORMED_BACKGROUND_RE = re.compile(
    r'https://www\.fanfanyeh\.net/[^"&]*&quot;/(uploads/[^&]+)&quot;'
)
OLD_ARTICLE_URL_RE = re.compile(
    r'https?://www\.fanfanyeh\.net/2/post/\d{4}/\d{2}/([^?"\'&<]+\.html)'
)
OG_IMAGE_RE = re.compile(
    r'(<meta\s+property=["\']og:image["\']\s+content=["\'])([^"\']+)(["\']\s*/?>)',
    re.IGNORECASE,
)
OG_URL_RE = re.compile(
    r'(<meta\s+property=["\']og:url["\']\s+content=["\'])([^"\']+)(["\']\s*/?>)',
    re.IGNORECASE,
)
CANONICAL_RE = re.compile(
    r'\s*<link\s+rel=["\']canonical["\'][^>]*>', re.IGNORECASE
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--docs", type=Path, default=Path("docs"))
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--download-images", action="store_true")
    return parser.parse_args()


def normalize_base_url(value: str) -> str:
    return value.rstrip("/") + "/"


def slideshow_urls(source: str) -> list[str]:
    urls: list[str] = []
    for block in SLIDESHOW_BLOCK_RE.findall(source):
        urls.extend(value.replace(r"\/", "/") for value in SLIDESHOW_URL_RE.findall(block))
    return urls


def local_upload_path(docs: Path, image_url: str) -> Path:
    clean = image_url.lstrip("/")
    if clean.startswith("uploads/"):
        clean = clean.removeprefix("uploads/")
    return docs / "uploads" / clean


def download_images(docs: Path, urls: set[str]) -> int:
    downloaded = 0
    for image_url in sorted(urls):
        target = local_upload_path(docs, image_url)
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        source_url = f"{SOURCE_ORIGIN}/uploads/{quote(image_url.lstrip('/'), safe='/')}"
        request = urllib.request.Request(
            source_url,
            headers={"User-Agent": "Mozilla/5.0 static-site-archive/1.0"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            content_type = response.headers.get_content_type()
            if not content_type.startswith("image/"):
                raise RuntimeError(f"非圖片回應：{source_url} ({content_type})")
            target.write_bytes(response.read())
        downloaded += 1
        print(f"downloaded {source_url}")
    return downloaded


def normalize_query_filenames(docs: Path) -> dict[str, str]:
    replacements: dict[str, str] = {}
    uploads = docs / "uploads"
    for source in sorted(uploads.rglob("*")):
        if not source.is_file() or "?" not in source.name:
            continue
        target = source.with_name(source.name.split("?", 1)[0])
        if target.exists() and target.read_bytes() != source.read_bytes():
            raise RuntimeError(f"正規化圖片檔名衝突：{source} -> {target}")
        old_relative = source.relative_to(docs).as_posix()
        new_relative = target.relative_to(docs).as_posix()
        if not target.exists():
            source.rename(target)
        else:
            source.unlink()
        replacements[quote(old_relative, safe="/")] = quote(new_relative, safe="/")
        print(f"renamed {old_relative} -> {new_relative}")
    return replacements


def page_relative_url(page: Path, target: Path) -> str:
    relative = os.path.relpath(target, start=page.parent)
    return quote(Path(relative).as_posix(), safe="/.")


def gallery_html(page: Path, docs: Path, block: str) -> str:
    urls = [value.replace(r"\/", "/") for value in SLIDESHOW_URL_RE.findall(block)]
    images = []
    for index, image_url in enumerate(urls, start=1):
        target = local_upload_path(docs, image_url)
        src = page_relative_url(page, target)
        images.append(
            f'<img src="{html.escape(src)}" alt="文章圖片 {index}" '
            'loading="lazy" decoding="async" />'
        )
    return (
        '<div class="static-article-gallery" aria-label="文章圖片">\n'
        + "\n".join(images)
        + "\n</div>"
    )


def canonical_url(page: Path, docs: Path, base_url: str) -> str:
    relative = page.relative_to(docs).as_posix()
    if relative == "index.html":
        return base_url
    if relative == "column/20240507.html":
        return f"{base_url}insight/20240507.html"
    return base_url + quote(relative, safe="/")


def public_upload_url(docs: Path, base_url: str, source_url: str) -> str:
    parsed = urlparse(html.unescape(source_url))
    if parsed.netloc.endswith("editmysite.com"):
        default_image = "uploads/1/0/2/8/102844230/2026-03052024_orig.jpg"
        if not (docs / default_image).exists():
            raise FileNotFoundError(f"預設 OG 圖片不存在：{default_image}")
        return base_url + quote(default_image, safe="/")
    if parsed.netloc not in {"www.fanfanyeh.net", "fanfanyeh.net"}:
        return source_url
    relative = parsed.path.lstrip("/")
    target = docs / relative
    if parsed.query and (docs / f"{relative}?{parsed.query}").exists():
        relative = f"{relative}?{parsed.query}"
        target = docs / relative
    if not target.exists():
        raise FileNotFoundError(f"OG 圖片尚未本地化：{source_url}")
    return base_url + quote(relative, safe="/")


def article_share_url(page: Path, docs: Path, base_url: str, match: re.Match[str]) -> str:
    filename = match.group(1)
    if page.parent.name == "column" and page.name == filename:
        return canonical_url(page, docs, base_url)
    return f"{base_url}insight/{quote(filename)}"


def insert_stylesheet(source: str, page: Path, docs: Path) -> str:
    if "static-overrides.css" in source:
        return source
    href = page_relative_url(page, docs / "files" / "static-overrides.css")
    return source.replace(
        "</head>", f'<link rel="stylesheet" href="{href}" />\n</head>', 1
    )


def repair_page(
    page: Path,
    docs: Path,
    base_url: str,
    filename_replacements: dict[str, str],
) -> tuple[int, int]:
    source = page.read_text(encoding="utf-8")
    for old_name, new_name in filename_replacements.items():
        source = source.replace(old_name, new_name)
    if filename_replacements:
        source = re.sub(r"[ \t]+$", "", source, flags=re.MULTILINE)
    slideshow_count = len(SLIDESHOW_BLOCK_RE.findall(source))
    comment_count = len(COMMENT_RE.findall(source))

    source = SLIDESHOW_BLOCK_RE.sub(
        lambda match: gallery_html(page, docs, match.group(0)), source
    )

    source = COMMENT_RE.sub(
        '<h2 id="commentReplyTitle">留言</h2>\n'
        '<p class="comment-static-note">本站為靜態備份頁面，留言功能已停用；'
        '如需聯繫請來信 <a href="mailto:eltha0122@gmail.com">'
        'eltha0122@gmail.com</a>。</p>',
        source,
    )

    source = MALFORMED_BACKGROUND_RE.sub(
        lambda match: page_relative_url(page, docs / match.group(1)), source
    )

    page_canonical = canonical_url(page, docs, base_url)
    source = OG_URL_RE.sub(lambda match: f"{match.group(1)}{page_canonical}{match.group(3)}", source)
    source = OG_IMAGE_RE.sub(
        lambda match: (
            f"{match.group(1)}"
            f"{public_upload_url(docs, base_url, match.group(2))}"
            f"{match.group(3)}"
        ),
        source,
    )
    source = OLD_ARTICLE_URL_RE.sub(
        lambda match: article_share_url(page, docs, base_url, match), source
    )

    source = CANONICAL_RE.sub("", source)
    canonical_tag = f'<link rel="canonical" href="{page_canonical}" />'
    source = source.replace("</head>", f"{canonical_tag}\n</head>", 1)
    source = insert_stylesheet(source, page, docs)

    page.write_text(source, encoding="utf-8")
    return slideshow_count, comment_count


def redirect_document(destination: str) -> str:
    escaped = html.escape(destination, quote=True)
    return f"""<!doctype html>
<html lang="zh-TW">
<head>
  <meta charset="utf-8" />
  <meta name="robots" content="noindex" />
  <meta http-equiv="refresh" content="0; url={escaped}" />
  <link rel="canonical" href="{escaped}" />
  <title>頁面已移動</title>
</head>
<body>
  <p>頁面已移動至 <a href="{escaped}">{escaped}</a>。</p>
</body>
</html>
"""


def create_legacy_redirects(docs: Path, base_url: str, old_urls: set[str]) -> int:
    created = 0
    for old_url in sorted(old_urls):
        parsed = urlparse(old_url)
        match = re.fullmatch(r"/2/post/(\d{4})/(\d{2})/([^/]+\.html)", parsed.path)
        if not match:
            continue
        filename = match.group(3)
        target = docs / parsed.path.lstrip("/")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            redirect_document(f"{base_url}insight/{quote(filename)}"), encoding="utf-8"
        )
        created += 1
    return created


def write_sitemap(docs: Path, base_url: str) -> int:
    urls = []
    for page in sorted(docs.rglob("*.html")):
        relative = page.relative_to(docs)
        if relative.parts[0] == "2" or relative.parts[0] == "column":
            continue
        urls.append(canonical_url(page, docs, base_url))
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    lines.extend(f"  <url><loc>{html.escape(url)}</loc></url>" for url in urls)
    lines.append("</urlset>")
    (docs / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (docs / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\n" f"Sitemap: {base_url}sitemap.xml\n",
        encoding="utf-8",
    )
    return len(urls)


def main() -> None:
    args = parse_args()
    docs = args.docs.resolve()
    base_url = normalize_base_url(args.base_url)
    pages = sorted(
        page
        for page in docs.rglob("*.html")
        if page.relative_to(docs).parts[0] != "2"
    )
    if not pages:
        raise SystemExit(f"找不到 HTML：{docs}")

    filename_replacements = normalize_query_filenames(docs)
    sources = {page: page.read_text(encoding="utf-8") for page in pages}
    image_urls = {url for source in sources.values() for url in slideshow_urls(source)}
    old_urls = {
        match.group(0)
        for source in sources.values()
        for match in OLD_ARTICLE_URL_RE.finditer(source)
    }

    downloaded = download_images(docs, image_urls) if args.download_images else 0
    missing = sorted(
        image_url
        for image_url in image_urls
        if not local_upload_path(docs, image_url).exists()
    )
    if missing:
        raise SystemExit(
            "投影片圖片尚未齊全；請加上 --download-images：\n" + "\n".join(missing)
        )

    slideshow_count = 0
    comment_count = 0
    for page in pages:
        slideshows, comments = repair_page(
            page, docs, base_url, filename_replacements
        )
        slideshow_count += slideshows
        comment_count += comments

    redirects = create_legacy_redirects(docs, base_url, old_urls)
    sitemap_urls = write_sitemap(docs, base_url)
    print(
        "repair complete: "
        f"downloaded={downloaded}, renamed={len(filename_replacements)}, "
        f"slideshows={slideshow_count}, "
        f"comments={comment_count}, redirects={redirects}, sitemap_urls={sitemap_urls}"
    )


if __name__ == "__main__":
    main()
