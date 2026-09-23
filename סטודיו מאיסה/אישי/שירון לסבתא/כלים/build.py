import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = '/Users/my/Downloads/הקלוד של מאיסה/סטודיו מאיסה/אישי/שירון לסבתא'

songs = json.load(open(os.path.join(HERE, 'data.json'), encoding='utf-8'))
template = open(os.path.join(HERE, 'template.html'), encoding='utf-8').read()
payload = json.dumps(songs, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')

os.makedirs(OUT_DIR, exist_ok=True)
out = os.path.join(OUT_DIR, 'השירון לסבתא.html')
open(out, 'w', encoding='utf-8').write(template.replace('__DATA__', payload))
print(out, len(songs), 'songs')
