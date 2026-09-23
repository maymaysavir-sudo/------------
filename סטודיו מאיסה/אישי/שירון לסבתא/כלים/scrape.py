import urllib.request, urllib.parse, re, html, json, time, sys
UA={'User-Agent':'Mozilla/5.0 (personal songbook)'}
def get(url):
    for _ in range(3):
        try:
            return urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=25).read().decode('utf-8','ignore')
        except Exception:
            time.sleep(3)
    return ''
def norm(s):
    return re.sub(r'[\'"`׳״\-\s,.!?]','',html.unescape(s))
def search(q):
    h=get('https://www.tab4u.com/resultsSimple?tab=songs&q='+urllib.parse.quote(q))
    res=[];seen=set()
    for _,sid,slug in re.findall(r'href="([^"]*songs/(\d+)_([^"]*)\.html)"',h):
        if sid in seen: continue
        seen.add(sid)
        s=html.unescape(urllib.parse.unquote(slug)).replace('_',' ')
        a,t=(s.split(' - ',1)+[''])[:2] if ' - ' in s else ('',s)
        res.append((int(sid),a.strip(),t.strip()))
    return res
CH=re.compile(r'<span[^>]*class="c_C"[^>]*>(.*?)</span>',re.S)
LABELS=['פזמון','פתיחה','מעבר','סיום','בית','סולו','גשר','דקלום','בדקלום','נגינה','קדם פזמון','אינטרו','ביניים']
def clean(x): return html.unescape(re.sub(r'<[^>]+>','',x)).replace('\xa0',' ').strip()
def label_of(t):
    t2=re.sub(r'[:\-\s]*(x\s?\d|\d\s?x)?\s*$','',t).strip().strip(':').strip()
    if len(t)>20: return None
    for L in LABELS:
        if t2==L or re.fullmatch(L+r'\s?[\d\'אבגד]{0,2}',t2): return 'דקלום' if L=='בדקלום' else L
    return None
def rep_of(t):
    m=re.search(r'(?:x\s?(\d)|(\d)\s?x)',t)
    return int(m.group(1) or m.group(2)) if m else 0
def extract(sid):
    h=get(f'https://www.tab4u.com/tabs/songs/{sid}_song.html')
    i=h.find('id="songContentTPL"')
    if i<0: return None
    body=h[i:]
    secs=[];started=False
    for tb in re.finditer(r'<table[^>]*>(.*?)</table>',body,re.S):
        rows=re.findall(r'<td class="(chords|song)">(.*?)</td>',tb.group(1),re.S)
        if not rows:
            if started: break
            continue
        started=True
        sec={'label':None,'lines':[]}
        for kind,content in rows:
            if kind=='chords':
                ch=[clean(c) for c in CH.findall(content)]
                ch=[c for c in ch if c]
                rest=clean(CH.sub('',content))
                if ch: sec['lines'].append({'c':ch,'i':True,'r':rep_of(rest)})
            else:
                t=clean(content)
                if not t: continue
                L=label_of(t)
                if L:
                    if not sec['label'] and not sec['lines']: sec['label']=L
                    elif sec['lines'] and rep_of(t): sec['lines'][-1]['r']=rep_of(t)
                    continue
                if re.fullmatch(r'[xX]?\s?\d\s?[xX]?',t):
                    if sec['lines']: sec['lines'][-1]['r']=rep_of(t)
                    continue
                if sec['lines']: sec['lines'][-1]['i']=False
        if sec['lines']: secs.append(sec)
    m=re.search(r'<title>(.*?)</title>',h,re.S)
    return secs
out={};log=[]
for line in open('songs.txt',encoding='utf-8'):
    line=line.strip()
    if not line or line.startswith('#'): continue
    cats,q,hint=(line.split('|')+['',''])[:3]
    cats=cats.split(',')
    if q.startswith('#'):
        sid=int(q[1:]);title=hint;artist=None
    else:
        res=search(q);time.sleep(1)
        cand=[r for r in res if norm(r[2])==norm(q)]
        if hint: cand=sorted(cand,key=lambda r: 0 if norm(hint) in norm(r[1]) else 1)
        if not cand:
            log.append(f'MISS {q}: '+'; '.join(f'{r[1]} - {r[2]}' for r in res[:4])); continue
        sid,artist,title=cand[0]
    if sid in out:
        for c in cats:
            if c not in out[sid]['cats']: out[sid]['cats'].append(c)
        continue
    secs=extract(sid);time.sleep(1)
    if not secs:
        log.append(f'EMPTY {sid} {title}'); continue
    out[sid]={'id':sid,'title':title,'artist':artist,'cats':cats,'sections':secs}
    log.append(f'OK {sid} {artist or ""} - {title} ({len(secs)} secs)')
    print(log[-1],flush=True)
# fill artist for id-based entries from search slug is unavailable; resolve via page title
for sid,s in out.items():
    if not s['artist']:
        h=get(f'https://www.tab4u.com/tabs/songs/{sid}_song.html');time.sleep(0.5)
        m=re.search(r'אקורדים לשיר (.*?) - (.*?)(?: \||</title>)',h)
        if m: s['artist']=html.unescape(m.group(2)).strip()
json.dump(list(out.values()),open('data.json','w',encoding='utf-8'),ensure_ascii=False)
open('log.txt','w',encoding='utf-8').write('\n'.join(log))
print('DONE',len(out))
