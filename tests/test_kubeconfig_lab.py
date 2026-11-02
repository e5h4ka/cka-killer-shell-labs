import base64
from contextlib import nullcontext
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'lib'))
from core import Blocked, State, catalog
from kubeconfig_lab import execute


class LifecycleTests(unittest.TestCase):
    def test_start_fail_solve_pass_cleanup_repeat_and_conflicts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = State(root / 'state')
            course = root / 'course'
            task = catalog()[('killer-sh-1', '01')]
            def openssl(*args, **kwargs):
                Path(args[args.index('-out') + 1]).write_bytes(b'certificate-fixture\n')
                Path(args[args.index('-keyout') + 1]).write_bytes(b'private-fixture')
            with patch.object(state, 'lock', side_effect=lambda: nullcontext()), \
                 patch('kubeconfig_lab.identity', return_value={'uid': 'cluster'}), \
                 patch('core.identity', return_value={'uid': 'cluster'}), \
                 patch('kubeconfig_lab.run', side_effect=openssl):
                self.assertEqual(execute('start', task, state, course), 0)
                self.assertEqual(execute('validate', task, state, course), 1)
                config = json.loads((course / 'kubeconfig').read_text())
                (course / 'contexts').write_text('\n'.join(c['name'] for c in config['contexts']))
                (course / 'current-context').write_text(config['current-context'])
                user = next(u for u in config['users'] if u['name'] == 'account-0027@internal')
                (course / 'cert').write_bytes(base64.b64decode(user['user']['client-certificate-data']))
                self.assertEqual(execute('start', task, state, course), 0)
                self.assertEqual(execute('validate', task, state, course), 0)
                (course / 'extra').write_text('preserve')
                with self.assertRaises(Blocked):
                    execute('cleanup', task, state, course)
                self.assertTrue((course / 'kubeconfig').exists())
                (course / 'extra').unlink()
                self.assertEqual(execute('cleanup', task, state, course), 0)
                self.assertFalse(course.exists())
                self.assertEqual(execute('cleanup', task, state, course), 0)
                self.assertEqual(execute('start', task, state, course), 0)
