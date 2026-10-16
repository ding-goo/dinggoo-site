"""DING GOO's public pages for GitHub Pages:  python3 build.py

  source/privacy-policy.ar.md + .en.md → privacy/index.html   (the app opens https://dinggoo.app/privacy)
  source/terms.ar.md + .en.md          → terms/index.html
  (written here, Arabic + English)     → support/index.html, index.html

The Arabic texts are the approved ones, copied from the app project (docs/privacy/); the English is a translation
of them. Edit the texts in source/, never the HTML, then run this again. Plain static files: no scripts, no
analytics, no outside fonts (Tajawal is hosted here, under its OFL licence in fonts/). Contact: support@dinggoo.app.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "source"
DOMAIN = "dinggoo.app"
EMAIL = "support@dinggoo.app"

# DING GOO's colours (design/tokens.json in the app project), light and dark
CSS = """
@font-face{font-family:"Tajawal";src:url("/fonts/Tajawal-Regular.ttf") format("truetype");font-weight:400;font-display:swap}
@font-face{font-family:"Tajawal";src:url("/fonts/Tajawal-Bold.ttf") format("truetype");font-weight:700;font-display:swap}
:root{--bg:#FCFAF7;--card:#FFFFFF;--ink:#1E1B3A;--muted:#6B6785;--line:#ECE8F3;--accent:#6346E8;--tint:#EFEBFF;--on-accent:#FFFFFF}
@media (prefers-color-scheme:dark){:root{--bg:#15131F;--card:#1F1C2E;--ink:#F3F1FA;--muted:#A9A5C0;--line:#34304A;--accent:#9C88FF;--tint:#2E2752;--on-accent:#15131F}}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.8 "Tajawal",-apple-system,"SF Arabic","Geeza Pro","Segoe UI",Tahoma,sans-serif}
main{max-width:760px;margin:0 auto;padding:24px 16px 48px}
.top{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:8px}
.brand{color:var(--accent);font-weight:700;letter-spacing:.5px;text-decoration:none;font-size:18px}
.lang{display:inline-block;padding:6px 14px;border-radius:999px;background:var(--tint);color:var(--accent);font-weight:700;font-size:15px;text-decoration:none}
article{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:20px 20px 8px;margin:16px 0}
h1{font-size:26px;line-height:1.4;margin:4px 0 8px}
h2{font-size:19px;line-height:1.5;margin:28px 0 6px;color:var(--accent)}
p,li{color:var(--ink);overflow-wrap:anywhere}
.meta{color:var(--muted);font-size:15px}
ul{padding-inline-start:22px;margin:6px 0}
li{margin:6px 0}
a{color:var(--accent)}
.hero{text-align:center;padding:32px 20px}
.hero h1{font-size:34px;margin:0 0 6px;color:var(--accent);letter-spacing:1px}
.hero p{margin:4px 0;font-size:18px}
.links{display:flex;flex-wrap:wrap;justify-content:center;gap:10px;margin-top:20px}
.links a{display:inline-block;padding:10px 20px;border-radius:999px;background:var(--accent);color:var(--on-accent);font-weight:700;text-decoration:none}
footer{margin-top:32px;padding-top:16px;border-top:1px solid var(--line);color:var(--muted);font-size:15px;text-align:center}
footer a{margin:0 8px}
"""


def inline(text: str) -> str:
    """Escapes, then links only our own addresses: the support email and pages of dinggoo.app."""
    out = html.escape(text, quote=False)
    out = re.sub(rf"https://{re.escape(DOMAIN)}(/[a-z]*)?", lambda m: f'<a href="{m.group(1) or "/"}">{m.group(0)}</a>', out)
    return out.replace(EMAIL, f'<a href="mailto:{EMAIL}">{EMAIL}</a>')


META = ("آخر تحديث:", "مقدّم الخدمة:", "للتواصل:", "Last updated:", "Service provider:", "Contact:")


def body_of(text: str) -> tuple[str, str]:
    """Plain lines: a title, then blocks separated by blank lines. A short line alone is a heading, "- " lines are a
    list, «1. الخدمة» / "1. The service" starts a numbered heading with its paragraph under it."""
    lines = text.strip().splitlines()
    title, blocks, cur = lines[0].strip(), [], []
    for line in lines[1:] + [""]:
        if line.strip():
            cur.append(line.strip())
        elif cur:
            blocks.append(cur)
            cur = []
    parts = []
    for b in blocks:
        if any(l.startswith(META) for l in b):
            parts.append('<p class="meta">' + "<br>".join(inline(l) for l in b) + "</p>")
            continue
        if re.match(r"^\d+\. \S", b[0]):
            parts.append(f"<h2>{inline(b[0])}</h2>")
            b = b[1:]
        elif len(b) == 1 and not b[0].startswith("- ") and len(b[0]) < 60 and not b[0].endswith((".", ":", "؟", "?")):
            parts.append(f"<h2>{inline(b[0])}</h2>")
            continue
        items = [l for l in b if l.startswith("- ")]
        if items:
            parts.append("<ul>" + "".join(f"<li>{inline(l[2:])}</li>" for l in items) + "</ul>")
        parts += [f"<p>{inline(l)}</p>" for l in b if not l.startswith("- ")]
    return title, "\n".join(parts)


def article(text: str, lang: str) -> tuple[str, str]:
    title, body = body_of(text)
    direction = "rtl" if lang == "ar" else "ltr"
    return title, f'<article id="{lang}" lang="{lang}" dir="{direction}">\n<h1>{html.escape(title)}</h1>\n{body}\n</article>'


FOOTER = ('<footer><a href="/privacy/">الخصوصية · Privacy</a><a href="/terms/">الشروط · Terms</a>'
          f'<a href="/support/">الدعم · Support</a><br><a href="mailto:{EMAIL}">{EMAIL}</a></footer>')


def page(title: str, path: str, content: str, english_link: bool = True) -> str:
    switch = '<a class="lang" href="#en" lang="en">English</a>' if english_link else ""
    return f"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="referrer" content="no-referrer">
<meta name="color-scheme" content="light dark">
<title>{html.escape(title)}</title>
<link rel="canonical" href="https://{DOMAIN}{path}">
<style>{CSS}</style>
</head>
<body>
<main>
<div class="top"><a class="brand" href="/">DING GOO</a>{switch}</div>
{content}
{FOOTER}
</main>
</body>
</html>
"""


def bilingual(name: str, path: str) -> str:
    ar_title, ar = article((SRC / f"{name}.ar.md").read_text(encoding="utf-8"), "ar")
    _, en = article((SRC / f"{name}.en.md").read_text(encoding="utf-8"), "en")
    return page(ar_title, path, ar + "\n" + en)


SUPPORT_AR = f"""دعم دينغ غو (DING GOO)

للتواصل: {EMAIL}

اكتب لنا من البريد المسجّل في حسابك، ولا ترسل صور أطفالك أو رسائل المدرسة كاملة.


حذف الحساب

- من التطبيق: الإعدادات ⚙️ ← «حذف الحساب». تُلغى كل الجلسات فوراً، وتُمحى بيانات العائلة خلال ساعة.
- لا تحتاج مراسلتنا لذلك. وإن لم تستطع الدخول، راسلنا من بريدك المسجّل.


الاشتراك

- الإدارة والإلغاء: من «إدارة الاشتراك» في التطبيق، أو من إعدادات Apple ID على جهازك.
- اشتريت ولم يظهر الاشتراك: «استعادة المشتريات» في شاشة الاشتراك.
- الاسترداد: تتولاه Apple وفق سياساتها.


جهاز الطفل

- من جهاز ولي الأمر: «ربط جهاز» للطفل، ثم امسح رمز QR بجهاز الطفل، أو افتح عليه رابط الربط.
- يصلك تنبيه كلما رُبط جهاز جديد بحساب طفلك. ويمكنك إلغاء ربط أي جهاز في أي وقت.
"""

SUPPORT_EN = f"""DING GOO Support

Contact: {EMAIL}

Write to us from the email registered to your account, and do not send photos of your children or whole school messages.


Deleting your account

- In the app: Settings ⚙️ → "Delete account". All sessions are cancelled immediately, and the family's data is erased within one hour.
- You do not need to write to us for that. If you cannot sign in, write to us from your registered email.


Subscription

- Managing and cancelling: from "Manage subscription" in the app, or from the Apple ID settings on your device.
- You paid but the subscription does not show: "Restore purchases" on the subscription screen.
- Refunds: handled by Apple under its policies.


Your child's device

- From the parent's device: "Link device" for the child, then scan the QR code with the child's device, or open the linking link on it.
- You get a notification whenever a new device is linked to your child's account. You can unlink any device at any time.
"""


def index() -> str:
    content = f"""<article class="hero" lang="ar" dir="rtl">
<h1>DING GOO</h1>
<p>يحوّل رسائل المدرسة إلى مهام منظّمة لكل طفل، على iPhone و iPad.</p>
<p class="meta" lang="en" dir="ltr">Turns school messages into organised tasks for each child, on iPhone and iPad.</p>
<div class="links">
<a href="/privacy/">سياسة الخصوصية · Privacy</a>
<a href="/terms/">شروط الاستخدام · Terms</a>
<a href="/support/">الدعم · Support</a>
</div>
</article>"""
    return page("DING GOO — دينغ غو", "/", content, english_link=False)


def build(out: Path = ROOT) -> list[str]:
    files = {
        "index.html": index(),
        "privacy/index.html": bilingual("privacy-policy", "/privacy"),
        "terms/index.html": bilingual("terms", "/terms"),
        "support/index.html": page("دعم دينغ غو · DING GOO Support", "/support",
                                   article(SUPPORT_AR, "ar")[1] + "\n" + article(SUPPORT_EN, "en")[1]),
        "CNAME": DOMAIN + "\n",                     # GitHub Pages: the custom domain
        ".nojekyll": "",                               # serve the files exactly as they are
    }
    for rel, content in files.items():
        f = out / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(content, encoding="utf-8")
    return list(files)


if __name__ == "__main__":
    print("✅", ", ".join(build()))
