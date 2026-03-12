import unittest
try:
    from .config_utils import get_docker_compose_config
except ImportError:
    from config_utils import get_docker_compose_config

class TestDockerComposePerformance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = get_docker_compose_config()

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

    def test_traefik_log_level(self):
        """Verify Traefik log level is set to WARN."""
        traefik = self.config.get('services', {}).get('traefik', {})
        command = traefik.get('command', [])

        self.assertIn("--log.level=WARN", command)

    def _get_env_dict(self, service_name):
        """Normalize environment to a dictionary regardless of its format."""
        env = self.config.get('services', {}).get(service_name, {}).get('environment', {})
        if isinstance(env, list):
            return dict(item.split('=', 1) for item in env)
        return env

    def test_traefik_gomaxprocs(self):
        """Verify Traefik has GOMAXPROCS set."""
        env_dict = self._get_env_dict('traefik')
        self.assertEqual(env_dict.get('GOMAXPROCS'), "1")

    def test_traefik_gomemlimit(self):
        """Verify Traefik has GOMEMLIMIT set."""
        env_dict = self._get_env_dict('traefik')
        self.assertEqual(env_dict.get('GOMEMLIMIT'), "460MiB")

    def test_traefik_api_dashboard(self):
        """Verify Traefik API dashboard is enabled."""
        traefik = self.config.get('services', {}).get('traefik', {})
        command = traefik.get('command', [])

        self.assertIn("--api.dashboard=true", command)
        self.assertIn("--api.insecure=false", command)

    def test_traefik_ssh_entrypoint(self):
        """Verify Traefik SSH entrypoint is present."""
        traefik = self.config.get('services', {}).get('traefik', {})
        command = traefik.get('command', [])

        self.assertIn("--entrypoints.ssh.address=:22", command)

    def test_traefik_dashboard_router(self):
        """Verify Traefik dashboard router is configured."""
        traefik = self.config.get('services', {}).get('traefik', {})
        labels = traefik.get('labels', {})

        if isinstance(labels, list):
            self.assertIn("traefik.http.routers.dashboard.rule=Host(`traefik.localhost`)", labels)
            self.assertIn("traefik.http.routers.dashboard.service=api@internal", labels)
            self.assertIn("traefik.http.routers.dashboard.entrypoints=http", labels)
        else:
            self.assertEqual(labels.get("traefik.http.routers.dashboard.rule"), "Host(`traefik.localhost`)")
            self.assertEqual(labels.get("traefik.http.routers.dashboard.service"), "api@internal")
            self.assertEqual(labels.get("traefik.http.routers.dashboard.entrypoints"), "http")

    def test_traefik_max_idle_conns(self):
        """Verify Traefik global connection pooling is scaled."""
        traefik = self.config.get('services', {}).get('traefik', {})
        command = traefik.get('command', [])

        self.assertIn("--serverstransport.maxidleconns=1000", command)

    def test_traefik_connection_pooling(self):
        """Verify Traefik connection pooling is tuned."""
        traefik = self.config.get('services', {}).get('traefik', {})
        command = traefik.get('command', [])

        self.assertIn("--serverstransport.maxidleconnsperhost=250", command)

    def test_traefik_forwarding_timeouts(self):
        """Verify Traefik forwarding timeouts are set."""
        traefik = self.config.get('services', {}).get('traefik', {})
        command = traefik.get('command', [])

        self.assertIn("--serverstransport.forwardingtimeouts.dialtimeout=2s", command)
        self.assertIn("--serverstransport.forwardingtimeouts.responseheadertimeout=30s", command)

    def test_traefik_idle_timeout(self):
        """Verify Traefik idle timeout is optimized."""
        traefik = self.config.get('services', {}).get('traefik', {})
        command = traefik.get('command', [])

        self.assertIn("--entrypoints.http.transport.respondingtimeouts.idletimeout=60s", command)

    def test_traefik_read_write_timeouts(self):
        """Verify Traefik read and write timeouts are set."""
        traefik = self.config.get('services', {}).get('traefik', {})
        command = traefik.get('command', [])

        self.assertIn("--entrypoints.http.transport.respondingtimeouts.readtimeout=60s", command)
        self.assertIn("--entrypoints.http.transport.respondingtimeouts.writetimeout=60s", command)

    def test_traefik_global_compression(self):
        """Verify Traefik has global compression enabled on the http entrypoint."""
        traefik = self.config.get('services', {}).get('traefik', {})
        command = traefik.get('command', [])

        self.assertIn("--entrypoints.http.http.middlewares=compress@docker", command)

    def test_traefik_compress_middleware_definition(self):
        """Verify Traefik has the compress middleware defined."""
        traefik = self.config.get('services', {}).get('traefik', {})
        labels = traefik.get('labels', {})

        # Labels can be a list or a dict in the normalized JSON
        if isinstance(labels, list):
            self.assertIn("traefik.http.middlewares.compress.compress=true", labels)
        else:
            self.assertEqual(labels.get("traefik.http.middlewares.compress.compress"), "true")

    def test_portainer_ulimits_nofile(self):
        """Verify Portainer has high nofile ulimits."""
        portainer = self.config.get('services', {}).get('portainer', {})
        ulimits = portainer.get('ulimits', {})
        nofile = ulimits.get('nofile', {})

        self.assertEqual(nofile.get('soft'), 65535)
        self.assertEqual(nofile.get('hard'), 65535)

    def test_portainer_resource_limits(self):
        """Verify Portainer has resource limits defined."""
        portainer = self.config.get('services', {}).get('portainer', {})
        deploy = portainer.get('deploy', {})
        resources = deploy.get('resources', {})
        limits = resources.get('limits', {})

        self.assertEqual(limits.get('cpus'), 0.5)
        self.assertEqual(limits.get('memory'), "268435456") # 256M in bytes

    def test_portainer_resource_reservations(self):
        """Verify Portainer has resource reservations defined."""
        portainer = self.config.get('services', {}).get('portainer', {})
        deploy = portainer.get('deploy', {})
        resources = deploy.get('resources', {})
        reservations = resources.get('reservations', {})

        self.assertEqual(reservations.get('cpus'), 0.1)
        self.assertEqual(reservations.get('memory'), "134217728") # 128M in bytes

    def test_portainer_gomaxprocs(self):
        """Verify Portainer has GOMAXPROCS set."""
        env_dict = self._get_env_dict('portainer')
        self.assertEqual(env_dict.get('GOMAXPROCS'), "1")

    def test_portainer_snapshot_interval(self):
        """Verify Portainer snapshot interval is optimized."""
        portainer = self.config.get('services', {}).get('portainer', {})
        command = portainer.get('command', [])

        self.assertIn("--snapshot-interval=1h", command)

    def test_portainer_gomaxprocs(self):
        """Verify Portainer has GOMAXPROCS set."""
        portainer = self.config.get('services', {}).get('portainer', {})
        env = portainer.get('environment', {})

        self.assertEqual(env.get('GOMAXPROCS'), "1")

    def test_portainer_ulimits_nofile(self):
        """Verify Portainer has high nofile ulimits."""
        portainer = self.config.get('services', {}).get('portainer', {})
        ulimits = portainer.get('ulimits', {})
        nofile = ulimits.get('nofile', {})

        self.assertEqual(nofile.get('soft'), 65535)
        self.assertEqual(nofile.get('hard'), 65535)

    def test_portainer_gomaxprocs(self):
        """Verify Portainer has GOMAXPROCS set."""
        portainer = self.config.get('services', {}).get('portainer', {})
        env = portainer.get('environment', {})

        self.assertEqual(env.get('GOMAXPROCS'), "1")

if __name__ == '__main__':
    unittest.main()
