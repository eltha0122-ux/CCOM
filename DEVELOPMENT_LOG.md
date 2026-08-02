# 專案開發紀錄

## 2026-07-23

### Codex 複核與靜態備份完整化

- 重新核對已部署版本 `afcff671cd51e81f7c01cfb498f7498a2fba22af` 與 Claude 待修建議，發現原檢查沒有涵蓋 Weebly 投影片 JavaScript 內的圖片引用。
- 確認 11 個頁面含 149 個投影片引用（70 張不同圖片），GitHub Pages 實際會請求錯誤的主機根目錄 `/uploads/...`，抽樣回應 HTTP 404。
- 趁原 Weebly 網站仍可存取，將缺少的 70 張投影片圖片下載至 `docs/uploads/1/0/2/8/102844230/`；下載檔案經 `file` 檢查均為 PNG 圖片。
- 將 Weebly JavaScript 投影片改成使用本地圖片的水平滑動靜態圖庫，新增 `docs/files/static-overrides.css`，降低外部服務失效造成的內容缺漏。
- 將 12 個含查詢字串的圖片檔名正規化為標準 `.png`／`.jpg`，避免靜態主機以 `application/octet-stream` 回傳而影響瀏覽器顯示。
- 修正 19 篇文章與第 2 頁文章列表共 20 個格式錯誤的頁首背景網址；根因是原準備腳本只處理 `docs/*.html`，未遞迴處理文章子目錄。
- 移除 19 個 Weebly 留言輸入 iframe，保留既有留言顯示區並改為靜態停用提示與 Email 聯絡方式。
- 將 26 個正式頁面的 `og:url`、`og:image` 與 canonical 統一為目前 GitHub Pages 正式網址；所有 OG 圖片均改成本地檔案。
- 更新 37 個 Facebook 與 37 個 Twitter 舊文章分享網址，並建立 18 個 `/2/post/YYYY/MM/` 舊路徑靜態轉址頁。
- 新增含 25 個正式網址的 `docs/sitemap.xml`，並將 `docs/robots.txt` 更新為目前 sitemap 網址。
- 新增可重複執行的 `work/repair_static_site.py` 與 `work/check_static_site.py`，並串接 `work/prepare-static-site.sh`，避免日後重建恢復同類問題。
- 靜態驗證通過：26 個正式頁面各有一組 canonical、`og:url` 與本地覆寫樣式；所有本地 `src`／`href` 引用存在；表單、Weebly 留言、Weebly 投影片及錯誤背景網址均為 0。
- Python 語法檢查、Shell 語法檢查與 `git diff --check` 通過。
- 本機 HTTP smoke test 通過：首頁、文章列表、新舊文章、本地圖片、覆寫樣式、sitemap、robots.txt 與舊路徑轉址頁均回應 HTTP 200，正規化後的圖片回應正確圖片 MIME 類型。
- 嘗試進行自動化桌面／手機瀏覽器檢查，但目前執行環境沒有可用的瀏覽器實例；正式部署後仍需人工抽查桌面與手機排版。
- 修復 commit `8338001`（`完整化靜態網站圖片與舊網址`）已直接推送至 `origin/main`。
- GitHub Actions `Deploy GitHub Pages` run `30015886088` 已成功完成；正式站首頁、文章列表、舊文章、本地圖片、sitemap 與舊路徑轉址頁抽查均回應 HTTP 200，新增圖片回應 `image/png`。

### 初始建置與部署

