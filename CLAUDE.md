# CLAUDE.md — fanfanyeh.net 維護交接

給接手的 AI 助理或工程師：先讀這份，再讀 `README.md`。
最後更新：2026-10-09。

## 維護方式

- 文章內容：直接在 GitHub 網頁新增或修改 `articles/*.md`，存檔後自動部署，不需要本機環境。
- 程式與樣式修改：以 commit 或 patch 提交到 `main`，push 後自動部署。修改前先 `git pull`，因為 `articles/` 常有網頁上的新 commit。

## 架構

- 原站是 Weebly，整站爬成靜態 HTML 放在 `docs/`，由 GitHub Actions（`.github/workflows/pages.yml`）部署到 GitHub Pages。
- 網域：`fanfanyeh.net`，DNS 在 Cloudflare（橘雲 proxy）。apex 四筆 A 記錄指向 GitHub Pages，`www` 的 CNAME 指向 `eltha0122-ux.github.io`。網域續約到 2028-03。
- 正式網址是 `https://fanfanyeh.net`（不帶 www）。網址前綴一律從 `docs/robots.txt` 的 Sitemap 行讀取，換網域用 `tools/set_site_url.py`。
- 頁面是 Weebly 主題外殼，大量 `wsite-*` class 與已停用的 `_W` 設定片段（`index.html` 開頭有 `_W` stub 防止報錯）。這些是死程式碼，不要手動清，會弄壞版面。
- 全站共用的樣式修正都寫在 `docs/files/static-overrides.css`，所有頁面都會載入，主題 CSS（`main_style.css?…`）不要改。

## 文章機制（2026-10 新增）

- `articles/<檔名>.md`：開頭 front matter 必填 `title`、`date`、`summary`，選填 `tags`、`image`、`updated`、`slug`。`_` 開頭與 README 不會上架。
- `tools/build_articles.py` 在 Actions 部署前執行，產生以下內容：
  - `docs/insight/<檔名>.html`：沿用 `tools/templates/` 的版頭版尾外殼；無留言、RSS、FB 外掛；有 canonical、og、JSON-LD（BlogPosting + Person）。
  - 重建 `docs/insight.html` 列表：新文章加上仍存在的舊 Weebly 文章（`docs/insight/YYYYMMDD.html`），依日期排序。
  - 更新 `docs/sitemap.xml`。
- 產生的 HTML 不進 git，由 Actions 建置。本機測試：`pip install markdown && python3 tools/build_articles.py`，提交前用 `git checkout -- docs/insight.html docs/sitemap.xml` 還原、刪掉產生的 `docs/insight/2026-*.html`。
- 文章頁樣式（引言、作者框按鈕等）寫在 `build_articles.py` 的 `ARTICLE_CSS`。
- 舊文章下架：刪 `docs/insight/` 對應檔案即可，列表與 sitemap 自動更新。她想等寫完三篇新文章、確定新定位後再決定。
- 另有一份給作者的 GitHub 網頁上架操作手冊（Word 檔，未放在 repo）。

## 提交前檢查

```bash
python3 work/check_static_site.py docs   # 必須 passed
python3 tools/build_articles.py --check
```

## 部署注意

- 部署失敗時不要按 Re-run，會出現 "Multiple artifacts named github-pages" 的錯誤。要到 Actions → Deploy GitHub Pages → **Run workflow** 開一筆新的執行。
- 偶發的 `Failed to create deployment (status: 500)` 是 GitHub 端的錯誤，重新 Run workflow 即可。

## AI 爬蟲與 SEO 現況

- Cloudflare AI Crawl Control 的政策：搜尋＝允許、代理＝允許、訓練＝不允許，Bot Preference Sync 開啟。Cloudflare 會在 `robots.txt` 前面自動加上 Content-Signal 與訓練爬蟲的 Disallow 清單。
- repo 的 `robots.txt` 另外聲明 `Google-Extended`、`Applebot-Extended` 為 Disallow，與 Cloudflare 自動加的內容重複，但不衝突。`work/repair_static_site.py` 重建 robots.txt 時會保留這兩條。
- 已知：Cloudflare 把 `Claude-User` 歸類為 AI Crawler，被「訓練＝不允許」連帶封鎖、無法單獨解開，網站主決定先不處理。Cloudflare 自動清單也包含 `Baiduspider`。
- 網站主的意圖：能被 AI 搜尋與推薦，不能被拿去訓練。

## 信箱

- 本網域不收發信（站上的聯絡信箱是 Gmail）。
- Cloudflare 已加 SPF（`v=spf1 -all`）與 DMARC（`v=DMARC1; p=reject; adkim=s; aspf=s`）兩筆記錄。空 MX（`.`）Cloudflare 不接受，已略過。

## 待辦／已知問題

- **橫幅裁切**（暫緩，等網站主決定）：各頁 `.wsite-header-section` 是固定高度（400–700px）加上 `background-size: cover`。橫幅圖為 16:9 且文字畫在圖裡，螢幕越寬露出越少：2560 寬時首頁只露出原圖 35%，上下文字被切；1920 寬時預防霸凌頁下方箭頭被切。
  - 已試做的解法：改成 `background-size: 100% auto` 加上 `height: calc(100vw * 0.5625 * frac)`，依每張圖框選含文字的區段。框選比例（上緣%、高度比例）：首頁 30%/0.50、CCOS 與洽詢 26%/0.46、預防霸凌 25%/0.55、洞察 30%/0.52、關於 30%/0.58，`background-position-y = top / (1 - frac)`。
  - 尚未提交，需要先截圖給網站主確認。
- 洞察列表目前單頁全列，文章超過約 30 篇時再加分頁。
- `archive.org_bot` 目前允許，若網站主希望撤下的文章不留公開快照，可在 Cloudflare 封鎖。

## 變更紀錄（本輪）

- 0001 Markdown 文章機制
- 0002 全站網址改為 fanfanyeh.net、`docs/CNAME`
- 0003 robots.txt 加上 AI 訓練拒絕聲明
- 0004 文章頁引言疊字修正、作者框改為按鈕
- 0005 頁首 logo 上緣裁切修正（line-height 1.5、overflow visible、nowrap）
