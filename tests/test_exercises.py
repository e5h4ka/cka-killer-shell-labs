from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'lib'))
from core import Blocked
from exercises import prepare, validate_daemonset, validate_placement, checkpoint, preflight


class ExerciseTests(unittest.TestCase):
    def test_statefulset_initial_fixture_has_two_replicas(self):
        s = Mock()
        s.task = {'suite': 'killer-sh-1', 'id': '03'}
        prepare(s)
        s.namespace.assert_called_once_with('project-h800')
        stateful = s.put.call_args.args[0]
        self.assertEqual(stateful['kind'], 'StatefulSet')
        self.assertEqual(stateful['spec']['replicas'], 2)
        self.assertEqual(stateful['spec']['serviceName'], 'o3db')

    def test_unrelated_pods_do_not_pass_daemonset(self):
        s = Mock()
        s.data = {'nodes': {'cp': {'labels': {}, 'taints': []}}}
        s.get.return_value = {'metadata': {'uid': 'ds'}}
        p = {'metadata': {'name': 'foreign'}, 'spec': {'nodeName': 'cp'},
             'status': {'phase': 'Running', 'conditions': [{'type': 'Ready', 'status': 'True'}]}}
        s.items.side_effect = lambda kind, *args: [p] if kind == 'pods' else [
            {'metadata': {'name': 'cp'}, 'spec': {}}]
        validate_daemonset(s)
        results = {call.args[0]: call.args[1] for call in s.check.call_args_list}
        self.assertFalse(results['One Ready owned Pod on each node'])

    def test_pending_checkpoint_rejects_running_scheduler(self):
        s = Mock()
        s.task = {'suite': 'killer-sh-2', 'id': '09'}
        with patch('exercises.run', return_value='{"containers":[{"metadata":{"name":"kube-scheduler"}}]}'):
            with self.assertRaises(Blocked):
                checkpoint(s, 'pending')

    def test_missing_metrics_blocks_before_setup(self):
        s = Mock()
        s.task = {'suite': 'killer-sh-1', 'id': '05'}
        with patch('exercises.kubectl', side_effect=Blocked('metrics unavailable')):
            with self.assertRaises(Blocked):
                preflight(s)
        s.put.assert_not_called()

    def test_readiness_checkpoint_rejects_already_ready(self):
        s = Mock()
        s.task = {'suite': 'killer-sh-2', 'id': '04'}
        s.pod.return_value = {'status': {'phase': 'Running', 'conditions': [{'type': 'Ready', 'status': 'True'}]}}
        with self.assertRaises(Blocked):
            checkpoint(s, 'not-ready')