- 建立 GitHub Pages 靜態網站專案。
- 以 `https://www.fanfanyeh.net/` 為來源，保存首頁、服務頁、洞察文章、關於頁與原站公開圖片素材。
- 修正頁首背景圖片路徑，使網站能從 GitHub 專案子路徑載入。
- 將原 Weebly 洽詢表單與 reCAPTCHA 替換成 Email 聯絡卡片。
- 將 Cloudflare 電子郵件保護連結改為 `mailto:eltha0122@gmail.com`。
- 加入 `.nojekyll` 與 GitHub Pages 自動部署工作流程。
- 保留準備腳本 `work/prepare-static-site.sh`，方便日後重新擷取與整理來源內容。
- 本機 HTTP 驗證通過：首頁、CCOS、霸凌預防、洽詢、洞察、關於頁、主要樣式與抽樣圖片皆回應 HTTP 200。
- 發佈前檢查發現目前環境未安裝 GitHub CLI (`gh`)；GitHub 儲存庫建立與推送待安裝並登入後續作業。
- 建立 `outputs/CODEX_CLI_HANDOFF.md`，完整記錄 Codex CLI 接手所需的專案背景、完成項目、阻塞狀態、GitHub 發佈流程、驗證要求與注意事項。
- Codex CLI 已重新讀取移交文件並核對專案內容；確認 `docs/` 靜態網站、GitHub Pages workflow 與交付 ZIP 均存在。
- 再次檢查仍顯示系統找不到 `gh`，因此尚未執行 Git 初始化、建立公開儲存庫、提交、推送或啟用 GitHub Pages，避免在未確認登入帳號前誤發佈。
- 使用者改為指定既有私人儲存庫 `https://github.com/jesuswaytaipeisrv/yeh` 作為推送目標；在 `gh` 安裝並完成登入前，尚無法驗證遠端內容、寫入權限與 GitHub Pages 方案資格。
- 成本注意：GitHub 官方目前僅在 GitHub Pro、Team 或 Enterprise 等付費方案支援私人儲存庫的 GitHub Pages；若 `jesuswaytaipeisrv` 是組織且使用 Free 方案，需改為公開儲存庫或升級組織方案後才能用 Pages 發佈。
- 使用標準 `git ls-remote` 成功確認指定遠端目前沒有任何 branch 或 commit，可安全建立首個版本，不需要依賴 GitHub CLI。
- 發佈前安全掃描發現 1 個課程洽詢表單及 21 個重複的電子報訂閱表單仍會向舊 Weebly 端點送出訪客資料；已改成靜態提示與 Email 聯絡方式，並同步更新 `work/prepare-static-site.sh`，避免重建時恢復外部表單。
- 調整 `.gitignore`：繼續忽略 `work/reference/` 原站擷取資料，但允許提交可重現整理流程的 `work/prepare-static-site.sh`。
- 靜態檢查通過：Weebly 表單送出端點、multipart 表單、GitHub Pages 不相容的網域根路徑及私鑰特徵均為 0 筆；重建腳本通過 `bash -n` 語法檢查。
- 更新後的本機 HTTP smoke test 通過：首頁、CCOS、霸凌預防、洽詢、洞察、關於頁、頁首背景圖、帶 `%3F` 檔名的 CSS 與圖片皆回應 HTTP 200；課程洽詢、電子報停用及 Email 洽詢提示均可讀取。
- 已初始化本機 Git 儲存庫並建立 `main`，遠端設為私人儲存庫 `https://github.com/jesuswaytaipeisrv/yeh`；首個 commit 為 `57b8f5772ef728195965caad2af0131c99196c88`（`建立葉如凡靜態網站`），已成功推送。
- GitHub Actions `Deploy GitHub Pages #1`（run `30011028291`）已自動觸發但失敗；確認原因是儲存庫尚未啟用 Pages，而目前帳號方案的設定頁僅提供「升級方案或將儲存庫改為公開」兩種啟用方式。
- 目前儲存庫維持 private，未擅自改為 public、未開始付費升級，也尚未產生 GitHub Pages 正式網址；等待使用者決定升級 GitHub Pro 或改為公開儲存庫後再繼續部署。
- 使用者後續明確確認此儲存庫用於葉如凡網站，並完成 GitHub sudo mode 身分驗證；`jesuswaytaipeisrv/yeh` 已由 private 改為 public。
- GitHub Pages 已啟用，Build and deployment source 設為 GitHub Actions；依使用者要求先停在此階段，尚未重新執行失敗的 workflow 或驗證正式網址。
- 推送 commit `55cb77f58a13f02c63099dac4913184b19d2ebec`（`記錄公開 Pages 設定`）後，自動觸發 `Deploy GitHub Pages #2`（run `30011932199`），已於 25 秒內成功完成部署。
- 正式網站為 `https://jesuswaytaipeisrv.github.io/yeh/`；首頁、CCOS、霸凌預防、洽詢、洞察、關於頁，以及實際引用的背景圖、帶 `%3F` 檔名 CSS 與圖片皆回應 HTTP 200。
- 正式環境內容檢查通過：首頁與洽詢頁顯示 `mailto:` 聯絡方式，抽樣頁面未出現舊 Weebly 表單送出端點或可提交表單。
- 正式環境瀏覽器 smoke test 通過：桌面版顯示六個主要導覽連結；390 x 844 手機版顯示 Menu，展開後可由「洽詢服務」進入正式洽詢頁，Email 洽詢區塊正常顯示。
- 公開儲存庫搭配 GitHub Pages 的靜態託管費用為免費；若日後設定自訂網域，仍需負擔網域註冊或續約費用。

### 已知相依項目

- 文章投影片、投影片圖片與留言輸入功能已不再依賴 Weebly；版型的共用字型、CSS 與部分 JavaScript 仍由 Weebly 共用 CDN 載入，後續可再評估本地化與第三方資源授權。
  - **2026-08-02 已解除**：Weebly 共用 CDN 相依全部移除，詳見下方 2026-08-02 紀錄。
- Facebook、LinkedIn、Instagram 等外部連結需連線至各自平台。

### 暫緩處理決策

