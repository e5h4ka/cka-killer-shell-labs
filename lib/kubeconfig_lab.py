"""File-only exercise; never changes the administrator's kubeconfig."""
import base64
import json
from pathlib import Path
import uuid

from core import Blocked, State, identity, run

COURSE = Path('/opt/course/1')


def execute(action, task, state=None, course=None):
    state = state or State()
    course = Path(course or COURSE)
    key = [task['suite'], task['id']]
    with state.lock():
        data = state.read()
        if data and data.get('phase') == 'cleaned':
            data = None
        if data:
            if data['task'] != key:
                raise Blocked('Another task is active. Clean it first.')
            state.assert_identity(data['identity'])
            if data['course'] != str(course):
                raise Blocked('Course directory changed.')
        elif action != 'start':
            if action == 'cleanup':
                print('Already clean.')
                return 0
            raise Blocked('Run start first.')
        if action == 'start':
            if data:
                if data['phase'] != 'active':
                    raise Blocked('Interrupted setup; run cleanup first.')
            else:
                if course.exists() or course.is_symlink():
                    raise Blocked(f'{course} exists; refusing to overwrite it.')
                data = dict(task=key, identity=identity(), course=str(course),
                            phase='preparing', marker=uuid.uuid4().hex)
                state.write(data)
                course.mkdir(parents=True)
                (course / '.lab-owner').write_text(data['marker'])
                private = state.root / 'exercise.key'
                cert = state.root / 'exercise.crt'
                run('openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes',
                    '-keyout', str(private), '-out', str(cert), '-days', '30',
                    '-subj', '/CN=account-0027@internal', timeout=60)
                encoded = base64.b64encode(cert.read_bytes()).decode()
                config = dict(apiVersion='v1', kind='Config',
                    clusters=[dict(name='training', cluster={'server': 'https://127.0.0.1:6443'})],
                    contexts=[dict(name=name, context={'cluster': 'training', 'user': user})
                        for name, user in [('cluster-admin', 'admin@internal'),
                            ('cluster-w100', 'account-0027@internal'),
                            ('cluster-w200', 'account-0028@internal')]],
                    users=[{'name': user, 'user': {'client-certificate-data': encoded}}
                        for user in ['admin@internal', 'account-0027@internal', 'account-0028@internal']])
                config['current-context'] = 'cluster-w200'
                (course / 'kubeconfig').write_text(json.dumps(config, indent=2))
                private.unlink()
                data['certificate'] = encoded
                data['phase'] = 'active'
                state.write(data)
            print((task['directory'] / 'task.md').read_text(encoding='utf-8'))
            return 0
        marker = course / '.lab-owner'
        if course.is_symlink() or not marker.is_file() or marker.is_symlink() or marker.read_text() != data['marker']:
            raise Blocked('Course ownership marker missing or changed; refusing operation.')
        if action == 'validate':
            if data['phase'] != 'active':
                raise Blocked('Setup did not finish.')
            checks = []
            def check(name, expected, transform=lambda x: x):
                path = course / name
                ok = path.is_file() and not path.is_symlink()
                try:
                    ok = ok and transform(path.read_bytes()) == expected
                except (ValueError, UnicodeError):
                    ok = False
                checks.append(ok)
                print(('PASS: ' if ok else 'FAIL: ') + name)
            check('contexts', {'cluster-admin', 'cluster-w100', 'cluster-w200'},
                  lambda b: set(b.decode().splitlines()))
            check('current-context', 'cluster-w200', lambda b: b.decode().strip())
            check('cert', base64.b64decode(data['certificate']))
            return 0 if all(checks) else 1
        # Do not recursively remove the directory: unknown user files are preserved.
        known = ['kubeconfig', 'contexts', 'current-context', 'cert']
        unknown = set(p.name for p in course.iterdir()) - set(known) - {'.lab-owner'}
        if unknown:
            raise Blocked('Move extra files before cleanup: ' + ', '.join(sorted(unknown)))
        for name in known:
            path = course / name
            if path.is_dir() and not path.is_symlink():
                raise Blocked(f'Unexpected directory: {path}')
        for name in known:
            path = course / name
            if path.exists() or path.is_symlink():
                path.unlink()
        marker.unlink()
        course.rmdir()
        for name in ['exercise.key', 'exercise.crt']:
            path = state.root / name
            if path.exists():
                path.unlink()
        data['phase'] = 'cleaned'
        state.write(data)
        print('Cleaned killer-sh-1/01.')
        return 0
