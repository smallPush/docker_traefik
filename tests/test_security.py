import unittest
try:
    from .config_utils import get_docker_compose_config
except ImportError:
    from config_utils import get_docker_compose_config

class TestDockerComposeSecurity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Load and parse the Docker Compose configuration once for all tests in this class.
        This significantly reduces total test execution time by avoiding redundant 'docker compose config' calls.
        """
        cls.config = get_docker_compose_config()

    def test_traefik_docker_socket_read_only(self):
        """
        Verify that the traefik service mounts the Docker socket as read-only.
        Uses the cached configuration for improved performance.
        """
        services = self.config.get('services', {})
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
        Verify that port 22 is exposed for Traefik (backward compatibility),
        but port 8080 is NOT exposed (security).
        Uses the cached configuration for improved performance.
        """
        services = self.config.get('services', {})
        traefik = services.get('traefik', {})
        ports = traefik.get('ports', [])

        exposed_ports = [str(p.get('published')) for p in ports]
        self.assertNotIn("8080", exposed_ports, "Port 8080 should NOT be exposed for security")
        self.assertIn("22", exposed_ports, "Port 22 should be exposed for backward compatibility")

if __name__ == '__main__':
    unittest.main()
