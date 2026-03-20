import unittest
from unittest.mock import patch, MagicMock
import json
import subprocess

try:
    from . import config_utils
    from .config_utils import get_docker_compose_config
except ImportError:
    import config_utils
    from config_utils import get_docker_compose_config

class TestConfigUtils(unittest.TestCase):
    def setUp(self):
        # Reset the global cached config before each test
        config_utils._cached_config = None

    def tearDown(self):
        # Reset the global cached config after each test to prevent cache pollution
        config_utils._cached_config = None

    @patch('subprocess.run')
    def test_get_docker_compose_config_success(self, mock_run):
        """Test successful loading and parsing of docker compose config."""
        mock_result = MagicMock()
        mock_result.stdout = '{"services": {"web": {"image": "nginx"}}}'
        mock_run.return_value = mock_result

        config = get_docker_compose_config()

        self.assertEqual(config, {"services": {"web": {"image": "nginx"}}})
        mock_run.assert_called_once_with(
            ['docker', 'compose', 'config', '--format', 'json'],
            capture_output=True,
            text=True,
            check=True
        )

    @patch('subprocess.run')
    def test_get_docker_compose_config_cached(self, mock_run):
        """Test that subsequent calls return the cached config."""
        mock_result = MagicMock()
        mock_result.stdout = '{"services": {"web": {"image": "nginx"}}}'
        mock_run.return_value = mock_result

        # First call should execute subprocess.run
        config1 = get_docker_compose_config()
        self.assertEqual(config1, {"services": {"web": {"image": "nginx"}}})
        mock_run.assert_called_once()

        # Second call should return cached result without calling subprocess.run again
        mock_run.reset_mock()
        config2 = get_docker_compose_config()
        self.assertEqual(config2, {"services": {"web": {"image": "nginx"}}})
        mock_run.assert_not_called()

    @patch('subprocess.run')
    def test_get_docker_compose_config_called_process_error(self, mock_run):
        """Test that CalledProcessError raises SkipTest."""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=['docker', 'compose', 'config', '--format', 'json'],
            stderr="Failed to run docker compose"
        )

        with self.assertRaises(unittest.SkipTest) as context:
            get_docker_compose_config()

        self.assertIn("Failed to run 'docker compose config'", str(context.exception))

    @patch('subprocess.run')
    def test_get_docker_compose_config_json_decode_error(self, mock_run):
        """Test that JSONDecodeError raises SkipTest."""
        mock_result = MagicMock()
        mock_result.stdout = "Invalid JSON"
        mock_run.return_value = mock_result

        with self.assertRaises(unittest.SkipTest) as context:
            get_docker_compose_config()

        self.assertIn("Failed to parse JSON from 'docker compose config'", str(context.exception))

    @patch('subprocess.run')
    def test_get_docker_compose_config_file_not_found_error(self, mock_run):
        """Test that FileNotFoundError raises SkipTest."""
        mock_run.side_effect = FileNotFoundError("No such file or directory: 'docker'")

        with self.assertRaises(unittest.SkipTest) as context:
            get_docker_compose_config()

        self.assertIn("The 'docker' command was not found", str(context.exception))

if __name__ == '__main__':
    unittest.main()
