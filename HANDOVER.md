# 移交說明（fanfanyeh.net → GitHub Pages）

原站 `www.fanfanyeh.net` 建在 Weebly，空間即將到期。本專案把整站爬成純靜態 HTML，
改放 GitHub Pages（免費），並已移除所有 Weebly 相依，可獨立運作。

本檔記錄移交的進度與剩餘步驟。技術細節見 `README.md`，完整開發過程見 `DEVELOPMENT_LOG.md`。

## 現況

| 項目 | 狀態 |
|---|---|
| 站台內容 | 44 個 HTML、107 張圖，已完全脫離 Weebly |
| 新家 | `https://github.com/eltha0122-ux/CCOM`（葉如凡本人帳號，public） |
| 新網址 | **`https://eltha0122-ux.github.io/CCOM/` 已上線**（2026-08-02 部署成功並驗證） |
| 原建置位置 | `https://github.com/jesuswaytaipeisrv/yeh`：2026-08-03 起改為 **private**，其 GitHub Pages 已隨之停用，`jesuswaytaipeisrv.github.io/yeh/` 不再對外。repo 本身保留為備份，待移轉完成後刪除 |
| 網域 | `fanfanyeh.net` 仍指向 Weebly，**尚未變更** |
| 離線備份 | `yeh-網站移轉包.zip`（232 檔，與 repo 內容相同） |

## 移轉步驟與進度

順序不可跳，尤其第 4 步是唯一不可逆的關卡——**改 DNS 之前，Weebly 必須還活著**，
否則無法回頭比對原站內容。

- [x] **1. 站台靜態化**：移除 Weebly 的 CSS／JS／輪播／圖示字型與平台級 Google Analytics，
      jQuery 與字型改為自帶（MIT／OFL 授權）。
- [x] **2. 換成新網址**：`python3 tools/set_site_url.py https://eltha0122-ux.github.io/CCOM/`
      已執行，47 個檔案共 341 處絕對網址（canonical、og:url、sitemap、robots、RSS）皆已更新。
- [x] **3. 推上她的 repo 並上線** — 已完成，站台在 `https://eltha0122-ux.github.io/CCOM/`
  - [x] 她到 `CCOM` repo 的 Settings → Collaborators 邀請協助者帳號（`jesuswaytaipeisrv`）
  - [x] 推送 `main` 分支（完整專案，含 `docs/`、`tools/`、`work/`、`.github/`）
  - [x] 她到 **Settings → Pages → Build and deployment → Source 選 `GitHub Actions`**
  - [x] 重跑 workflow → 部署成功（2026-08-02）
  - [x] 線上驗證通過：25 頁全開、201 張圖無破圖、18 個轉址頁全部正確、
        390／768／1280px 三種寬度皆無水平溢出

  > **啟用 Pages 只有 repo 擁有者能做，無法代勞。** 實測：collaborator 的 push 權限呼叫
  > Pages API 回 `404`；在 workflow 加 `enablement: true` 讓它自行啟用也失敗
  > （`Resource not accessible by integration`，建立 Pages 站台需要 admin 權限）。
  > 因此 Pages 未啟用前，每次推送的 Actions 都會在 `Configure Pages` 這步失敗，屬預期現象。
- [ ] **4. 請她逐頁對照確認**（不可逆關卡）
  - 開兩個視窗，左邊原站 `www.fanfanyeh.net`、右邊新站，逐頁比對有無漏內容
  - 重點：26 個主要頁面、107 張圖、18 個舊文章轉址頁
  - **她確認「內容都在」之後，才可以進行第 5 步**
- [ ] **5. 改 DNS**（需登入 Register.com，帳號在她本人手上）
- [ ] **6. 停掉 Weebly 訂閱**（確認新站在自訂網域上正常運作數日後再停）
- [ ] **7. 刪除原建置位置的備份 repo**（`jesuswaytaipeisrv/yeh`，見下）

### 原建置位置的處置（2026-08-03）

站台原先建在 `jesuswaytaipeisrv/yeh`，其 GitHub Pages 會在
`https://jesuswaytaipeisrv.github.io/yeh/` 放送一份**完全相同的公開複本**。
正式站既已移到 `CCOM`，該複本沒有存在必要，已將 repo 改為 **private**——
免費帳號的 private repo 不能開 Pages，Pages 因此自動停用，公開複本消失。

**刻意先 private 而不直接刪除**：協助者在 `CCOM` 只有 collaborator **write、不是 admin**，
若 `CCOM` 發生誤刪或權限變動，這是 GitHub 上唯一還受控的完整副本。
待第 6 步（停 Weebly）觀察無誤後再刪，即上方第 7 步。

刪除前已確認內容零損失：兩邊 `main` 同為 `d705cf7`、`custom-domain` 同為 `a95955c`，
`git ls-remote` 的 refs 完全一致，舊 repo 的 issues／PR／releases／forks 全部為 0。

### 時程（2026-08-02 確認：Weebly 預計 8 月底停用）

**不要把 DNS 留到 8/31 當天改。** 自訂網域要等 GitHub 跟 Let's Encrypt 申請到憑證才能開啟
Enforce HTTPS，通常幾十分鐘、偶爾要等上一天。若當天才改而憑證卡住，訪客會看到憑證警告，
而那時 Weebly 已停、無法回頭。建議讓 DNS 與 Weebly 有兩週重疊期：

