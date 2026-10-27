"""Move os moldes da remessa 13 (e as versões de 1 placa deles) para o FIM do templates.js: a tela inicial mostra como "Novidades" os últimos 12."""
import os, sys, json
SP = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, SP)
import tplfile
p = os.path.join(os.path.dirname(SP), 'templates.js')
d = tplfile.parse(p)
names = {n for n, g, r in json.load(open(os.path.join(SP, 'data', 'final15_120.json'), encoding='utf-8'))}
isnew = lambda t: t['name'] in names or (t['name'].endswith(' (1 placa)') and t['name'][:-len(' (1 placa)')] in names)
items = [t for t in d['items'] if not isnew(t)] + [t for t in d['items'] if isnew(t)]
assert len(items) == len(d['items'])
tplfile.write(p, d['legend'], d['cfg'], items, d.get('removed'))
print('remessa 13 movida para o fim:', sum(isnew(t) for t in d['items']), 'moldes')
