"""Command interface. Unimplemented tasks are explicitly BLOCKED."""
import argparse
import json
import subprocess
import sys

from core import Blocked, State, catalog, identity, query, run


def main(argv=None):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['doctor', 'list', 'start', 'validate', 'hint', 'cleanup'])
    parser.add_argument('suite', nargs='?', choices=['killer-sh-1', 'killer-sh-2'])
    parser.add_argument('task', nargs='?')
    parser.add_argument('--level', type=int, choices=[1, 2, 3], default=1)
    args = parser.parse_args(argv)
    try:
        tasks = catalog()
        if args.action == 'list':
            for (suite, number), task in tasks.items():
                if not args.suite or suite == args.suite:
                    print(suite, number, task['status'], task['title'])
            return 0
        if args.action == 'doctor':
            print('Cluster:', json.dumps(identity(), indent=2))
            print('Nodes:', ', '.join(x['metadata']['name'] for x in query('nodes')['items']))
            print('Python:', sys.version.split()[0])
            print('Kubernetes:', run('kubectl', 'version', '-o', 'json'))
            return 0
        key = (args.suite, (args.task or '').zfill(2))
        if key not in tasks:
            parser.error('Specify a registered suite and task number; use lab list.')
        task = tasks[key]
        if args.action == 'hint':
            hints = (task['directory'] / 'hints.md').read_text(encoding='utf-8').split('<!-- level -->')
            print(hints[min(args.level, len(hints)) - 1].strip())
            return 0
        if task['status'] != 'implemented':
            raise Blocked(f'{key[0]}/{key[1]} implementation pending. See PLAN.md.')
        if key == ('killer-sh-1', '01'):
            from kubeconfig_lab import execute
            return execute(args.action, task)
        raise Blocked('Lifecycle backend not yet installed.')
    except (Blocked, subprocess.TimeoutExpired, OSError) as exc:
        print('BLOCKED:', exc, file=sys.stderr)
        return 2
    except (ValueError, KeyError) as exc:
        print('ERROR:', exc, file=sys.stderr)
        return 3


if __name__ == '__main__':
    sys.exit(main())