| 時間 | 動作 | 理由 |
|---|---|---|
| 現在 – 8/10 | 第 4 步：逐頁對照確認 | Weebly 還活著，唯一能比對原站的時機 |
| 約 8/15 | 第 5 步：改 DNS + 設自訂網域 | Weebly 仍在，改壞了可以把 DNS 改回去 |
| 8/15 – 8/31 | 觀察憑證、`www` 與根網域、信箱 | 留兩週處理意外 |
| 8/31 | 第 6 步：停 Weebly | 屆時新站已實際運作兩週 |

改 DNS 當天的順序：**先在 Register.com 改好 A 記錄，再回 GitHub Settings → Pages 填自訂網域**。
這樣 GitHub 的網域驗證會立刻通過並開始申請憑證；反過來做會先驗證失敗、白等一輪。

⚠️ **設定自訂網域後，`https://eltha0122-ux.github.io/CCOM/` 會自動轉址到 `fanfanyeh.net`**，
臨時網址等於消失。因此第 4 步的逐頁對照必須在改 DNS 之前完成。

## 第 5 步：DNS 要改什麼

網域 `fanfanyeh.net` 註冊於 **Register.com**（不是 Weebly），登入後改 DNS 設定：

| 記錄 | 現況 | 要改成 |
|---|---|---|
| `@` A 記錄 | `199.34.228.133`（Weebly） | 改為 GitHub Pages 的四筆：`185.199.108.153`、`185.199.109.153`、`185.199.110.153`、`185.199.111.153` |
| `www` | 指向 Weebly | 改為 CNAME 指向 `eltha0122-ux.github.io` |
| `*` 萬用字元 A 記錄 | 指向 Weebly | **建議刪除**。Weebly 停用後該 IP 可能改服務他人 |
| `mail` 子網域 | 指向 Register.com | 註冊時的殘留，不影響收信，可留可刪 |
| **`MX` 五筆（Google）** | 指向 Google | **絕對不要動**，見下 |

> ⚠️ **MX 記錄不可刪**。五筆 MX 指向 Google，代表寄到 `@fanfanyeh.net` 的信會送到 Google，
> 但站上（含原站）出現的信箱全部是 `eltha0122@gmail.com`（89 處），查無任何 `@fanfanyeh.net` 位址，
> 因此無法確認該信箱是否使用中。**確認她沒在用之前一律保留**，刪錯會直接讓信收不到。

另：該網域目前**沒有 SPF／DKIM／DMARC**，代表任何人都能冒用 `@fanfanyeh.net` 寄信。
若確認信箱有在使用，建議補上；若確認沒在使用，建議加一筆 `v=spf1 -all` 擋掉冒名寄信。

**換網址的 commit 已經先做好了，放在 `custom-domain` 分支**（commit `a95955c`，兩邊 repo 都有）：
341 處絕對網址已改指 `https://www.fanfanyeh.net/`、`docs/CNAME` 已產生，靜態檢查與瀏覽器逐頁掃描皆通過。

⚠️ **DNS 生效前不要合併進 `main`。** 這個 commit 一旦部署，
`eltha0122-ux.github.io/CCOM` 就會轉址到自訂網域；DNS 還沒指過來的話兩邊都連不上。

改 DNS 當天的順序：

1. Register.com 改好 A 記錄（見上表）
2. GitHub Settings → Pages 填入自訂網域 `www.fanfanyeh.net`
3. 合併 `custom-domain` 進 `main` 並推送 → Actions 自動部署
4. 等 GitHub 發完 Let's Encrypt 憑證後，勾選 **Enforce HTTPS**

事後若還要再換網址，一律用腳本、不要手改：

```bash
python3 tools/set_site_url.py https://新網址
```

## 費用

| 項目 | 費用 |
|---|---|
| GitHub Pages 託管 | **免費**（public repo） |
| 網域 `fanfanyeh.net` 續約 | 約 US$30–40／年，**2027-03-19 到期**，Register.com 續約價偏高 |
| Weebly 訂閱 | 移轉完成後**可停掉**，這是這次省下來的錢 |

> 續約提醒：到期日前務必確認 Register.com 的自動續約與付款方式，網域過期會直接斷站。
> 若嫌 Register.com 貴，到期前可轉出到其他註冊商（轉出需解除 `clientTransferProhibited` 鎖定）。

## 已知限制與陷阱

- 原本的 Weebly 聯絡表單已改為 `mailto:` 連結，不再蒐集訪客資料。
- 文章頁的臉書／推特分享按鈕仍會載入第三方腳本（`connect.facebook.net`、`platform.twitter.com`），
  是站上唯一的對外連線；若不希望訪客被追蹤，可以移除這兩顆按鈕。
- 18 個轉址頁已自動驗證（全部 200 且指向新站文章頁）。**尚未驗證的是「內容有沒有漏」**：
  107 張圖未逐張與原站目視比對、文章內文未逐段比對——這正是第 4 步要她確認的原因。
- ⚠️ **`work/repair_static_site.py` 不要再執行**。它會依原站重新產生站台，
  執行後會把 Weebly 的外部相依裝回去，並覆蓋 `docs/files/fonts/`、`docs/files/vendor/`
  與 `static-overrides.css` 的本地化成果。
