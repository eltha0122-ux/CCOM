#!/usr/bin/env python3
"""Static validation for the archived site before GitHub Pages deployment."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import unquote, urlparse


# 站台目前的正式網址。換站或換網域時用 --base-url 覆蓋，或直接改這行。
DEFAULT_BASE_URL = "https://eltha0122-ux.github.io/CCOM/"
ATTRIBUTE_RE = re.compile(r'(?:src|href)=["\']([^"\']+)', re.IGNORECASE)


def local_target(page: Path, docs: Path, value: str, site_prefix: str) -> Path | None:
    """把 HTML 內的 src/href 換算成本地檔案路徑；外部或非檔案連結回傳 None。

    site_prefix 是正式網址的路徑前綴（例如 GitHub Pages 專案站的 `/CCOM/`），
    用來把根相對連結對應回 docs/ 底下。
    """
    if value.startswith(("#", "mailto:", "tel:", "javascript:", "data:", "//")):
        return None
    parsed = urlparse(value)
    if parsed.scheme or parsed.netloc:
        return None
    path = unquote(parsed.path)
    if site_prefix != "/" and path.startswith(site_prefix):
        return docs / path.removeprefix(site_prefix)
    if path.startswith("/"):
        return docs.parent / path.lstrip("/")
    return page.parent / path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docs", nargs="?", default="docs", help="站台目錄，預設 docs")
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"站台正式網址，預設 {DEFAULT_BASE_URL}",
    )
    args = parser.parse_args()

    docs = Path(args.docs).resolve()
    base_url = args.base_url if args.base_url.endswith("/") else args.base_url + "/"
    site_prefix = urlparse(base_url).path
    errors: list[str] = []
    primary_pages = sorted(
        page
        for page in docs.rglob("*.html")
        if page.relative_to(docs).parts[0] != "2"
    )

    for page in primary_pages:
        source = page.read_text(encoding="utf-8")
        relative = page.relative_to(docs)
        checks = {
            "canonical": len(re.findall(r'<link\s+rel=["\']canonical["\']', source, re.I)),
            "og:url": len(re.findall(r'<meta\s+property=["\']og:url["\']', source, re.I)),
            "static stylesheet": source.count("static-overrides.css"),
        }
        for label, count in checks.items():
            if count != 1:
                errors.append(f"{relative}: {label} 數量應為 1，實際為 {count}")

        forbidden = {
            "Weebly 留言 iframe": "showCommentForm",
            "Weebly 投影片": "wSlideshow.render",
            "錯誤背景網址": "&quot;/uploads/",
            "可提交表單": "<form",
        }
        for label, needle in forbidden.items():
            if needle.lower() in source.lower():
                errors.append(f"{relative}: 仍含有{label}")

        for meta_name in ("og:image", "og:url"):
            for tag in re.findall(
                rf'<meta\s+property=["\']{re.escape(meta_name)}["\'][^>]+>', source, re.I
            ):
                if "fanfanyeh.net" in tag or "editmysite.com" in tag:
                    errors.append(f"{relative}: {meta_name} 仍依賴舊站或 Weebly")

        for value in ATTRIBUTE_RE.findall(source):
            target = local_target(page, docs, value, site_prefix)
            if target is not None and not target.exists():
                errors.append(f"{relative}: 本地引用缺檔 {value}")

    redirects = list((docs / "2" / "post").rglob("*.html"))
    if len(redirects) != 18:
        errors.append(f"舊文章轉址頁應為 18，實際為 {len(redirects)}")

    sitemap = docs / "sitemap.xml"
    if not sitemap.exists():
        errors.append("缺少 sitemap.xml")
    else:
        sitemap_source = sitemap.read_text(encoding="utf-8")
        if sitemap_source.count("<url>") != 25:
            errors.append("sitemap.xml 應包含 25 個正式網址")
        if base_url not in sitemap_source:
            errors.append("sitemap.xml 未使用目前 GitHub Pages 正式網址")

    robots = (docs / "robots.txt").read_text(encoding="utf-8")
    if f"Sitemap: {base_url}sitemap.xml" not in robots:
        errors.append("robots.txt 的 Sitemap 網址不正確")

    if errors:
        print("static validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "static validation passed: "
        f"primary_pages={len(primary_pages)}, redirects={len(redirects)}, sitemap_urls=25"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
