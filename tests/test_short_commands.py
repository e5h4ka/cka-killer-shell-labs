from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'lib'))
from cli import short_args
from core import Blocked


class ShortCommandTests(unittest.TestCase):
    def test_number_and_suite(self):
        self.assertEqual(short_args(['1']), ['start', 'killer-sh-1', '1'])
        self.assertEqual(short_args(['2/12']), ['start', 'killer-sh-2', '12'])
        self.assertEqual(short_args([]), ['list'])

    def test_active_task_and_hint_level(self):
        with patch('cli.State.read', return_value={'task': ['killer-sh-1', '01'], 'phase': 'active'}):
            self.assertEqual(short_args(['check']), ['validate', 'killer-sh-1', '01'])
            self.assertEqual(short_args(['hint', '--level', '3']),
                             ['hint', 'killer-sh-1', '01', '--level', '3'])
            self.assertEqual(short_args(['clean']), ['cleanup', 'killer-sh-1', '01'])

    def test_no_active_task_is_not_guessed(self):
        for data in (None, {'phase': 'cleaned'}):
            with patch('cli.State.read', return_value=data):
                with self.assertRaises(Blocked):
                    short_args(['check'])

    def test_explicit_command_is_preserved(self):
        args = ['validate', 'killer-sh-2', '12']
        self.assertEqual(short_args(args), args)
