"""Generate translated pages from the English templates and add a 10-language switcher.

Usage: python3 build.py <repo>
"""
import html, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from tok import walk

R = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
PAGES = ['index', 'detail', 'review']
# code, dir ('' = repo root), html lang, native name, short label
LANGS = [
    ('zh', '', 'zh-CN', '简体中文', '中文'),
    ('en', 'en', 'en', 'English', 'EN'),
    ('es', 'es', 'es', 'Español', 'ES'),
    ('pt', 'pt', 'pt-BR', 'Português', 'PT'),
    ('fr', 'fr', 'fr', 'Français', 'FR'),
    ('de', 'de', 'de', 'Deutsch', 'DE'),
    ('ja', 'ja', 'ja', '日本語', '日本語'),
    ('ko', 'ko', 'ko', '한국어', '한국어'),
    ('ar', 'ar', 'ar', 'العربية', 'العربية'),
    ('id', 'id', 'id', 'Bahasa Indonesia', 'ID'),
]
EXTRA_FONTS = {
    'ja': '&amp;family=Noto+Serif+JP:wght@700;900',
    'ko': '&amp;family=Noto+Serif+KR:wght@700;900',
    'ar': '&amp;family=Noto+Naskh+Arabic:wght@700&amp;family=Noto+Sans+Arabic:wght@400;600',
}
GLOBE = ('<svg class="i" viewBox="0 0 24 24" aria-hidden="true" style="width:15px;height:15px">'
         '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.7 3.8 5.7 3.8 9s-1.3 6.3-3.8 9c-2.5-2.7-3.8-5.7-3.8-9S9.5 5.7 12 3z"/></svg>')

en_strings = json.load(open(f'{HERE}/en.json'))
EN_TO_ID = {v: k for k, v in en_strings.items()}


def href(from_dir, to_dir, page):
    up = '../' if from_dir else ''
    return f'{up}{to_dir + "/" if to_dir else ""}{page}.html'


def switcher(cur, page):
    code, d, lang, name, short = cur
    items = []
    for c2, d2, l2, n2, s2 in LANGS:
        cur_attr = ' aria-current="page"' if c2 == code else ''
        items.append(f'<li><a href="{href(d, d2, page)}" lang="{l2}" hreflang="{l2}"{cur_attr}>{n2}</a></li>')
    return (f'<details class="langs"><summary aria-label="Language · 语言">{GLOBE}<span>{short}</span></summary>'
            f'<ul>{"".join(items)}</ul></details>')


def alternates(cur, page):
    d = cur[1]
    return '\n'.join(f'<link rel="alternate" hreflang="{l2}" href="{href(d, d2, page)}">' for _, d2, l2, _, _ in LANGS)


def chrome(s, cur, page):
    """Language switcher + hreflang alternates; idempotent."""
    s = re.sub(r'<a class="lang"[^>]*>.*?</a>|<details class="langs">.*?</details>', lambda m: switcher(cur, page), s, count=1, flags=re.S)
    s = re.sub(r'<link rel="alternate"[^>]*>\n', '', s)
    s = s.replace('</title>\n', '</title>\n' + alternates(cur, page) + '\n', 1)
    return s


def translate(s, T, cur):
    code, d, lang, _, _ = cur

    def tr(x):
        u = html.unescape(x).strip()
        k = EN_TO_ID.get(u)
        if k is not None and k in T:
            return html.escape(T[k], quote=False)
        return x

    def tr_attr(x):
        u = html.unescape(x)
        k = EN_TO_ID.get(u)
        return html.escape(T[k], quote=True) if k is not None and k in T else x

    s = walk(s, tr, tr_attr)
    s = s.replace('<html lang="en">', f'<html lang="{lang}"' + (' dir="rtl"' if code == 'ar' else '') + '>', 1)
    if code in EXTRA_FONTS:
        s = s.replace('&amp;display=swap', EXTRA_FONTS[code] + '&amp;display=swap', 1)
        s = s.replace('&display=swap', EXTRA_FONTS[code].replace('&amp;', '&') + '&display=swap', 1)
    js = {
        "'Choose a score.'": 'j0', "'no score chosen'": 'j1',
        "'Add a bit more detail: at least 80 characters about the task and the result.'": 'j2',
        "'review too short'": 'j3', "'Confirm this is your own experience.'": 'j4', "'confirmation not ticked'": 'j5',
    }
    for lit, k in js.items():
        s = s.replace(lit, json.dumps(T[k], ensure_ascii=False))
    s = s.replace("errs.length+(errs.length>1?' things':' thing')+' to fix: '",
                  json.dumps(T['j6'], ensure_ascii=False) + ".replace('{n}',errs.length)")
    return s


missing = {}
for cur in LANGS:
    code, d = cur[0], cur[1]
    T = json.load(open(f'{HERE}/{code}.json')) if code not in ('zh', 'en') else None
    if T is not None:
        miss = [k for k in en_strings if k not in T and not en_strings[k].strip().isdigit()]
        missing[code] = miss
        os.makedirs(f'{R}/{d}', exist_ok=True)
    for p in PAGES:
        if T is None:
            path = f'{R}/{d + "/" if d else ""}{p}.html'
            s = open(path).read()
        else:
            s = translate(open(f'{R}/en/{p}.html').read(), T, cur)
            path = f'{R}/{d}/{p}.html'
        open(path, 'w').write(chrome(s, cur, p))
print('missing keys (left in English):', {k: v for k, v in missing.items() if v})
