import re,html
TOK=re.compile(r'(<!--.*?-->|<[^>]+>)',re.S)
SKIP=re.compile(r'^[\d\s.,/%#·–—+×:()\-*]*$')
ATTR=re.compile(r'\b(aria-label|placeholder|title|alt)="([^"]*)"')
KEEP={'知用','Claude','ChatGPT','DeepSeek','Gemini','Kimi','Perplexity','Felo','Manus','Grok Bot','Muse','Cursor','Claude Code','GitHub Copilot','Windsurf','Trae','Midjourney','Ideogram','Stable Diffusion','Runway','Sora','Pika','claude.ai','Lin W.','Zhou Y.','Kai','Chen M.','Mia','中文','/ Claude'}
def walk(s,fn_text,fn_attr):
    parts=TOK.split(s); out=[]; skip=False
    for p in parts:
        if p.startswith('<') and TOK.fullmatch(p):
            low=p.lower()
            if low.startswith('<script') or low.startswith('<style'): skip=True
            elif low.startswith('</script') or low.startswith('</style'): skip=False
            if low.startswith('<meta') and 'name="description"' not in low: out.append(p); continue
            p=re.sub(r'\b(aria-label|placeholder|title|alt|content)="([^"]*)"',lambda m:f'{m.group(1)}="{fn_attr(m.group(2))}"' if m.group(1)!='content' or 'name="description"' in low else m.group(0),p)
            out.append(p)
        elif skip or not p.strip(): out.append(p)
        else:
            m=re.match(r'^(\s*)(.*?)(\s*)$',p,re.S)
            out.append(m.group(1)+fn_text(m.group(2))+m.group(3))
    return ''.join(out)
def collect(s):
    found=[]
    def t(x):
        u=html.unescape(x).strip()
        if u and not SKIP.match(u) and u not in KEEP and u not in found: found.append(u)
        return x
    walk(s,t,t); return found
