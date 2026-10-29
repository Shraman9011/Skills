import argparse, json, os, subprocess, sys, time
from pathlib import Path
from common import ROOT, adb, load_state, save_state

def sh(*cmd):
    r = subprocess.run(list(cmd), capture_output=True, text=True)
    print(r.stdout + r.stderr)

def require_scope(package):
    f = Path(os.environ.get('QA_SCOPE', '.qa-scope.json'))
    if not f.exists():
        sys.exit('Missing scope file: ' + str(f))
    scope = json.loads(f.read_text())
    if not scope.get('owner_confirmed') or scope.get('package') != package:
        sys.exit('Ownership not confirmed or package mismatch in scope file.')
    return scope

def devices(a): sh('adb', 'devices', '-l')
def pair(a): sh('adb', 'pair', a.hostport, a.code)      # physical device, wireless debugging
def connect(a): sh('adb', 'connect', a.hostport)

def select(a):
    s = load_state(); s['serial'] = a.serial; save_state(s); print('selected', a.serial)

def install(a): print(adb('install', '-r', a.apk))

def start(a):
    adb('shell', 'monkey', '-p', a.package, '-c', 'android.intent.category.LAUNCHER', '1')
    print('launched')

def fresh(a):
    # Simulates a brand-new user: stop the app and wipe its data (this usually resets its permissions too).
    adb('shell', 'am', 'force-stop', a.package)
    print(adb('shell', 'pm', 'clear', a.package))

def newrun(a):
    s = load_state()
    s.update(step=0, finished=False, max_steps=a.steps, persona=a.persona)
    save_state(s)
    ev = ROOT / 'events.jsonl'
    if ev.exists():
        ev.rename(ROOT / ('events_' + str(int(time.time())) + '.jsonl'))
    print('new run:', a.persona, 'budget', a.steps)

def crashes(a): print(adb('logcat', '-d', '-b', 'crash'))

def stress(a):
    require_scope(a.package)
    try:
        out = adb('shell', 'monkey', '-p', a.package, '-s', str(a.seed),
                  '--throttle', '50', '-v', str(a.events), timeout=1200)
    except RuntimeError as e:
        out = 'monkey ended with error: ' + str(e)
    ROOT.mkdir(parents=True, exist_ok=True)
    (ROOT / ('monkey_seed_' + str(a.seed) + '.txt')).write_text(out)
    print(out[-1500:])
    print(adb('logcat', '-d', '-b', 'crash')[-3000:])

def scope_check(a): print(require_scope(a.package))

def main():
    p = argparse.ArgumentParser(); sp = p.add_subparsers(dest='cmd', required=True)
    def add(name, fn, *args, **opts):
        q = sp.add_parser(name)
        for arg, kw in args: q.add_argument(arg, **kw)
        q.set_defaults(fn=fn); return q
    add('devices', devices)
    add('pair', pair, ('hostport', {}), ('code', {}))
    add('connect', connect, ('hostport', {}))
    add('select', select, ('serial', {}))
    add('install', install, ('apk', {}))
    add('start', start, ('package', {}))
    add('fresh', fresh, ('package', {}))
    add('newrun', newrun, ('--persona', {'required': True}), ('--steps', {'type': int, 'default': 60}))
    add('crashes', crashes)
    add('stress', stress, ('package', {}), ('--events', {'type': int, 'default': 5000}), ('--seed', {'type': int, 'default': 1}))
    add('scope-check', scope_check, ('package', {}))
    a = p.parse_args(); a.fn(a)

main()
