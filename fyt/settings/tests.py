import os
import tempfile
import unittest

from .loader import EnvLoader


class EnvLoaderTestCase(unittest.TestCase):
    def setUp(self):
        os.environ['ENV_LOADER_VALUE'] = '123'

    def test_load_from_environment(self):
        env = EnvLoader()
        self.assertEqual(env.get('ENV_LOADER_VALUE'), '123')
        self.assertEqual(env.get('MISSING_VALUE', 'fallback'), 'fallback')

    def test_load_from_config_file(self):
        f = tempfile.NamedTemporaryFile('w+')
        f.write('ENV_LOADER_VALUE: "456"\nANOTHER_VALUE: "789"')
        f.seek(0)

        env = EnvLoader(f.name)
        self.assertEqual(env.get('ANOTHER_VALUE'), '789')
        # Environment variables take precedence
        self.assertEqual(env.get('ENV_LOADER_VALUE'), '123')

    def tearDown(self):
        del os.environ['ENV_LOADER_VALUE']
