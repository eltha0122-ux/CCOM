# 葉如凡｜企業溝通治理顧問

這是 [fanfanyeh.net](https://www.fanfanyeh.net/) 的 GitHub Pages 靜態備份專案。

## 網站內容

- 首頁
- CCOS 企業溝通營運系統
- 預防霸凌與溝通治理
- 洞察文章
- 關於如凡
- Email 洽詢頁面

原本依賴 Weebly 的聯絡表單已改為 `mailto:` Email 聯絡，不會蒐集或儲存訪客資料。

舊文章的投影片圖片已保存於專案內，並改為可水平滑動的靜態圖庫；不再依賴 Weebly 投影片與留言服務。原 Weebly 文章網址也保留靜態轉址頁，避免既有外部連結立即失效。

## 外部相依

**無。** 本站不向 Weebly 或任何第三方 CDN 請求資源（2026-08-02 起）。

| 資源 | 位置 | 授權 |
|---|---|---|
| jQuery 1.8.3 | `docs/files/vendor/` | MIT，取自官方 `code.jquery.com` |
| 6 套字型 | `docs/files/fonts/` | SIL Open Font License，取自 Google Fonts 官方 |
| 版型樣式 | `docs/files/main_style.css` | 站台外觀主要來源 |
| 靜態化補丁 | `docs/files/static-overrides.css` | 社群圖示 SVG、側欄浮動，均含註解 |

Weebly 專有的 `sites.css`、`main.js`、輪播與圖示字型已整批移除，未複製亦未自架。
社群圖示改為內嵌 SVG。唯一對外連線是內容本身的連結與文章頁的臉書／推特分享按鈕。

> ⚠️ `work/repair_static_site.py` 會依原站重新產生站台，**再次執行會把 Weebly 外部相依裝回去**並覆蓋上述本地化成果。需重跑前請先評估如何保留 `docs/files/fonts/`、`docs/files/vendor/` 與 `static-overrides.css`。

## 更換網站網址

站內有寫死的絕對網址（canonical、og:url、og:image、sitemap、robots、RSS feed）。
更換網址時不要手動改，執行：

```bash
python3 tools/set_site_url.py https://新網址
python3 tools/set_site_url.py https://新網址 --dry-run   # 只試算
```

腳本會一併處理自訂網域所需的 `docs/CNAME`，且可重複執行。

## 本機預覽

```bash
python3 -m http.server 8000 --directory docs
```

開啟 <http://localhost:8000/> 即可檢視。

## 維護與檢查

重新整理原站備份後，可執行修復腳本下載文章圖片、移除 Weebly 留言與投影片依賴，並重建 SEO metadata、舊網址轉址及 sitemap：

```bash
python3 work/repair_static_site.py \
  --docs docs \
  --base-url https://jesuswaytaipeisrv.github.io/yeh/ \
  --download-images
```

提交前執行：

```bash
python3 work/check_static_site.py docs
bash -n work/prepare-static-site.sh
git diff --check
```

## 部署

推送到 GitHub 的 `main` 分支後，GitHub Actions 會自動將 `docs/` 發佈到 GitHub Pages。

- 正式網站：<https://jesuswaytaipeisrv.github.io/yeh/>
- GitHub 儲存庫：<https://github.com/jesuswaytaipeisrv/yeh>
- Sitemap：<https://jesuswaytaipeisrv.github.io/yeh/sitemap.xml>

## 自訂網域

`fanfanyeh.net` 由網站擁有者本人註冊於 **Register.com**（非 Weebly），**2027-03-19 到期**，
與 Weebly 訂閱互相獨立，只需改 A 記錄即可指向 GitHub Pages。

改 DNS 時注意：**五筆指向 Google 的 MX 記錄不可刪除**（未確認信箱是否使用前一律保留），
另有指向 Weebly 的萬用字元 `*` A 記錄建議一併處理。完整說明見 `DEVELOPMENT_LOG.md`
2026-08-02 的「自訂網域 fanfanyeh.net 的查證結果」。

## 費用

本專案使用公開 GitHub 儲存庫與 GitHub Pages，靜態網站託管費用為免費。自訂網域若沿用既有網域，另需負擔原網域註冊／續約費用（Register.com 的 .net 續約價約每年 US$30–40）。
