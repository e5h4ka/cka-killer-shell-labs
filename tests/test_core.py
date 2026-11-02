import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'lib'))
from core import Blocked, State, catalog, owned, ready


class CoreTests(unittest.TestCase):
    def test_complete_catalog_without_duplicate_ids(self):
        tasks = catalog()
        self.assertEqual(set(tasks), {
            (suite, f'{number:02}')
            for suite, count in [('killer-sh-1', 20), ('killer-sh-2', 17)]
            for number in range(1, count + 1)})

    def test_running_without_ready_is_not_success(self):
        self.assertFalse(ready({'status': {'phase': 'Running'}}))
        self.assertFalse(ready({'status': {'phase': 'Pending', 'conditions': [
            {'type': 'Ready', 'status': 'True'}]}}))

    def test_unrelated_pod_is_not_owned(self):
        pod = {'metadata': {'ownerReferences': [{'uid': 'other'}]}}
        self.assertFalse(owned(pod, 'target'))
        self.assertFalse(owned(pod, None))
        self.assertTrue(owned(pod, 'other'))

    def test_failed_atomic_replace_preserves_previous_state(self):
        with tempfile.TemporaryDirectory() as directory:
            state = State(directory)
            state.write({'phase': 'active'})
            with patch('core.os.replace', side_effect=OSError('disk error')):
                with self.assertRaises(OSError):
                    state.write({'phase': 'cleaned'})
            self.assertEqual(state.read(), {'phase': 'active'})
            self.assertEqual(len(list(Path(directory).iterdir())), 1)

    def test_changed_cluster_is_rejected(self):
        with patch('core.identity', return_value={'uid': 'new'}):
            with self.assertRaises(Blocked):
                State().assert_identity({'uid': 'old'})


if __name__ == '__main__':
    unittest.main()
