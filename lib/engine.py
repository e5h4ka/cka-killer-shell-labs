"""Sequential lab lifecycle with namespace ownership and a durable mutation journal."""
import json
import os
from pathlib import Path
import time
import uuid

from core import Blocked, State, identity, kubectl, query, ready, run


def object_get(kind, name, ns=None):
    args = ['get', kind, name, '--ignore-not-found', '-o', 'json']
    if ns:
        args += ['-n', ns]
    value = kubectl(*args).strip()
    return json.loads(value) if value else {}


def apply(obj):
    return kubectl('apply', '-f', '-', stdin=json.dumps(obj))


class Session:
    def __init__(self, task, store=None):
        self.task = task
        self.store = store or State()
        self.data = None
        self.failures = []

    def save(self):
        self.store.write(self.data)

    def check(self, label, condition):
        print(('PASS: ' if condition else 'FAIL: ') + label)
        if not condition:
            self.failures.append(label)

    def get(self, kind, name, ns=None):
        return object_get(kind, name, ns)

    def items(self, kind, ns=None):
        return query(kind, ns)['items']

    def namespace(self, name):
        self.reserve('namespace', name)
        self.put({'apiVersion': 'v1', 'kind': 'Namespace', 'metadata': {'name': name}})

    def reserve(self, kind, name, ns=None):
        key = [kind, name, ns]
        if any(r['key'] == key for r in self.data['resources']):
            return
        if self.get(kind, name, ns):
            raise Blocked(f'Resource exists: {key}. Use a fresh playground.')
        self.data['resources'].append({'key': key, 'uid': None})
        self.save()

    def put(self, obj):
        meta = obj['metadata']
        # Namespaces are isolated; reserve individual cluster/default resources.
        ns = meta.get('namespace')
        if not ns or ns in ('default', 'kube-system'):
            self.reserve(obj['kind'].lower(), meta['name'], ns)
        meta.setdefault('labels', {})['cka-labs-attempt'] = self.data['attempt']
        kubectl('apply', '-f', '-', stdin=json.dumps(obj))
        current = self.get(obj['kind'], meta['name'], ns)
        for resource in self.data['resources']:
            if resource['key'] == [obj['kind'].lower(), meta['name'], ns]:
                resource['uid'] = current['metadata']['uid']
        self.save()

    def file(self, name, content):
        path = Path(self.data['course']) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')

    def text(self, name):
        path = Path(self.data['course']) / name
        if not path.is_file() or path.is_symlink():
            return ''
        return path.read_text(encoding='utf-8').strip()

    def jsonfile(self, name):
        try:
            return json.loads(self.text(name))
        except ValueError:
            return {}

    def pod(self, name, ns='default'):
        return self.get('pod', name, ns)

    def exec(self, pod, ns, *cmd, container=None):
        args = ['exec', '-n', ns, pod]
        if container:
            args += ['-c', container]
        return kubectl(*args, '--', *cmd)

    def snapshot_file(self, path):
        path = Path(path)
        if path.is_symlink():
            raise Blocked(f'Refusing symlink: {path}')
        self.data.setdefault('backups', {})[str(path)] = path.read_text() if path.exists() else None
        self.save()

    def cleanup(self):
        from exercises import restore
        restore(self)
        # First identify every object; never partially delete before detecting a UID conflict.
        for resource in self.data['resources']:
            kind, name, ns = resource['key']
            current = self.get(kind, name, ns)
            if not current:
                continue
            uid = resource['uid']
            if uid and current['metadata']['uid'] != uid:
                raise Blocked(f'Resource was replaced: {kind}/{name}')
            if not uid and current['metadata'].get('labels', {}).get('cka-labs-attempt') != self.data['attempt']:
                # Student-created target was absent at baseline and explicitly reserved.
                if not resource.get('student'):
                    raise Blocked(f'Unconfirmed ownership: {kind}/{name}')
        for resource in reversed(self.data['resources']):
            kind, name, ns = resource['key']
            args = ['delete', kind, name, '--ignore-not-found', '--wait=true', '--timeout=90s']
            if ns:
                args += ['-n', ns]
            kubectl(*args)
        course = Path(self.data['course'])
        if course.exists():
            marker = course / '.lab-owner'
            if course.is_symlink() or not marker.is_file() or marker.read_text() != self.data['attempt']:
                raise Blocked('Course directory ownership changed.')
            # Preserve answers for inspection; avoid recursive deletion of user files.
            archive = self.store.root / ('answers-' + self.data['attempt'])
            if archive.exists():
                raise Blocked(f'Archive already exists: {archive}')
            course.rename(archive)
            print('Answers archived:', archive)
        cidr_experiment = self.data['task'] == ['killer-sh-1', '20']
        self.data['phase'] = 'recreate-required' if cidr_experiment else 'cleaned'
        self.save()
        print('Recreate the playground before any further tasks.' if cidr_experiment else 'Cleaned.')

    def target(self, kind, name, ns=None):
        self.reserve(kind, name, ns)
        next(r for r in self.data['resources'] if r['key'] == [kind, name, ns])['student'] = True
        self.save()


