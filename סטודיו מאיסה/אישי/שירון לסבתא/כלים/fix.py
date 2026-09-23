import json, re, time, html
import importlib.util, sys, types
# reuse helpers from scrape.py without running its main loop
src = open('scrape.py', encoding='utf-8').read().split('out={};log=[]')[0]
mod = types.ModuleType('s'); exec(src, mod.__dict__)
get, search, norm, clean, label_of, rep_of, CH = mod.get, mod.search, mod.norm, mod.clean, mod.label_of, mod.rep_of, mod.CH

def extract(sid):
    h = get(f'https://www.tab4u.com/tabs/songs/{sid}_song.html')
    i = h.find('id="songContentTPL"')
    if i < 0: return None
    body = h[i:]
    for marker in ('id="ratingWrap"', 'id="downInSongTable"'):
        j = body.find(marker)
        if j > 0: body = body[:j]
    secs = []
    for tb in re.finditer(r'<table[^>]*>(.*?)</table>', body, re.S):
        rows = re.findall(r'<td class="(chords|song)">(.*?)</td>', tb.group(1), re.S)
        if not rows: continue          # guitar-tab tables, ads: skip, keep reading
        sec = {'label': None, 'lines': []}
        for kind, content in rows:
            if kind == 'chords':
                ch = [c for c in (clean(x) for x in CH.findall(content)) if c]
                if ch: sec['lines'].append({'c': ch, 'i': True, 'r': rep_of(clean(CH.sub('', content)))})
            else:
                t = clean(content)
                if not t: continue
                L = label_of(t)
                if L:
                    if not sec['label'] and not sec['lines']: sec['label'] = L
                    elif sec['lines'] and rep_of(t): sec['lines'][-1]['r'] = rep_of(t)
                    continue
                if re.fullmatch(r'[xX]?\s?\d\s?[xX]?', t):
                    if sec['lines']: sec['lines'][-1]['r'] = rep_of(t)
                    continue
                if sec['lines']: sec['lines'][-1]['i'] = False
        if sec['lines']: secs.append(sec)
    return secs

data = {s['id']: s for s in json.load(open('data.json', encoding='utf-8'))}
for sid in (2027, 72977, 303, 67303, 2313, 72766):
    data.pop(sid, None)

thin = [s for s in data.values() if sum(len(l['c']) for x in s['sections'] for l in x['lines']) < 30]
for s in thin:
    secs = extract(s['id']); time.sleep(1)
    n = sum(len(l['c']) for x in (secs or []) for l in x['lines'])
    print(f"REDO {s['id']} {s['title']}: {sum(len(l['c']) for x in s['sections'] for l in x['lines'])} -> {n}")
    if secs and n >= 4: s['sections'] = secs

adds = [
    ('ארץ ישראל', 'ציפור קטנה בלב', 'יגאל בשן'),
    ('עוד בסגנון', 'אצלנו בכפר טודרא', 'שלמה בר'),
    ('ארץ ישראל', 'באב אל ווד', 'שלמה גרוניך'),
    ('ארץ ישראל', 'הנה מה טוב', 'עממי'),
    ('ארץ ישראל', 'פרחים בקנה', 'להקת חיל התותחנים'),
    ('ארץ ישראל', 'תפוח חינני', 'הדודאים'),
    ('ראש השנה', 'אדון עולם', 'עוזי חיטמן'),
    ('ארץ ישראל', 'עוד יבוא שלום עלינו', ''),
]
for cat, q, hint in adds:
    res = search(q); time.sleep(1)
    cand = [r for r in res if norm(r[2]) == norm(q)]
    if hint: cand = [r for r in cand if norm(hint) in norm(r[1])] or cand
    if not cand: print('MISS', q); continue
    sid, artist, title = cand[0]
    if sid in data:
        if cat not in data[sid]['cats']: data[sid]['cats'].append(cat)
        continue
    secs = extract(sid); time.sleep(1)
    n = sum(len(l['c']) for x in (secs or []) for l in x['lines'])
    if not secs or n < 4: print('EMPTY', sid, title); continue
    data[sid] = {'id': sid, 'title': title, 'artist': artist, 'cats': [cat], 'sections': secs}
    print(f'ADD {sid} {artist} - {title} ({n} chords)')

# Liora's kids Rosh Hashana song by id
sid = 1775
if sid not in data:
    secs = extract(sid)
    if secs: data[sid] = {'id': sid, 'title': 'בראש השנה', 'artist': 'ליאורה', 'cats': ['ראש השנה'], 'sections': secs}; print('ADD 1775 ליאורה - בראש השנה')

# artist names missing for id-based entries
for s in data.values():
    if not s.get('artist'):
        h = get(f"https://www.tab4u.com/tabs/songs/{s['id']}_song.html"); time.sleep(.5)
        m = re.search(r'אקורדים לשיר (.*?) - (.*?)(?: \||</title>)', h)
        if m: s['artist'] = html.unescape(m.group(2)).strip()

# Tab4u spells the name בעז; show it the familiar way
for s in data.values():
    if s.get('artist'): s['artist'] = s['artist'].replace('בעז שרעבי', 'בועז שרעבי').replace('עפרה חזה', 'עופרה חזה')

json.dump(list(data.values()), open('data.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('TOTAL', len(data), 'missing artist:', [s['id'] for s in data.values() if not s.get('artist')])
