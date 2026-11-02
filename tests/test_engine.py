from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'lib'))
from core import Blocked, State
from engine import Session
from exercises import quantities, qty, script_check


class EngineTests(unittest.TestCase):
    def session(self, directory):
        s = Session({'suite': 'killer-sh-1', 'id': '03'}, State(directory))
        s.data = {'resources': [], 'attempt': 'attempt', 'phase': 'active'}
        return s

    def test_existing_resource_cannot_be_reserved(self):
        with tempfile.TemporaryDirectory() as directory:
            s = self.session(directory)
            with patch.object(s, 'get', return_value={'metadata': {'uid': 'foreign'}}):
                with self.assertRaises(Blocked):
                    s.reserve('namespace', 'foreign')
            self.assertEqual(s.data['resources'], [])

    def test_reservation_survives_create_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            s = self.session(directory)
            with patch.object(s, 'get', return_value={}), patch('engine.kubectl', side_effect=Blocked('API down')):
                with self.assertRaises(Blocked):
                    s.namespace('isolated')
            self.assertEqual(s.store.read()['resources'][0]['uid'], None)

    def test_create_records_uid(self):
        with tempfile.TemporaryDirectory() as directory:
            s = self.session(directory)
            with patch.object(s, 'get', side_effect=[{}, {'metadata': {'uid': 'created'}}]), patch('engine.kubectl'):
                s.namespace('isolated')
            self.assertEqual(s.store.read()['resources'][0]['uid'], 'created')

    def test_replaced_namespace_not_deleted(self):
        with tempfile.TemporaryDirectory() as directory:
            s = self.session(directory)
            s.data['resources'] = [{'key': ['namespace', 'isolated', None], 'uid': 'original'}]
            with patch('exercises.restore'), patch.object(s, 'get', return_value={'metadata': {'uid': 'replacement'}}), patch('engine.kubectl') as command:
                with self.assertRaises(Blocked):
                    s.cleanup()
                command.assert_not_called()

    def test_equivalent_quantities(self):
        self.assertEqual(qty('2Gi'), qty('2048Mi'))
        self.assertTrue(quantities({'resources': {'requests': {'cpu': '0.01', 'memory': '10485760'}}}, '10m', '10Mi'))

    def test_student_script_is_not_executed(self):
        s = Mock()
        s.text.return_value = 'kubectl top node; rm -rf /'
        with patch('exercises.run') as command:
            script_check(s, 'node.sh', ['top', 'node'])
            command.assert_not_called()
            self.assertFalse(s.check.call_args.args[1])

    def test_shell_chain_cannot_pass_script_check(self):
        s = Mock()
        s.text.return_value = 'kubectl top node && false'
        script_check(s, 'node.sh', ['top', 'node'])
        self.assertFalse(s.check.call_args.args[1])

    def test_sort_script_requires_all_namespaces(self):
        s = Mock()
        s.text.return_value = 'kubectl get pod --sort-by=.metadata.uid'
        script_check(s, 'find.sh', ['get', 'pod', '-A', '--sort-by=.metadata.uid'])
        self.assertFalse(s.check.call_args.args[1])
