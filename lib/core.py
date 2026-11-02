"""Process, catalog and durable state primitives. Standard library only."""
import contextlib
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


class Blocked(RuntimeError):
    pass


def run(*args, timeout=45, stdin=None):
    result = subprocess.run(args, input=stdin, text=True, capture_output=True,
                            timeout=timeout, check=False)
    if result.returncode:
        raise Blocked(f'{args[0]} exited {result.returncode}: {result.stderr.strip()}')
    return result.stdout


def kubectl(*args):
    return run('kubectl', '--request-timeout=20s', *args)


def query(kind, namespace=None):
    args = ['get', kind, '-o', 'json']
    args += ['-n', namespace] if namespace else []
    return json.loads(kubectl(*args))


def identity():
    config = json.loads(kubectl('config', 'view', '--minify', '--raw', '-o', 'json'))
    cluster = config['clusters'][0]['cluster']
    return {
        'context': config['current-context'],
        'server': cluster['server'],
        'ca': hashlib.sha256(cluster.get('certificate-authority-data', '').encode()).hexdigest(),
        'uid': query('namespace/kube-system')['metadata']['uid'],
    }


def catalog():
    result = {}
    for path in sorted((ROOT / 'labs').glob('*/*/task.json')):
        task = json.loads(path.read_text(encoding='utf-8'))
        key = (task['suite'], task['id'])
        if key in result:
            raise ValueError(f'Duplicate task: {key}')
        task['directory'] = path.parent
        result[key] = task
    return result


def ready(pod):
    return pod.get('status', {}).get('phase') == 'Running' and any(
        c.get('type') == 'Ready' and c.get('status') == 'True'
        for c in pod.get('status', {}).get('conditions', []))


def owned(pod, uid):
    return bool(uid) and any(x.get('uid') == uid for x in
                            pod.get('metadata', {}).get('ownerReferences', []))


class State:
    def __init__(self, root=None):
        self.root = Path(root or '/var/lib/cka-killer-shell-labs')

    @contextlib.contextmanager
    def lock(self):
        import fcntl
        self.root.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(self.root, 0o700)
        with (self.root / 'lock').open('a') as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise Blocked('Another lab operation is running.') from exc
            try:
                yield
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    def read(self):
        path = self.root / 'active.json'
        return json.loads(path.read_text()) if path.exists() else None

    def write(self, data):
        self.root.mkdir(mode=0o700, parents=True, exist_ok=True)
        fd, name = tempfile.mkstemp(dir=self.root, prefix='.state-')
        try:
            with os.fdopen(fd, 'w') as stream:
                json.dump(data, stream, indent=2)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, self.root / 'active.json')
            if os.name == 'posix':
                directory = os.open(self.root, os.O_RDONLY)
                try:
                    os.fsync(directory)
                finally:
                    os.close(directory)
        finally:
            if os.path.exists(name):
                os.unlink(name)

    def assert_identity(self, expected):
        if identity() != expected:
            raise Blocked('Cluster identity changed; select the original cluster.')
