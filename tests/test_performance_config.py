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
        cls.traefik_command = cls.traefik.get('command', [])
        cls.traefik_cmd_set = set(cls.traefik_command)
        cls.traefik_deploy = cls.traefik.get('deploy', {})
        # Optimization: Normalize labels to a dictionary once in setUpClass to eliminate redundant checks in tests.
        cls.traefik_labels = cls._normalize_labels(cls.traefik)
        cls.traefik_ulimits = cls.traefik.get('ulimits', {})
        # Optimization: Cache normalized environment dictionary to avoid repeated parsing in tests.
        cls.traefik_env = cls._normalize_env(cls.traefik)

        cls.portainer = services.get('portainer', {})
        cls.portainer_command = cls.portainer.get('command', [])
        cls.portainer_cmd_set = set(cls.portainer_command)
        cls.portainer_deploy = cls.portainer.get('deploy', {})
        # Optimization: Normalize labels to a dictionary once in setUpClass to eliminate redundant checks in tests.
        cls.portainer_labels = cls._normalize_labels(cls.portainer)
        cls.portainer_ulimits = cls.portainer.get('ulimits', {})
        # Optimization: Cache normalized environment dictionary to avoid repeated parsing in tests.
        cls.portainer_env = cls._normalize_env(cls.portainer)

    @staticmethod
    def _normalize_env(service_config):
        """Normalize environment to a dictionary regardless of its format."""
        env = service_config.get('environment', {})
        if isinstance(env, list):
            # Optimization: Use dictionary comprehension for faster parsing of environment variables.
            return {k: v for item in env for k, v in [item.split('=', 1)]}
        return env

    @staticmethod
    def _normalize_labels(service_config):
        """Normalize labels to a dictionary regardless of its format."""
        labels = service_config.get('labels', {})
        if isinstance(labels, list):
            # Optimization: Use dictionary comprehension for faster parsing of labels.
            return {k: v for item in labels for k, v in [item.split('=', 1)]}
        return labels

    def test_traefik_ulimits_nofile(self):
        """Verify Traefik has high nofile ulimits."""
        nofile = self.traefik_ulimits.get('nofile', {})

        self.assertEqual(nofile.get('soft'), 65535)
        self.assertEqual(nofile.get('hard'), 65535)

    def test_traefik_resource_limits(self):
        """Verify Traefik has resource limits defined."""
        resources = self.traefik_deploy.get('resources', {})
        limits = resources.get('limits', {})

        self.assertEqual(limits.get('cpus'), 0.75)
        self.assertEqual(limits.get('memory'), "536870912") # 512M in bytes

    def test_traefik_resource_reservations(self):
        """Verify Traefik has resource reservations defined."""
        resources = self.traefik_deploy.get('resources', {})
        reservations = resources.get('reservations', {})

        self.assertEqual(reservations.get('cpus'), 0.25)
        self.assertEqual(reservations.get('memory'), "268435456") # 256M in bytes

    def test_traefik_log_level(self):
        """Verify Traefik log level is set to WARN."""
        self.assertIn("--log.level=WARN", self.traefik_cmd_set)

    def test_traefik_gomaxprocs(self):
        """Verify Traefik has GOMAXPROCS set."""
        self.assertEqual(self.traefik_env.get('GOMAXPROCS'), "1")

    def test_traefik_gomemlimit(self):
        """Verify Traefik has GOMEMLIMIT set."""
        self.assertEqual(self.traefik_env.get('GOMEMLIMIT'), "460MiB")

    def test_traefik_gogc(self):
        """Verify Traefik has GOGC set."""
        self.assertEqual(self.traefik_env.get('GOGC'), "400")

    def test_traefik_api_dashboard(self):
        """Verify Traefik API dashboard is enabled."""
        self.assertIn("--api.dashboard=true", self.traefik_cmd_set)
        self.assertIn("--api.insecure=false", self.traefik_cmd_set)

    def test_traefik_allow_empty_services(self):
        """Verify Traefik allowemptyservices optimization is enabled."""
        self.assertIn("--providers.docker.allowemptyservices=true", self.traefik_cmd_set)

    def test_traefik_docker_provider_filters(self):
        """Verify Traefik Docker provider filters are configured."""
        self.assertIn("--providers.docker.filters=label=traefik.enable=true", self.traefik_cmd_set)

    def test_traefik_send_anonymous_usage(self):
        """Verify Traefik anonymous usage statistics are disabled."""
        self.assertIn("--global.sendanonymoususage=false", self.traefik_cmd_set)

    def test_traefik_ssh_entrypoint(self):
        """Verify Traefik SSH entrypoint is present."""
        self.assertIn("--entrypoints.ssh.address=:22", self.traefik_cmd_set)

    def test_traefik_dashboard_router(self):
        """Verify Traefik dashboard router is configured with optimized middleware chain."""
        # Optimization: Use pre-normalized labels dictionary for direct O(1) lookups.
        labels = self.traefik_labels

        self.assertEqual(labels.get("traefik.http.routers.dashboard.rule"), "Host(`traefik.localhost`)")
        self.assertEqual(labels.get("traefik.http.routers.dashboard.service"), "api@internal")
        self.assertEqual(labels.get("traefik.http.routers.dashboard.entrypoints"), "http")
        self.assertEqual(labels.get("traefik.http.routers.dashboard.middlewares"), "auth@docker")

    def test_traefik_max_idle_conns(self):
        """Verify Traefik global connection pooling is scaled."""
        self.assertIn("--serverstransport.maxidleconns=32000", self.traefik_cmd_set)

    def test_traefik_connection_pooling(self):
        """Verify Traefik connection pooling is tuned."""
        self.assertIn("--serverstransport.maxidleconnsperhost=32000", self.traefik_cmd_set)

    def test_traefik_forwarding_timeouts(self):
        """Verify Traefik forwarding timeouts are set."""
        self.assertIn("--serverstransport.forwardingtimeouts.dialtimeout=100ms", self.traefik_cmd_set)
        self.assertIn("--serverstransport.forwardingtimeouts.responseheadertimeout=1s", self.traefik_cmd_set)

    def test_traefik_backend_idle_timeout(self):
        """Verify Traefik backend idle connection timeout is set."""
        self.assertIn("--serverstransport.forwardingtimeouts.idleconntimeout=1s", self.traefik_cmd_set)

    def test_traefik_idle_timeout(self):
        """Verify Traefik idle timeout is optimized."""
        self.assertIn("--entrypoints.http.transport.respondingtimeouts.idletimeout=1s", self.traefik_cmd_set)

    def test_traefik_read_write_timeouts(self):
        """Verify Traefik read and write timeouts are set."""
        self.assertIn("--entrypoints.http.transport.respondingtimeouts.readtimeout=10s", self.traefik_cmd_set)
        self.assertIn("--entrypoints.http.transport.respondingtimeouts.writetimeout=10s", self.traefik_cmd_set)
        self.assertIn("--entrypoints.http.transport.respondingtimeouts.readheadertimeout=200ms", self.traefik_cmd_set)

    def test_traefik_max_concurrent_streams(self):
        """Verify Traefik HTTP/2 max concurrent streams is optimized."""
        self.assertIn("--entrypoints.http.http2.maxconcurrentstreams=1000", self.traefik_cmd_set)

    def test_traefik_global_compression(self):
        """Verify Traefik has global compression enabled on the http entrypoint."""
        self.assertIn("--entrypoints.http.http.middlewares=compress@docker", self.traefik_cmd_set)

    def test_traefik_compress_middleware_definition(self):
        """Verify Traefik has the compress middleware defined with optimized settings."""
        # Optimization: Use pre-normalized labels dictionary for direct O(1) lookups.
        labels = self.traefik_labels

        self.assertEqual(labels.get("traefik.http.middlewares.compress.compress.encodings"), "zstd,br,gzip")
        self.assertEqual(labels.get("traefik.http.middlewares.compress.compress.minResponseBodyBytes"), "256")

    def test_portainer_ulimits_nofile(self):
        """Verify Portainer has high nofile ulimits."""
        nofile = self.portainer_ulimits.get('nofile', {})

        self.assertEqual(nofile.get('soft'), 65535)
        self.assertEqual(nofile.get('hard'), 65535)

    def test_portainer_resource_limits(self):
        """Verify Portainer has resource limits defined."""
        resources = self.portainer_deploy.get('resources', {})
        limits = resources.get('limits', {})

        self.assertEqual(limits.get('cpus'), 0.5)
        self.assertEqual(limits.get('memory'), "268435456") # 256M in bytes

    def test_portainer_resource_reservations(self):
        """Verify Portainer has resource reservations defined."""
        resources = self.portainer_deploy.get('resources', {})
        reservations = resources.get('reservations', {})

        self.assertEqual(reservations.get('cpus'), 0.1)
        self.assertEqual(reservations.get('memory'), "134217728") # 128M in bytes

    def test_portainer_gomaxprocs(self):
        """Verify Portainer has GOMAXPROCS set."""
        self.assertEqual(self.portainer_env.get('GOMAXPROCS'), "1")

    def test_portainer_gogc(self):
        """Verify Portainer has GOGC set."""
        self.assertEqual(self.portainer_env.get('GOGC'), "200")

    def test_portainer_snapshot_interval(self):
        """Verify Portainer snapshot interval is optimized."""
        self.assertIn("--snapshot-interval=1h", self.portainer_cmd_set)

    def test_portainer_analytics_disabled(self):
        """Verify Portainer anonymous usage statistics are disabled."""
        self.assertIn("--no-analytics", self.portainer_cmd_set)

if __name__ == '__main__':
    unittest.main()
