import json, re, time, html, types, urllib.parse
src = open('fix.py', encoding='utf-8').read().split("data = {s['id']")[0]
mod = types.ModuleType('f'); exec(src, mod.__dict__)
get, search, norm, extract = mod.get, mod.search, mod.norm, mod.extract
TARGET = 300
MIN_CHORDS = 20

ARTISTS = [
  # ארץ ישראל
  ('יהורם גאון','ארץ ישראל',12), ('שושנה דמארי','ארץ ישראל',8), ('יפה ירקוני','ארץ ישראל',8),
  ('הדודאים','ארץ ישראל',10), ('אילנית','ארץ ישראל',8), ('הגבעטרון','ארץ ישראל',8),
  ('להקת הנח"ל','ארץ ישראל',8), ('שלישיית גשר הירקון','ארץ ישראל',5), ('אסתר עופרים','ארץ ישראל',5),
  ('התרנגולים','ארץ ישראל',5), ('חוה אלברשטיין','ארץ ישראל',12), ('אריק איינשטיין','ארץ ישראל',15),
  # מזרחית
  ('זוהר ארגוב','מזרחית',10), ('חיים משה','מזרחית',8), ('אהובה עוזרי','מזרחית',5),
  ('אבי טולדנו','מזרחית',5), ('ישי לוי','מזרחית',5), ('מרגלית צנעני','מזרחית',5),
  ("ג'ו עמר",'מזרחית',4), ('שלמה בר','מזרחית',3),
  # זמר עברי
  ('שלמה ארצי','זמר עברי',8), ('מתי כספי','זמר עברי',8), ('ירדנה ארזי','זמר עברי',6),
  ('עוזי חיטמן','זמר עברי',6), ('ריטה','זמר עברי',4), ('גלי עטרי','זמר עברי',4),
  ('חנן יובל','זמר עברי',4), ('רבקה זוהר','זמר עברי',4), ('אריק לביא','זמר עברי',4),
  ('שמוליק קראוס','זמר עברי',4), ('יגאל בשן','זמר עברי',4), ('ששי קשת','זמר עברי',3),
  ('יהודית רביץ','זמר עברי',4), ('גידי גוב','זמר עברי',4), ('שלום חנוך','זמר עברי',4),
  ('צביקה פיק','זמר עברי',4), ('שלמה גרוניך','זמר עברי',3), ('נורית גלרון','זמר עברי',3),
  ('יזהר כהן','זמר עברי',3), ('רמי קלינשטיין','זמר עברי',3),
]

def decode(slug): return html.unescape(urllib.parse.unquote(slug)).replace('_', ' ')

def artist_page(name):
    h = get('https://www.tab4u.com/resultsSimple?tab=songs&q=' + urllib.parse.quote(name)); time.sleep(1)
    for aid, slug in re.findall(r'artists/(\d+)_([^"\'#?]+)\.html', h):
        if norm(decode(slug)) == norm(name):
            return f'https://www.tab4u.com/tabs/artists/{aid}_{slug}.html'
    for sid, a, t in search(name):
        if norm(a) == norm(name):
            hh = get(f'https://www.tab4u.com/tabs/songs/{sid}_song.html'); time.sleep(1)
            for aid, slug in re.findall(r'artists/(\d+)_([^"\'#?]+)\.html', hh):
                if norm(decode(slug)) == norm(name):
                    return f'https://www.tab4u.com/tabs/artists/{aid}_{slug}.html'
            break
    return None

def artist_songs(url, name):
    h = get(url); time.sleep(1)
    out, seen = [], set()
    for sid, slug in re.findall(r'songs/(\d+)_([^"\'#?]+)\.html', h):
        if sid in seen: continue
        seen.add(sid)
        s = decode(slug)
        if ' - ' not in s: continue
        a, t = s.split(' - ', 1)
        if norm(name) in norm(a): out.append((int(sid), a.strip(), t.strip()))
    return out

data = {s['id']: s for s in json.load(open('data.json', encoding='utf-8'))}
# regroup the small "עוד בסגנון" shelf into the new shelves
for s in data.values():
    if 'עוד בסגנון' in s['cats']:
        s['cats'].remove('עוד בסגנון')
        s['cats'].append({1165: 'ארץ ישראל', 77298: 'זמר עברי'}.get(s['id'], 'מזרחית'))
titles = {norm(s['title']) for s in data.values()}

for name, cat, n in ARTISTS:
    if len(data) >= TARGET: break
    url = artist_page(name)
    if not url: print('NO ARTIST PAGE', name, flush=True); continue
    added = 0
    for sid, a, t in artist_songs(url, name):
        if added >= n or len(data) >= TARGET: break
        if sid in data:
            if cat not in data[sid]['cats']: data[sid]['cats'].append(cat)
            continue
        if norm(t) in titles: continue
        secs = extract(sid); time.sleep(1)
        cnt = sum(len(l['c']) for x in (secs or []) for l in x['lines'])
        if not secs or cnt < MIN_CHORDS: continue
        a = a.replace('בעז שרעבי', 'בועז שרעבי').replace('עפרה חזה', 'עופרה חזה')
        data[sid] = {'id': sid, 'title': t, 'artist': a, 'cats': [cat], 'sections': secs}
        titles.add(norm(t)); added += 1
    print(f'{name}: +{added} (total {len(data)})', flush=True)
    json.dump(list(data.values()), open('data.json', 'w', encoding='utf-8'), ensure_ascii=False)

json.dump(list(data.values()), open('data.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('DONE', len(data))
