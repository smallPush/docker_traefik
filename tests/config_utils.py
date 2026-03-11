import subprocess
import json
import unittest

_cached_config = None

def get_docker_compose_config():
    """
    Load and parse the Docker Compose configuration once and cache it.
    This significantly reduces total test execution time by avoiding redundant 'docker compose config' calls.
    """
    global _cached_config
    if _cached_config is not None:
        return _cached_config

    try:
        result = subprocess.run(
            ['docker', 'compose', 'config', '--format', 'json'],
            capture_output=True,
            text=True,
            check=True
        )
        _cached_config = json.loads(result.stdout)
        return _cached_config
    except subprocess.CalledProcessError as e:
        raise unittest.SkipTest(f"Failed to run 'docker compose config': {e.stderr}")
    except json.JSONDecodeError as e:
        raise unittest.SkipTest(f"Failed to parse JSON from 'docker compose config': {e}")
    except FileNotFoundError:
        raise unittest.SkipTest("The 'docker' command was not found. Please ensure Docker is installed.")
