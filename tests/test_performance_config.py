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
        cls.traefik_deploy = cls.traefik.get('deploy', {})
        cls.traefik_labels = cls.traefik.get('labels', {})
        cls.traefik_ulimits = cls.traefik.get('ulimits', {})

        cls.portainer = services.get('portainer', {})
        cls.portainer_command = cls.portainer.get('command', [])
        cls.portainer_deploy = cls.portainer.get('deploy', {})
        cls.portainer_ulimits = cls.portainer.get('ulimits', {})

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
        self.assertEqual(reservations.get('memory'), "134217728") # 128M in bytes

    def test_traefik_log_level(self):
        """Verify Traefik log level is set to WARN."""
        self.assertIn("--log.level=WARN", self.traefik_command)

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
        self.assertIn("--api.dashboard=true", self.traefik_command)
        self.assertIn("--api.insecure=false", self.traefik_command)

    def test_traefik_allow_empty_services(self):
        """Verify Traefik allowEmptyServices is enabled."""
        self.assertIn("--providers.docker.allowEmptyServices=true", self.traefik_command)

    def test_traefik_send_anonymous_usage(self):
        """Verify Traefik anonymous usage statistics are disabled."""
        self.assertIn("--global.sendanonymoususage=false", self.traefik_command)

    def test_traefik_allow_empty_services(self):
        """Verify Traefik allowEmptyServices optimization is enabled."""
        self.assertIn("--providers.docker.allowEmptyServices=true", self.traefik_command)

    def test_traefik_ssh_entrypoint(self):
        """Verify Traefik SSH entrypoint is present."""
        self.assertIn("--entrypoints.ssh.address=:22", self.traefik_command)

    def test_traefik_dashboard_router(self):
        """Verify Traefik dashboard router is configured with optimized middleware chain."""
        labels = self.traefik_labels

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
        self.assertIn("--serverstransport.maxidleconns=2000", self.traefik_command)

    def test_traefik_connection_pooling(self):
        """Verify Traefik connection pooling is tuned."""
        self.assertIn("--serverstransport.maxidleconnsperhost=500", self.traefik_command)

    def test_traefik_forwarding_timeouts(self):
        """Verify Traefik forwarding timeouts are set."""
        self.assertIn("--serverstransport.forwardingtimeouts.dialtimeout=1s", self.traefik_command)
        self.assertIn("--serverstransport.forwardingtimeouts.responseheadertimeout=30s", self.traefik_command)

    def test_traefik_idle_timeout(self):
        """Verify Traefik idle timeout is optimized."""
        self.assertIn("--entrypoints.http.transport.respondingtimeouts.idletimeout=30s", self.traefik_command)

    def test_traefik_read_write_timeouts(self):
        """Verify Traefik read and write timeouts are set."""
        self.assertIn("--entrypoints.http.transport.respondingtimeouts.readtimeout=30s", self.traefik_command)
        self.assertIn("--entrypoints.http.transport.respondingtimeouts.writetimeout=30s", self.traefik_command)

    def test_traefik_global_compression(self):
        """Verify Traefik has global compression enabled on the http entrypoint."""
        self.assertIn("--entrypoints.http.http.middlewares=compress@docker", self.traefik_command)

    def test_traefik_compress_middleware_definition(self):
        """Verify Traefik has the compress middleware defined."""
        labels = self.traefik_labels

        # Labels can be a list or a dict in the normalized JSON
        if isinstance(labels, list):
            self.assertIn("traefik.http.middlewares.compress.compress=true", labels)
        else:
            self.assertEqual(labels.get("traefik.http.middlewares.compress.compress"), "true")

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
        env_dict = self._get_env_dict(self.portainer)
        self.assertEqual(env_dict.get('GOMAXPROCS'), "1")

    def test_portainer_gogc(self):
        """Verify Portainer has GOGC set."""
        env_dict = self._get_env_dict(self.portainer)
        self.assertEqual(env_dict.get('GOGC'), "200")

    def test_portainer_snapshot_interval(self):
        """Verify Portainer snapshot interval is optimized."""
        self.assertIn("--snapshot-interval=1h", self.portainer_command)

    def test_portainer_analytics_disabled(self):
        """Verify Portainer anonymous usage statistics are disabled."""
        command = self.portainer.get('command', [])

        self.assertIn("--no-analytics", command)

if __name__ == '__main__':
    unittest.main()
