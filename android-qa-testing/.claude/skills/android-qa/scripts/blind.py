import argparse, shlex, sys
from common import ROOT, adb, load_state, save_state, log_event, ui_elements

KEYS = {'back': 4, 'home': 3, 'enter': 66}

def guard():
    s = load_state()
    if s.get('finished'):
        sys.exit('Session already finished.')
    if s.get('step', 0) >= s.get('max_steps', 60):
        sys.exit('PATIENCE BUDGET USED UP. Call: blind.py finish --goal-met no --summary <why>')

def observe(a):
    guard()
    shots = ROOT / 'shots'; shots.mkdir(parents=True, exist_ok=True)
    step = load_state().get('step', 0) + 1
    path = shots / f'step_{step:03d}.png'
    path.write_bytes(adb('exec-out', 'screencap', '-p', binary=True))
    log_event('observe', screenshot=str(path))
    print('Screenshot:', path)
    for i, e in enumerate(ui_elements()):
        mark = 'tap' if e['clickable'] else 'text'
        print('[{}] {} {} {!r} at ({},{})'.format(i, mark, e['type'], e['label'] or '(no label)', e['x'], e['y']))

def tap(a):
    guard(); adb('shell', 'input', 'tap', str(a.x), str(a.y))
    log_event('tap', x=a.x, y=a.y, expect=a.expect); print('tapped')

def tap_text(a):
    guard()
    hits = [e for e in ui_elements() if a.text.lower() in e['label'].lower()]
    if not hits:
        log_event('tap_text_failed', text=a.text, expect=a.expect)
        sys.exit('No visible element contains that text.')
    adb('shell', 'input', 'tap', str(hits[0]['x']), str(hits[0]['y']))
    log_event('tap_text', text=a.text, expect=a.expect); print('tapped', hits[0]['label'])

def type_text(a):
    guard()
    adb('shell', 'input', 'text', shlex.quote(a.text.replace(' ', '%s')))
    log_event('type', text=a.text, expect=a.expect); print('typed')

def swipe(a):  # direction = where the finger moves
    guard()
    w, h = [int(v) for v in adb('shell', 'wm', 'size').strip().split()[-1].split('x')]
    cx, cy = w // 2, h // 2
    d = {'up': (cx, cy + h // 4, cx, cy - h // 4), 'down': (cx, cy - h // 4, cx, cy + h // 4),
         'left': (cx + w // 4, cy, cx - w // 4, cy), 'right': (cx - w // 4, cy, cx + w // 4, cy)}[a.direction]
    adb('shell', 'input', 'swipe', *[str(v) for v in d], '300')
    log_event('swipe', direction=a.direction, expect=a.expect); print('swiped')

def key(a):
    guard(); adb('shell', 'input', 'keyevent', str(KEYS[a.name]))
    log_event('key', name=a.name, expect=a.expect); print('pressed', a.name)

def rotate(a):
    guard()
    adb('shell', 'settings', 'put', 'system', 'accelerometer_rotation', '0')
    adb('shell', 'settings', 'put', 'system', 'user_rotation', '1' if a.mode == 'landscape' else '0')
    log_event('rotate', mode=a.mode, expect=a.expect); print('rotated')

def note(a):
    log_event('note', text=a.text); print('noted')

def finish(a):
    log_event('finish', goal_met=a.goal_met, summary=a.summary)
    s = load_state(); s['finished'] = True; save_state(s); print('finished')

def main():
    p = argparse.ArgumentParser(); sp = p.add_subparsers(dest='cmd', required=True)
    sp.add_parser('observe').set_defaults(fn=observe)
    def action(name, fn, *args):
        q = sp.add_parser(name)
        for arg, kw in args: q.add_argument(arg, **kw)
        q.add_argument('--expect', required=True, help='what you expect to happen next')
        q.set_defaults(fn=fn)
    action('tap', tap, ('x', {'type': int}), ('y', {'type': int}))
    action('tap-text', tap_text, ('text', {}))
    action('type', type_text, ('text', {}))
    action('swipe', swipe, ('direction', {'choices': ['up', 'down', 'left', 'right']}))
    action('key', key, ('name', {'choices': list(KEYS)}))
    action('rotate', rotate, ('mode', {'choices': ['portrait', 'landscape']}))
    q = sp.add_parser('note'); q.add_argument('text'); q.set_defaults(fn=note)
    q = sp.add_parser('finish')
    q.add_argument('--goal-met', choices=['yes', 'no', 'partly'], required=True)
    q.add_argument('--summary', required=True); q.set_defaults(fn=finish)
    a = p.parse_args(); a.fn(a)

main()