- 本站是使用者協助朋友建立的臨時 GitHub Pages，後續預計移回朋友的正式網站空間，不以目前 GitHub Pages 網址作為長期正式站。
- commit `8338001` 已補齊文章圖片與舊網址、移除留言輸入 iframe，並修正分享連結、Canonical／Open Graph、Sitemap 及 robots.txt；這些項目不再列為待修。
- 目前仍保留 Weebly 共用 CDN、分析／追蹤程式與舊版 jQuery 等版型相依。使用者決定臨時站階段不再投入全面本地化或長期 SEO／主機最佳化，以免正式搬遷時重做。
  - **2026-08-02 決策變更**：因確定移轉給葉如凡本人，已完成全面本地化並移除第三方追蹤，詳見 2026-08-02 紀錄。
- 正式搬遷前應重新檢查第三方追蹤、外部資源授權與自託管、正式網域、隱私說明、404 頁面及正式主機的安全設定。
  - 其中「第三方追蹤」「外部資源授權與自託管」已於 2026-08-02 處理完成；正式網域、隱私說明、404 頁面仍待處理。

## 2026-08-02

### 移除 Weebly 外部相依，改為完全自託管

移轉給葉如凡本人前，處理先前列為「已知相依項目」的版型外部資源。原本站台仍即時向
`cdn2.editmysite.com`／`cdn11.editmysite.com` 載入 26 個檔案（CSS、字型、jQuery、輪播、圖示字型）。

處置方式依授權性質分層，而非一律下載自架：

- **jQuery 1.8.3**：改用官方 `code.jquery.com` 版本，置於 `docs/files/vendor/`。MIT 授權，自架合法。
- **6 套字型**（Lora、Open Sans、Crimson Text、Josefin Sans、Playfair Display、Quattrocento）：
  改用 Google Fonts 官方 woff2，取 latin 與 latin-ext 子集共 52 檔，置於 `docs/files/fonts/`。
  SIL Open Font License，明文允許自架。
- **Weebly 專有資源**（`sites.css`、`main.js`、`slideshow`、`social-icons.css`、
  `site_membership.css`、wIcons／wSocial 圖示字型）：**整批移除，不複製也不自架**，避開服務條款與著作權的灰色地帶。
- **Weebly 追蹤與元件程式**（Snowplow 分析、連結追蹤、marketplace platform elements）：一併移除。
  其中 membership／customer-accounts 相關資源經檢查 `wsite-member` 於全站出現 0 次，確認為未使用。
- **社群圖示**：原以 wSocial 圖示字型顯示，改為內嵌 data-URI SVG，規則寫於 `docs/files/static-overrides.css`。
- **fancybox 燈箱**：實測原版點擊圖片亦無反應，確認為失效功能，移除無損失。

移除 Weebly 樣式後版面幾乎不變，因 `docs/files/main_style.css`（版型自有樣式）本即承擔主要視覺。
僅需於 `static-overrides.css` 補兩條規則，均已加註說明：

- `.blog-sidebar .column-blog { float: right }`：原由 `sites.css` 提供，缺少會使側欄整欄貼左。
- 社群圖示 `margin-right: 5px`：使整列總寬維持 110px，與原圖示字型版本一致。

另於 26 個頁面標頭加入 `var _W = window._W || {}` 相容宣告。該全域物件原由 `main.js` 定義，
移除後頁面內殘留的 Weebly 設定片段會拋 `ReferenceError`。

順帶修正 `docs/2/feed`：30 個文章連結為 Weebly 的無副檔名格式（GitHub Pages 不支援，會 404），
已補上 `.html`；feed 內指向舊 Weebly 站的圖片改指回本站。`tools/set_site_url.py` 的處理範圍
一併納入 `docs/2/feed`。

### 測試結果

驗證方法：將「本次修改後」與「修改前」兩份站台同時以 `python3 -m http.server` 架於不同 port，
於頁面內以同源 iframe 逐頁載入並量測，避免人工截圖比對的誤差。

- **26 個內容頁面全站版面比對通過**：文章側欄 `240px @ 982`、內文欄 `821px @ 43`、
  社群圖示列 `110px`，三項與修改前完全一致。
- **破圖檢查通過**：26 頁共 200 餘個 `<img>`，以 `naturalWidth` 判定，破圖 0 張。
- **瀏覽器 console 錯誤 0 個**。
- **手機版 390px 通過**：首頁、關於我、文章列表、文章內頁、洽詢頁均無橫向溢出；
  實際點擊確認漢堡選單可展開且六個選單項目完整。
- **本地資源完整性通過**：44 個 HTML 的全部相對路徑引用，程式驗證檔案皆存在，缺檔 0。
- **`work/check_static_site.py` 通過**：`primary_pages=26, redirects=18, sitemap_urls=25`。
- **`bash -n work/prepare-static-site.sh`、`git diff --check` 通過**。
- 全站可發出網路請求的 `editmysite` 引用為 **0 處**。

