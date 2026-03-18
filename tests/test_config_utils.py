import unittest
from unittest.mock import patch, MagicMock
import subprocess
import json
import tests.config_utils as config_utils

class TestConfigUtils(unittest.TestCase):
    def setUp(self):
        # Reset the global cache before each test
        config_utils._cached_config = None

    @patch('subprocess.run')
    def test_get_docker_compose_config_success(self, mock_run):
        """Test successful retrieval of docker compose config."""
        mock_stdout = '{"services": {"test": {"image": "test-image"}}}'
        mock_run.return_value = MagicMock(stdout=mock_stdout)

        config = config_utils.get_docker_compose_config()

        self.assertEqual(config['services']['test']['image'], 'test-image')
        mock_run.assert_called_once_with(
            ['docker', 'compose', 'config', '--format', 'json'],
            capture_output=True,
            text=True,
            check=True
        )

    @patch('subprocess.run')
    def test_get_docker_compose_config_called_process_error(self, mock_run):
        """Test handling of subprocess.CalledProcessError."""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=['docker', 'compose', 'config'],
            stderr='Mock error message'
        )

        with self.assertRaises(unittest.SkipTest) as cm:
            config_utils.get_docker_compose_config()

        self.assertIn("Failed to run 'docker compose config': Mock error message", str(cm.exception))

    @patch('subprocess.run')
    def test_get_docker_compose_config_json_decode_error(self, mock_run):
        """Test handling of json.JSONDecodeError."""
        mock_run.return_value = MagicMock(stdout='invalid json')

        with self.assertRaises(unittest.SkipTest) as cm:
            config_utils.get_docker_compose_config()

        self.assertIn("Failed to parse JSON from 'docker compose config'", str(cm.exception))

    @patch('subprocess.run')
    def test_get_docker_compose_config_file_not_found_error(self, mock_run):
        """Test handling of FileNotFoundError (docker not found)."""
        mock_run.side_effect = FileNotFoundError()

        with self.assertRaises(unittest.SkipTest) as cm:
            config_utils.get_docker_compose_config()

        self.assertIn("The 'docker' command was not found", str(cm.exception))

    @patch('subprocess.run')
    def test_get_docker_compose_config_caching(self, mock_run):
        """Test that the configuration is cached after the first call."""
        mock_stdout = '{"services": {}}'
        mock_run.return_value = MagicMock(stdout=mock_stdout)

        # First call should trigger subprocess.run
        config1 = config_utils.get_docker_compose_config()
        # Second call should return cached value
        config2 = config_utils.get_docker_compose_config()

        self.assertIs(config1, config2)
        mock_run.assert_called_once()

if __name__ == '__main__':
    unittest.main()
