#!/usr/bin/env bash
set -euo pipefail

source_dir="work/reference/www.fanfanyeh.net"
target_dir="docs"

mkdir -p "$target_dir"
cp -R "$source_dir"/. "$target_dir"/

# Weebly uses HTML-encoded quote marks in inline background URLs. Replace them
# with normal site-relative paths suitable for GitHub Pages.
for page in docs/*.html; do
  perl -0pi -e 's#https://www\.fanfanyeh\.net/&quot;/(uploads/[^&]+)&quot;#$1#g' "$page"
done

# Replace Cloudflare-protected email links with a normal email link because the
# GitHub Pages copy does not run behind the original Cloudflare configuration.
find docs -name '*.html' -type f -print0 | while IFS= read -r -d '' page; do
  perl -0pi -e 's#https://www\.fanfanyeh\.net/cdn-cgi/l/email-protection(?:\#[^"<> ]+)?#mailto:eltha0122\@gmail.com#g' "$page"
  perl -0pi -e 's~<a href="mailto:eltha0122\@gmail\.com" class="__cf_email__"[^>]*>\[email&#160;protected\]</a>~<a href="mailto:eltha0122\@gmail.com">eltha0122\@gmail.com</a>~g' "$page"
  perl -0pi -e 's~</head>~<style>.email-contact{max-width:760px;margin:40px auto;padding:42px;border:1px solid #ddd;background:#faf9f6;text-align:center}.email-contact h2{margin:0 0 18px}.email-contact p{line-height:1.8}.email-contact__button{display:inline-block;margin:20px 0 10px;padding:14px 24px;background:#3f3f3f;color:#fff!important;text-decoration:none;letter-spacing:.04em}.email-contact__button:hover,.email-contact__button:focus{background:#666}.email-contact__note{font-size:14px;color:#666}\@media(max-width:600px){.email-contact{margin:24px 0;padding:28px 18px}.email-contact__button{display:block;overflow-wrap:anywhere}}</style>\n</head>~' "$page"
done

# The original Weebly form requires Weebly hosting. Replace it with a simple,
# privacy-friendly email contact card.
perl -0pi -e 's#<form enctype="multipart/form-data".*?</form>\s*<div id="g-recaptcha-[^>]+></div>#<section class="email-contact" aria-labelledby="email-contact-title">\n<h2 id="email-contact-title">洽詢合作服務</h2>\n<p>請以 Email 說明公司名稱、聯絡人、希望討論的議題與預期合作方式，如凡將於收到信件後與您聯繫。</p>\n<a class="email-contact__button" href="mailto:eltha0122\@gmail.com?subject=%E5%90%88%E4%BD%9C%E6%B4%BD%E8%A9%A2%EF%BD%9C%E5%85%AC%E5%8F%B8%E5%90%8D%E7%A8%B1">Email 洽詢：eltha0122\@gmail.com</a>\n<p class="email-contact__note">點擊按鈕會開啟您裝置上的預設郵件程式。</p>\n</section>#s' docs/inquiry.html

# Disable the remaining Weebly-hosted forms. The static copy must not collect
# visitor data through form endpoints that are controlled by the old host.
perl -0pi -e 's#<form enctype="multipart/form-data"[^>]*id="form-495892663918342574".*?</form>\s*<div id="g-recaptcha-495892663918342574"[^>]*></div>#<section class="email-contact" aria-labelledby="course-contact-title">\n<h2 id="course-contact-title">【預防霸凌溝通力】課程洽詢</h2>\n<p>請以 Email 說明公司名稱、聯絡人、預計日期、人數、時數與其他課程需求。</p>\n<a class="email-contact__button" href="mailto:eltha0122\@gmail.com?subject=%E9%A0%90%E9%98%B2%E9%9C%B8%E5%87%8C%E6%BA%9D%E9%80%9A%E5%8A%9B%E8%AA%B2%E7%A8%8B%E6%B4%BD%E8%A9%A2">Email 洽詢：eltha0122\@gmail.com</a>\n<p class="email-contact__note">本靜態網站不會蒐集或儲存表單資料。</p>\n</section>#s' docs/bullying-prevention-training.html

find docs -name '*.html' -type f -print0 | while IFS= read -r -d '' page; do
  perl -0pi -e 's#<form enctype="multipart/form-data"[^>]*id="form-382051188821923108".*?</form>\s*<div id="g-recaptcha-382051188821923108"[^>]*></div>#<section class="email-contact" aria-label="電子報訂閱狀態">\n<p>此靜態網站目前未提供電子報訂閱；如需聯絡，請使用 <a href="mailto:eltha0122\@gmail.com">Email</a>。</p>\n</section>#s' "$page"
done

touch docs/.nojekyll

# Make the archive independent from Weebly slideshow/comment endpoints, repair
# metadata and legacy URLs, and download slideshow images while the source site
# is still available.
python3 work/repair_static_site.py \
  --docs "$target_dir" \
  --base-url "https://eltha0122-ux.github.io/CCOM/" \
  --download-images