def execute(action, task, stage=None):
    from exercises import prepare, validate, checkpoint, preflight, restore
    session = Session(task)
    with session.store.lock():
        data = session.store.read()
        if data and data.get('phase') == 'cleaned':
            data = None
        key = [task['suite'], task['id']]
        if data:
            if data['task'] != key:
                raise Blocked('Clean the active task first: ./lab clean')
            session.data = data
            if action == 'recover':
                restore(session, offline=True)
                return 0
            session.store.assert_identity(data['identity'])
        elif action != 'start':
            if action == 'cleanup':
                print('Already clean.')
                return 0
            raise Blocked('Start this task first.')
        if action == 'start' and not data:
            nodes = query('nodes')['items']
            controls = [n for n in nodes if 'node-role.kubernetes.io/control-plane' in n['metadata'].get('labels', {})]
            if len(controls) != 1 or not all(any(c['type'] == 'Ready' and c['status'] == 'True'
                    for c in n['status']['conditions']) for n in nodes):
                raise Blocked('Requires exactly one control-plane and all nodes Ready.')
            cp = controls[0]['metadata']['name']
            if run('hostname').strip() != cp:
                raise Blocked('Run on the control-plane host.')
            number = task['id'].lstrip('0')
            directory = 'p1' if key == ['killer-sh-1', '18'] else 'p2' if key == ['killer-sh-1', '19'] else number
            course = Path('/opt/course') / directory
            if course.exists() or course.is_symlink():
                raise Blocked(f'{course} already exists; move it aside first.')
            session.data = dict(task=key, identity=identity(), attempt=uuid.uuid4().hex,
                phase='preparing', course=str(course), resources=[], backups={}, checkpoints={},
                machine_id=Path('/etc/machine-id').read_text(),
                cp=cp, workers=[n['metadata']['name'] for n in nodes if n not in controls],
                nodes={n['metadata']['name']: {'labels': n['metadata'].get('labels', {}),
                    'taints': n['spec'].get('taints', [])} for n in nodes})
            preflight(session)
            session.save()
            if key == ['killer-sh-1', '12']:
                print('Required replicas:', len(session.data['workers']) + 1)
            course.mkdir(parents=True)
            (course / '.lab-owner').write_text(session.data['attempt'])
            prepare(session)
            session.data['phase'] = 'active'
            session.save()
        if action == 'start':
            if session.data['phase'] != 'active':
                raise Blocked('Interrupted setup: ./lab clean')
            print((task['directory'] / 'task.md').read_text(encoding='utf-8'))
            print('Control-plane:', session.data['cp'], '| Workers:', ', '.join(session.data['workers']))
            print('Check: ./lab check | Hint: ./lab hint | Cleanup: ./lab clean')
        elif action == 'cleanup':
            session.cleanup()
        elif action == 'checkpoint':
            checkpoint(session, stage)
            session.save()
        elif action == 'validate':
            if session.data['phase'] != 'active':
                raise Blocked('Setup did not finish.')
            validate(session)
            return int(bool(session.failures))
    return 0
