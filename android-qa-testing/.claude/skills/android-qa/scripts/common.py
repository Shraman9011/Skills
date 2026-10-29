import json, os, subprocess, time
import xml.etree.ElementTree as ET
from pathlib import Path

# The orchestrator exports QA_HOME as an ABSOLUTE path so every process agrees.
ROOT = Path(os.environ.get('QA_HOME', '.qa-run')).resolve()
STATE = ROOT / 'state.json'

def load_state():
    return json.loads(STATE.read_text()) if STATE.exists() else {}

def save_state(s):
    ROOT.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, indent=2))

def adb(*args, binary=False, timeout=60):
    serial = load_state().get('serial')
    cmd = ['adb'] + (['-s', serial] if serial else []) + list(args)
    r = subprocess.run(cmd, capture_output=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode(errors='replace').strip())
    return r.stdout if binary else r.stdout.decode(errors='replace')

def log_event(kind, **data):
    s = load_state()
    s['step'] = s.get('step', 0) + 1
    save_state(s)
    rec = {'step': s['step'], 'time': time.strftime('%H:%M:%S'), 'kind': kind, **data}
    with open(ROOT / 'events.jsonl', 'a') as f:
        f.write(json.dumps(rec) + chr(10))
    return rec

def ui_elements():
    adb('shell', 'uiautomator', 'dump', '/sdcard/qa_ui.xml')
    root = ET.fromstring(adb('exec-out', 'cat', '/sdcard/qa_ui.xml').strip())
    items = []
    for n in root.iter('node'):
        label = n.get('text') or n.get('content-desc') or ''
        clickable = n.get('clickable') == 'true'
        if not label and not clickable:
            continue
        x1, y1, x2, y2 = [int(v) for v in n.get('bounds').replace('][', ',').strip('[]').split(',')]
        items.append({'label': label, 'type': n.get('class', '').split('.')[-1],
                      'clickable': clickable, 'x': (x1 + x2) // 2, 'y': (y1 + y2) // 2})
    return items
