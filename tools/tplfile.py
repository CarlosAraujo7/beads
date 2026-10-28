"""Ler e gravar o templates.js do projeto (o mesmo formato que o app grava pelo botão "Gravar no catálogo").

    from tplfile import parse, write
    d = parse(path)          # {'legend': {...}, 'cfg': {...}|None, 'baked': str|None, 'items': [{'id','cat','group','name','rows'}]}
    write(path, d['legend'], d['cfg'], d['items'])   # faz cópia de segurança em tools/backups/ antes de gravar
"""
import os, re, json, unicodedata, datetime, shutil

_STR = r'"(?:[^"\\]|\\.)*"'
ITEM_RE = re.compile(r'\{id:(%s),cat:(%s),group:(%s),name:(%s),rows:\[(.*?)\n\]\}' % (_STR, _STR, _STR, _STR), re.S)
HEADER = [
    '// Templates de beads - cada letra e um codigo de cor Pindou (veja TPL_LEGEND).',
    '// Formato: {id:"x", cat:"categoria", group:"Serie", name:"Nome", rows:["....kk....", ...]}  ("." = vazio)',
    '// Este arquivo e gravado pelo proprio app (Templates > Gravar no catalogo) e acrescentado por tools/add_templates.py.',
]


def slug(s):
    s = unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-') or 'item'


def parse(path):
    text = open(path, encoding='utf-8').read()
    legend = json.loads(re.search(r'window\.TPL_LEGEND\s*=\s*(\{.*?\});', text, re.S).group(1))
    m = re.search(r'window\.TPL_CATS_CFG\s*=\s*(\{.*?\});\s*\n', text, re.S)
    cfg = json.loads(m.group(1)) if m else None
    m = re.search(r'window\.TPL_BAKED\s*=\s*("[^"]*");', text)
    baked = json.loads(m.group(1)) if m else None
    m = re.search(r'window\.TPL_REMOVED\s*=\s*(\[.*?\]);', text, re.S)
    removed = json.loads(m.group(1)) if m else []
    items = []
    for m in ITEM_RE.finditer(text):
        rows = json.loads('[' + m.group(5) + ']')
        items.append({'id': json.loads(m.group(1)), 'cat': json.loads(m.group(2)), 'group': json.loads(m.group(3)),
                      'name': json.loads(m.group(4)), 'rows': rows})
    return {'legend': legend, 'cfg': cfg, 'baked': baked, 'removed': removed, 'items': items}


def render(legend, cfg, items, removed=None):
    out = list(HEADER)
    out.append('window.TPL_LEGEND = ' + json.dumps(legend, ensure_ascii=False) + ';')
    if cfg is not None:
        out.append('window.TPL_CATS_CFG = ' + json.dumps(cfg, ensure_ascii=False) + ';')
    out.append('window.TPL_BAKED = ' + json.dumps(datetime.datetime.now().isoformat(timespec='seconds')) + ';')
    if removed: out.append('window.TPL_REMOVED = ' + json.dumps(removed, ensure_ascii=False) + ';')
    out.append('window.TEMPLATES = [')
    for t in items:
        out.append('{id:%s,cat:%s,group:%s,name:%s,rows:[' % tuple(json.dumps(t[k], ensure_ascii=False) for k in ('id', 'cat', 'group', 'name')))
        out.append(',\n'.join(json.dumps(r) for r in t['rows']))
        out.append(']},')
    out.append('];')
    return '\n'.join(out) + '\n'


def backup(path, keep=30):
    """copia o arquivo atual para tools/backups/templates-AAAAMMDD-HHMMSS.js (guarda as últimas `keep`)"""
    if not os.path.exists(path): return None
    bdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups'); os.makedirs(bdir, exist_ok=True)
    dst = os.path.join(bdir, 'templates-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '.js')
    shutil.copy(path, dst)
    olds = sorted(f for f in os.listdir(bdir) if f.startswith('templates-') and f.endswith('.js'))
    for f in olds[:-keep]: os.remove(os.path.join(bdir, f))
    return dst


def write(path, legend, cfg, items, removed=None, do_backup=True):
    if do_backup: backup(path)
    open(path, 'w', encoding='utf-8').write(render(legend, cfg, items, removed))
