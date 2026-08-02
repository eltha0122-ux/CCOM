#!/usr/bin/env python3
"""把整站寫死的網站網址換成新網址。

這個靜態站的內文連結都是相對路徑，搬家後照樣能開；但下面這些地方寫死了絕對網址，
不換掉的話：Google 會以為正版還在舊網址（canonical）、臉書 LINE 分享會抓不到縮圖（og:image）。

會處理的位置：
  docs/**/*.html   <link rel="canonical">、<meta property="og:url">、<meta property="og:image">、
                   臉書 / Twitter 分享按鈕的網址
  docs/sitemap.xml 全部 <loc>
  docs/robots.txt  Sitemap: 那一行
  docs/CNAME       用自訂網域時自動建立，改回 github.io 時自動刪除

目前網址是從 docs/robots.txt 的 Sitemap 行讀出來的，所以這支腳本可以重複執行，
換幾次網址都行。

用法（在 repo 根目錄執行）：
    python3 tools/set_site_url.py https://www.fanfanyeh.net
    python3 tools/set_site_url.py https://fanfanyeh.github.io/yeh
    python3 tools/set_site_url.py https://fanfanyeh.github.io
    python3 tools/set_site_url.py https://www.fanfanyeh.net --dry-run   # 只看會改什麼，不動檔案
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
ROBOTS = DOCS / "robots.txt"


def read_current_base() -> str:
    """從 robots.txt 的 Sitemap 行反推目前全站使用的網址前綴（不含結尾斜線）。"""
    if not ROBOTS.exists():
        sys.exit(f"找不到 {ROBOTS}，請確認你在 repo 根目錄執行這支腳本。")
    m = re.search(r"^Sitemap:\s*(\S+)/sitemap\.xml\s*$", ROBOTS.read_text(encoding="utf-8"), re.M)
    if not m:
        sys.exit(f"{ROBOTS} 裡找不到 'Sitemap: <網址>/sitemap.xml'，無法判斷目前網址。")
    return m.group(1).rstrip("/")


def normalize(url: str) -> str:
    url = url.strip().rstrip("/")
    if not url.startswith(("http://", "https://")):
        sys.exit(f"網址要以 https:// 開頭，你給的是：{url}")
    if url.startswith("http://"):
        print("提醒：GitHub Pages 一律走 https，已自動改成 https://")
        url = "https://" + url[len("http://"):]
    return url


def target_files() -> list[Path]:
    files = sorted(DOCS.rglob("*.html"))
    for extra in (DOCS / "sitemap.xml", ROBOTS, DOCS / "2" / "feed"):
        if extra.exists():
            files.append(extra)
    return files


def sync_cname(new_base: str, dry_run: bool) -> None:
    """自訂網域要有 CNAME 檔；用回 github.io 則必須把它刪掉，否則 Pages 會部署失敗。"""
    prefix = "（試算）" if dry_run else ""
    host = new_base.split("//", 1)[1].split("/", 1)[0]
    cname = DOCS / "CNAME"
    if host.endswith(".github.io"):
        if cname.exists():
            print(f"  {prefix}刪除 docs/CNAME（改用 {host}，不需要自訂網域檔）")
            if not dry_run:
                cname.unlink()
        return
    print(f"  {prefix}寫入 docs/CNAME → {host}")
    if not dry_run:
        cname.write_text(host + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="把整站寫死的網址換成新網址")
    parser.add_argument("new_url", help="新網址，例如 https://www.fanfanyeh.net")
    parser.add_argument("--dry-run", action="store_true", help="只印出會改幾處，不實際寫檔")
    args = parser.parse_args()

    old_base = read_current_base()
    new_base = normalize(args.new_url)

    if old_base == new_base:
        print(f"目前網址已經是 {new_base}，不需要改。")
        return

    print(f"舊網址：{old_base}")
    print(f"新網址：{new_base}")
    print("--dry-run：只試算，不會動到檔案\n" if args.dry_run else "")

    changed_files = 0
    changed_hits = 0
    for path in target_files():
        text = path.read_text(encoding="utf-8", errors="surrogateescape")
        hits = text.count(old_base)
        if not hits:
            continue
        changed_files += 1
        changed_hits += hits
        print(f"  {path.relative_to(ROOT)}：{hits} 處")
        if not args.dry_run:
            path.write_text(text.replace(old_base, new_base), encoding="utf-8", errors="surrogateescape")

    sync_cname(new_base, args.dry_run)

    print(f"\n{'預計改' if args.dry_run else '已改'} {changed_files} 個檔案、共 {changed_hits} 處網址。")
    if not args.dry_run:
        print("接著把改動 commit + push，GitHub Pages 會自動重新部署。")


if __name__ == "__main__":
    main()