**未驗證項目**：768px 平板寬度未測；107 張圖片未逐張目視（僅程式化破圖檢查）；
18 個轉址頁僅確認轉址網址正確，未逐一點擊。頁面高度與修改前有 1% 內差異
（例如首頁 6954 → 6911 px），來自字型檔來源不同造成的字寬差異，屬正常範圍。

### 補正：移除 Weebly 平台級 Google Analytics

推送後以瀏覽器檢查線上站台的實際網路請求時，發現仍有一支追蹤程式在運作：
Weebly 平台級的 Google Analytics（`UA-7870337-1`，搭配 `_setDomainName: 'none'`）。

前一輪清理是以「移除含 `editmysite` 字樣的 script 區塊」為條件，而這段程式碼直接內嵌於 HTML、
且其網址是以字串拼接組出（`'https:' == protocol ? 'https://ssl' : 'http://www'` + `'.google-analytics.com/ga.js'`），
因此既未被字串比對掃到，也未出現在靜態的主機清單中，僅能由實際執行後的網路請求發現。

已自 26 個頁面移除該 `<script>` 區塊。移除理由：該追蹤屬於 Weebly 平台而非網站擁有者，
葉如凡無從存取其資料，卻仍持續將訪客資訊送往該帳號；且 Universal Analytics 已停止處理資料，
留著只是無效請求。

移除後複驗：`performance.getEntriesByType('resource')` 顯示頁面僅載入自身網域資源，
以及臉書／推特分享按鈕的元件；`ssl.google-analytics.com` 已不再出現。
破圖 0、console 錯誤 0、側欄與社群圖示列寬維持不變。

**目前僅存的第三方連線**：文章頁分享按鈕的 `platform.twitter.com`、`syndication.twitter.com`、
`connect.facebook.net`、`www.facebook.com`。這些屬於功能性元件而非站方植入的分析追蹤，
若要達成零第三方連線，需改為純連結式的分享按鈕。

### 平板寬度的文章版面（768px 驗證後的修正）

768px 驗證發現文章頁在平板寬度仍維持「內文 + 側欄」兩欄，側欄被壓到僅約 148px，
訂閱區塊文字擠成一行三四個字。

先確認責任歸屬：取出本地化前的 commit `98313ae` 以相同條件量測，兩版的內文欄（491px）與
側欄（214px）完全相同，訂閱段落舊版 42px、新版 62px。**確認為版型既有問題，非本次變更造成**。

修正方式是在 `static-overrides.css` 加入斷點，讓側欄堆疊到內文下方。過程中修正兩個問題：

- **選擇器優先權**：主題有 `#blogTable .blog-sidebar { width: 30% }`（0,1,1,0），
  壓過原本寫的 `#blogTable > tbody > tr > td`（0,1,0,3）。改用 `#blogTable td.blog-sidebar`（0,1,1,1）才生效。
  另有 `#blogTable .blog-sidebar .column-blog { width: 70%; max-width: 240px }`，
  需一併解除 `max-width`，否則堆疊後內容仍只佔左側 240px。
- **斷點位置**：起初取 900px，但實測側欄內容寬度是漸進遞減的
  （1200px→231px、1150px→220px、1100px→210px、901px→176px，桌面基準 240px），
  900px 會漏掉 901–1150 這段同樣難看的區間。最終取 **1150px**。

主題本身已有 `@media screen and (max-width: 767px)` 的堆疊規則，因此真正的問題區間是 768–1150px。

驗證（同源 iframe 逐一量測）：

- 斷點兩側行為明確：1440／1280／1200／1151px 維持並排，且側欄內容 240／240／231／221px
  與修改前完全一致；1150／1024／900／768／600／390px 全部堆疊為滿寬。
- 訂閱段落寬度由 64px 提升至 623px（768px 時）。
- 四個含側欄的頁面（`insight.html`、`insight/previous/2.html`、`column/20240507.html`、
  文章內頁）行為一致；三個無側欄頁面（首頁、CCOS、洽詢）完全不受影響。
- 所有測試寬度均無橫向溢出、破圖 0。

此修正使平板版面與原站不同（原站同樣是擠的），為使用者明確選擇「比原站好看」的結果。

### 注意事項

- `work/repair_static_site.py` 是依原站重新產生站台的腳本，**再次執行會把 Weebly 外部相依裝回去**，
  且會覆蓋本次的本地化成果。若日後需重跑，必須先評估如何保留 `docs/files/fonts/`、
  `docs/files/vendor/` 與 `static-overrides.css` 的修改。
- 同內容的交接包（含移轉步驟、維護手冊、已知限制三份文件）另行提供給葉如凡本人。
