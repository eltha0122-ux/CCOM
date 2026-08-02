# 移交說明（fanfanyeh.net → GitHub Pages）

原站 `www.fanfanyeh.net` 建在 Weebly，空間即將到期。本專案把整站爬成純靜態 HTML，
改放 GitHub Pages（免費），並已移除所有 Weebly 相依，可獨立運作。

本檔記錄移交的進度與剩餘步驟。技術細節見 `README.md`，完整開發過程見 `DEVELOPMENT_LOG.md`。

## 現況

| 項目 | 狀態 |
|---|---|
| 站台內容 | 44 個 HTML、107 張圖，已完全脫離 Weebly |
| 新家 | `https://github.com/eltha0122-ux/CCOM`（葉如凡本人帳號，public） |
| 新網址 | `https://eltha0122-ux.github.io/CCOM/`（站內絕對網址已全部換成這個） |
| 原建置位置 | `https://github.com/jesuswaytaipeisrv/yeh`（保留為備份，不再是正式站） |
| 網域 | `fanfanyeh.net` 仍指向 Weebly，**尚未變更** |
| 離線備份 | `yeh-網站移轉包.zip`（232 檔，與 repo 內容相同） |

## 移轉步驟與進度

順序不可跳，尤其第 4 步是唯一不可逆的關卡——**改 DNS 之前，Weebly 必須還活著**，
否則無法回頭比對原站內容。

- [x] **1. 站台靜態化**：移除 Weebly 的 CSS／JS／輪播／圖示字型與平台級 Google Analytics，
      jQuery 與字型改為自帶（MIT／OFL 授權）。
- [x] **2. 換成新網址**：`python3 tools/set_site_url.py https://eltha0122-ux.github.io/CCOM/`
      已執行，47 個檔案共 341 處絕對網址（canonical、og:url、sitemap、robots、RSS）皆已更新。
- [ ] **3. 推上她的 repo 並上線**
  - 她到 `CCOM` repo 的 Settings → Collaborators 邀請協助者帳號（`jesuswaytaipeisrv`）
  - 推送 `main` 分支
  - 她到 Settings → Pages 把 **Source 設為 GitHub Actions**（此步驟只有 repo 擁有者能做）
  - 等 Actions 跑完，確認 `https://eltha0122-ux.github.io/CCOM/` 開得起來
- [ ] **4. 請她逐頁對照確認**（不可逆關卡）
  - 開兩個視窗，左邊原站 `www.fanfanyeh.net`、右邊新站，逐頁比對有無漏內容
  - 重點：26 個主要頁面、107 張圖、18 個舊文章轉址頁
  - **她確認「內容都在」之後，才可以進行第 5 步**
- [ ] **5. 改 DNS**（需登入 Register.com，帳號在她本人手上）
- [ ] **6. 停掉 Weebly 訂閱**（確認新站在自訂網域上正常運作數日後再停）

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

DNS 改完後，回 GitHub repo 的 Settings → Pages 填入自訂網域，並重跑一次：

```bash
python3 tools/set_site_url.py https://www.fanfanyeh.net/
```

（腳本會一併產生 `docs/CNAME`，commit 推上去即可。）

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
- 尚未逐一驗證的部分：107 張圖未逐張目視、18 個轉址頁未逐一點擊——這正是第 4 步要她確認的原因。
- ⚠️ **`work/repair_static_site.py` 不要再執行**。它會依原站重新產生站台，
  執行後會把 Weebly 的外部相依裝回去，並覆蓋 `docs/files/fonts/`、`docs/files/vendor/`
  與 `static-overrides.css` 的本地化成果。
