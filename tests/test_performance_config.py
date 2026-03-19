import unittest
try:
    from .config_utils import get_docker_compose_config
except ImportError:
    from config_utils import get_docker_compose_config

class TestDockerComposePerformance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = get_docker_compose_config()
        services = cls.config.get('services', {})
        cls.traefik = services.get('traefik', {})
        cls.portainer = services.get('portainer', {})

    def test_traefik_ulimits_nofile(self):
        """Verify Traefik has high nofile ulimits."""
        ulimits = self.traefik.get('ulimits', {})
        nofile = ulimits.get('nofile', {})

        self.assertEqual(nofile.get('soft'), 65535)
        self.assertEqual(nofile.get('hard'), 65535)

    def test_traefik_resource_limits(self):
        """Verify Traefik has resource limits defined."""
        deploy = self.traefik.get('deploy', {})
        resources = deploy.get('resources', {})
        limits = resources.get('limits', {})

        self.assertEqual(limits.get('cpus'), 0.75)
        self.assertEqual(limits.get('memory'), "536870912") # 512M in bytes

    def test_traefik_resource_reservations(self):
        """Verify Traefik has resource reservations defined."""
        deploy = self.traefik.get('deploy', {})
        resources = deploy.get('resources', {})
        reservations = resources.get('reservations', {})

        self.assertEqual(reservations.get('cpus'), 0.25)
        self.assertEqual(reservations.get('memory'), "134217728") # 128M in bytes

    def test_traefik_log_level(self):
        """Verify Traefik log level is set to WARN."""
        command = self.traefik.get('command', [])

        self.assertIn("--log.level=WARN", command)

    def _get_env_dict(self, service_config):
        """Normalize environment to a dictionary regardless of its format."""
        env = service_config.get('environment', {})
        if isinstance(env, list):
            return dict(item.split('=', 1) for item in env)
        return env

    def test_traefik_gomaxprocs(self):
        """Verify Traefik has GOMAXPROCS set."""
        env_dict = self._get_env_dict(self.traefik)
        self.assertEqual(env_dict.get('GOMAXPROCS'), "1")

    def test_traefik_gomemlimit(self):
        """Verify Traefik has GOMEMLIMIT set."""
        env_dict = self._get_env_dict(self.traefik)
        self.assertEqual(env_dict.get('GOMEMLIMIT'), "460MiB")

    def test_traefik_gogc(self):
        """Verify Traefik has GOGC set."""
        env_dict = self._get_env_dict(self.traefik)
        self.assertEqual(env_dict.get('GOGC'), "200")

    def test_traefik_api_dashboard(self):
        """Verify Traefik API dashboard is enabled."""
        command = self.traefik.get('command', [])

        self.assertIn("--api.dashboard=true", command)
        self.assertIn("--api.insecure=false", command)

    def test_traefik_send_anonymous_usage(self):
        """Verify Traefik anonymous usage statistics are disabled."""
        command = self.traefik.get('command', [])

        self.assertIn("--global.sendanonymoususage=false", command)

    def test_traefik_ssh_entrypoint(self):
        """Verify Traefik SSH entrypoint is present."""
        command = self.traefik.get('command', [])

        self.assertIn("--entrypoints.ssh.address=:22", command)

    def test_traefik_dashboard_router(self):
        """Verify Traefik dashboard router is configured with optimized middleware chain."""
        labels = self.traefik.get('labels', {})

        if isinstance(labels, list):
            self.assertIn("traefik.http.routers.dashboard.rule=Host(`traefik.localhost`)", labels)
            self.assertIn("traefik.http.routers.dashboard.service=api@internal", labels)
            self.assertIn("traefik.http.routers.dashboard.entrypoints=http", labels)
            self.assertIn("traefik.http.routers.dashboard.middlewares=auth@docker", labels)
        else:
            self.assertEqual(labels.get("traefik.http.routers.dashboard.rule"), "Host(`traefik.localhost`)")
            self.assertEqual(labels.get("traefik.http.routers.dashboard.service"), "api@internal")
            self.assertEqual(labels.get("traefik.http.routers.dashboard.entrypoints"), "http")
            self.assertEqual(labels.get("traefik.http.routers.dashboard.middlewares"), "auth@docker")

    def test_traefik_max_idle_conns(self):
        """Verify Traefik global connection pooling is scaled."""
        command = self.traefik.get('command', [])

        self.assertIn("--serverstransport.maxidleconns=2000", command)

    def test_traefik_connection_pooling(self):
        """Verify Traefik connection pooling is tuned."""
        command = self.traefik.get('command', [])

        self.assertIn("--serverstransport.maxidleconnsperhost=500", command)

    def test_traefik_forwarding_timeouts(self):
        """Verify Traefik forwarding timeouts are set."""
        command = self.traefik.get('command', [])

        self.assertIn("--serverstransport.forwardingtimeouts.dialtimeout=1s", command)
        self.assertIn("--serverstransport.forwardingtimeouts.responseheadertimeout=30s", command)

    def test_traefik_idle_timeout(self):
        """Verify Traefik idle timeout is optimized."""
        command = self.traefik.get('command', [])

        self.assertIn("--entrypoints.http.transport.respondingtimeouts.idletimeout=30s", command)

    def test_traefik_read_write_timeouts(self):
        """Verify Traefik read and write timeouts are set."""
        command = self.traefik.get('command', [])

        self.assertIn("--entrypoints.http.transport.respondingtimeouts.readtimeout=30s", command)
        self.assertIn("--entrypoints.http.transport.respondingtimeouts.writetimeout=30s", command)

    def test_traefik_global_compression(self):
        """Verify Traefik has global compression enabled on the http entrypoint."""
        command = self.traefik.get('command', [])

        self.assertIn("--entrypoints.http.http.middlewares=compress@docker", command)

    def test_traefik_compress_middleware_definition(self):
        """Verify Traefik has the compress middleware defined."""
        labels = self.traefik.get('labels', {})

        # Labels can be a list or a dict in the normalized JSON
        if isinstance(labels, list):
            self.assertIn("traefik.http.middlewares.compress.compress=true", labels)
        else:
            self.assertEqual(labels.get("traefik.http.middlewares.compress.compress"), "true")

    def test_portainer_ulimits_nofile(self):
        """Verify Portainer has high nofile ulimits."""
        ulimits = self.portainer.get('ulimits', {})
        nofile = ulimits.get('nofile', {})

        self.assertEqual(nofile.get('soft'), 65535)
        self.assertEqual(nofile.get('hard'), 65535)

    def test_portainer_resource_limits(self):
        """Verify Portainer has resource limits defined."""
        deploy = self.portainer.get('deploy', {})
        resources = deploy.get('resources', {})
        limits = resources.get('limits', {})

        self.assertEqual(limits.get('cpus'), 0.5)
        self.assertEqual(limits.get('memory'), "268435456") # 256M in bytes

    def test_portainer_resource_reservations(self):
        """Verify Portainer has resource reservations defined."""
        deploy = self.portainer.get('deploy', {})
        resources = deploy.get('resources', {})
        reservations = resources.get('reservations', {})

        self.assertEqual(reservations.get('cpus'), 0.1)
        self.assertEqual(reservations.get('memory'), "134217728") # 128M in bytes

    def test_portainer_gomaxprocs(self):
        """Verify Portainer has GOMAXPROCS set."""
        env_dict = self._get_env_dict(self.portainer)
        self.assertEqual(env_dict.get('GOMAXPROCS'), "1")

    def test_portainer_gogc(self):
        """Verify Portainer has GOGC set."""
        env_dict = self._get_env_dict(self.portainer)
        self.assertEqual(env_dict.get('GOGC'), "200")

    def test_portainer_snapshot_interval(self):
        """Verify Portainer snapshot interval is optimized."""
        command = self.portainer.get('command', [])

        self.assertIn("--snapshot-interval=1h", command)

    def test_portainer_analytics_disabled(self):
        """Verify Portainer anonymous usage statistics are disabled."""
        command = self.portainer.get('command', [])

        self.assertIn("--no-analytics", command)

if __name__ == '__main__':
    unittest.main()
