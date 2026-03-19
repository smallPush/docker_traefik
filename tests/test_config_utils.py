import unittest
from unittest.mock import patch
import subprocess

# Standard import mechanism
try:
    from .config_utils import get_docker_compose_config
    from . import config_utils
except ImportError:
    import config_utils
    from config_utils import get_docker_compose_config

class TestConfigUtils(unittest.TestCase):
    def setUp(self):
        # Reset the cached config before each test to ensure fresh execution
        config_utils._cached_config = None

    @patch('subprocess.run')
    def test_get_docker_compose_config_file_not_found(self, mock_run):
        # Configure the mock to raise FileNotFoundError
        mock_run.side_effect = FileNotFoundError("The 'docker' command was not found.")

        # Verify that unittest.SkipTest is raised with the appropriate message
        with self.assertRaises(unittest.SkipTest) as context:
            get_docker_compose_config()

        self.assertIn("The 'docker' command was not found. Please ensure Docker is installed.", str(context.exception))

if __name__ == '__main__':
    unittest.main()
