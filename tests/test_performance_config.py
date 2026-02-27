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

    def test_traefik_gomaxprocs(self):
        """Verify Traefik has GOMAXPROCS set."""
        traefik = self.config.get('services', {}).get('traefik', {})
        env = traefik.get('environment', {})

        self.assertEqual(env.get('GOMAXPROCS'), "1")

    def test_traefik_gomemlimit(self):
        """Verify Traefik has GOMEMLIMIT set."""
        traefik = self.config.get('services', {}).get('traefik', {})
        env = traefik.get('environment', {})

        self.assertEqual(env.get('GOMEMLIMIT'), "460MiB")

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

    def test_portainer_gomaxprocs(self):
        """Verify Portainer has GOMAXPROCS set."""
        portainer = self.config.get('services', {}).get('portainer', {})
        env = portainer.get('environment', {})

        self.assertEqual(env.get('GOMAXPROCS'), "1")

if __name__ == '__main__':
    unittest.main()
