import unittest
import json
import subprocess
import os

class TestDockerComposeSecurity(unittest.TestCase):
    def test_traefik_docker_socket_read_only(self):
        """
        Verify that the traefik service mounts the Docker socket as read-only.
        Uses 'docker compose config --format json' to robustly parse the configuration.
        """
        try:
            # We use 'docker compose config' to get the resolved and normalized configuration in JSON format.
            # This is more robust than manual string parsing or regex.
            result = subprocess.run(
                ['docker', 'compose', 'config', '--format', 'json'],
                capture_output=True,
                text=True,
                check=True
            )
            config = json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            self.fail(f"Failed to run 'docker compose config': {e.stderr}")
        except json.JSONDecodeError as e:
            self.fail(f"Failed to parse JSON from 'docker compose config': {e}")
        except FileNotFoundError:
            self.fail("The 'docker' command was not found. Please ensure Docker is installed.")

        services = config.get('services', {})
        traefik = services.get('traefik')
        self.assertIsNotNone(traefik, "traefik service not found in docker-compose.yml")

        volumes = traefik.get('volumes', [])
        found_socket_ro = False
        for vol in volumes:
            # The normalized JSON format uses 'source', 'target', and 'read_only' fields for bind mounts.
            if (vol.get('source') == '/var/run/docker.sock' and
                vol.get('target') == '/var/run/docker.sock' and
                vol.get('read_only') is True):
                found_socket_ro = True
                break

        self.assertTrue(found_socket_ro, "Traefik service must mount /var/run/docker.sock as read-only")

    def test_traefik_dashboard_ports_exposed(self):
        """
        Verify that port 8080 and 22 are exposed for Traefik (backward compatibility).
        """
        try:
            result = subprocess.run(
                ['docker', 'compose', 'config', '--format', 'json'],
                capture_output=True,
                text=True,
                check=True
            )
            config = json.loads(result.stdout)
        except Exception as e:
            self.fail(f"Failed to load docker-compose config: {e}")

        services = config.get('services', {})
        traefik = services.get('traefik', {})
        ports = traefik.get('ports', [])

        exposed_ports = [str(p.get('published')) for p in ports]
        self.assertIn("8080", exposed_ports, "Port 8080 should be exposed for backward compatibility")
        self.assertIn("22", exposed_ports, "Port 22 should be exposed for backward compatibility")

if __name__ == '__main__':
    unittest.main()
