import unittest
import json
import subprocess
import os

class TestDockerComposePerformance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            result = subprocess.run(
                ['docker', 'compose', 'config', '--format', 'json'],
                capture_output=True,
                text=True,
                check=True
            )
            cls.config = json.loads(result.stdout)
        except Exception as e:
            raise unittest.SkipTest(f"Failed to load docker-compose config: {e}")

    def _get_env_var(self, service_name, var_name):
        """Helper to get an environment variable from a service, handling both list and dict formats."""
        service = self.config.get('services', {}).get(service_name, {})
        env = service.get('environment', {})

        if isinstance(env, dict):
            return env.get(var_name)
        elif isinstance(env, list):
            for item in env:
                if item.startswith(f"{var_name}="):
                    return item.split('=', 1)[1]
        return None

    def test_traefik_ulimits_nofile(self):
        """Verify Traefik has high nofile ulimits."""
        traefik = self.config.get('services', {}).get('traefik', {})
        ulimits = traefik.get('ulimits', {})
        nofile = ulimits.get('nofile', {})

        self.assertEqual(nofile.get('soft'), 65535)
        self.assertEqual(nofile.get('hard'), 65535)

    def test_traefik_resource_limits(self):
        """Verify Traefik has resource limits defined."""
        traefik = self.config.get('services', {}).get('traefik', {})
        deploy = traefik.get('deploy', {})
        resources = deploy.get('resources', {})
        limits = resources.get('limits', {})

        self.assertEqual(limits.get('cpus'), 0.75)
        self.assertEqual(limits.get('memory'), "536870912") # 512M in bytes

    def test_traefik_resource_reservations(self):
        """Verify Traefik has resource reservations defined."""
        traefik = self.config.get('services', {}).get('traefik', {})
        deploy = traefik.get('deploy', {})
        resources = deploy.get('resources', {})
        reservations = resources.get('reservations', {})

        self.assertEqual(reservations.get('cpus'), 0.25)
        self.assertEqual(reservations.get('memory'), "134217728") # 128M in bytes

    def test_traefik_gomaxprocs(self):
        """Verify Traefik has GOMAXPROCS set."""
        self.assertEqual(self._get_env_var('traefik', 'GOMAXPROCS'), "1")

    def test_traefik_gomemlimit(self):
        """Verify Traefik has GOMEMLIMIT set."""
        self.assertEqual(self._get_env_var('traefik', 'GOMEMLIMIT'), "460MiB")

    def test_traefik_connection_pooling(self):
        """Verify Traefik connection pooling is tuned."""
        traefik = self.config.get('services', {}).get('traefik', {})
        command = traefik.get('command', [])

        self.assertIn("--serverstransport.maxidleconnsperhost=100", command)

    def test_traefik_idle_timeout(self):
        """Verify Traefik idle timeout is optimized."""
        traefik = self.config.get('services', {}).get('traefik', {})
        command = traefik.get('command', [])

        self.assertIn("--entrypoints.http.transport.respondingTimeouts.idleTimeout=60s", command)

    def test_traefik_read_write_timeouts(self):
        """Verify Traefik read and write timeouts are set."""
        traefik = self.config.get('services', {}).get('traefik', {})
        command = traefik.get('command', [])

        self.assertIn("--entrypoints.http.transport.respondingTimeouts.readTimeout=60s", command)
        self.assertIn("--entrypoints.http.transport.respondingTimeouts.writeTimeout=60s", command)

    def test_portainer_ulimits_nofile(self):
        """Verify Portainer has high nofile ulimits."""
        portainer = self.config.get('services', {}).get('portainer', {})
        ulimits = portainer.get('ulimits', {})
        nofile = ulimits.get('nofile', {})

        self.assertEqual(nofile.get('soft'), 65535)
        self.assertEqual(nofile.get('hard'), 65535)

    def test_portainer_resource_reservations(self):
        """Verify Portainer has resource reservations defined."""
        portainer = self.config.get('services', {}).get('portainer', {})
        deploy = portainer.get('deploy', {})
        resources = deploy.get('resources', {})
        reservations = resources.get('reservations', {})

        self.assertEqual(reservations.get('cpus'), 0.1)
        self.assertEqual(reservations.get('memory'), "67108864") # 64M in bytes

    def test_portainer_gomaxprocs(self):
        """Verify Portainer has GOMAXPROCS set."""
        self.assertEqual(self._get_env_var('portainer', 'GOMAXPROCS'), "1")

if __name__ == '__main__':
    unittest.main()
