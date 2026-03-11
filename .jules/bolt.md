## 2026-02-18 - Optimized Traefik Logging and Compression
**Learning:** `DEBUG` log level in Traefik significantly impacts throughput and increases CPU/IO overhead. Enabling `compress` middleware at the edge reduces bandwidth usage and improves load times for web applications like Portainer.
**Action:** Always prefer `INFO` or `ERROR` log levels in production and enable Gzip compression for text-based service responses.

## 2026-02-19 - Tuned Traefik Connection Pooling
**Learning:** Traefik's default `maxIdleConnsPerHost` can be a bottleneck for high-concurrency workloads. Explicitly increasing it to 100+ ensures that Traefik reuses backend connections more effectively, reducing the latency associated with TCP/TLS handshakes.
**Action:** In high-traffic scenarios, always tune `serversTransport` settings, specifically `maxIdleConnsPerHost`, to match expected concurrency.

## 2026-02-20 - Implemented Portainer Resource Limits
**Learning:** Containers without resource limits can become "noisy neighbors," consuming excessive CPU and memory if a process misbehaves. This can starve critical infrastructure like Traefik. While a baseline couldn't be established due to network timeouts preventing image pulls, adding these limits is a preemptive optimization for stability and predictable performance.
**Action:** Always define `deploy.resources.limits` for management services like Portainer to ensure they operate within a controlled footprint (e.g., 0.5 CPU, 256M RAM).

## 2026-02-21 - Optimized Traefik High-Concurrency and Discovery
**Learning:** Default `nofile` ulimits (1024) in Docker containers can bottleneck high-concurrency proxies like Traefik, leading to "too many open files" errors under load. Additionally, specifying `--providers.docker.network` reduces Traefik's internal overhead by eliminating the need to guess the correct network for service backend communication.
**Action:** Always increase `nofile` ulimits for edge proxies and explicitly define the provider network to streamline service discovery.

## 2026-02-20 - Optimized Docker Provider and Resource Limits
**Learning:** Narrowing the Traefik Docker provider's scope to a specific network reduces service discovery overhead. Additionally, increasing the `nofile` soft limit from the default 1024 is critical for a reverse proxy to handle high concurrency without connection failures.
**Action:** Always specify `--providers.docker.network` when using a dedicated network and ensure `ulimits` are tuned for high-concurrency workloads.

## 2026-02-22 - Optimized Go Runtime for Traefik
**Learning:** For Go applications like Traefik running with fractional CPU limits (e.g., 0.75), the Go scheduler may still attempt to use all host CPUs, leading to excessive context switching. Explicitly setting `GOMAXPROCS` to match the integer rounded CPU limit improves efficiency.
**Action:** Set `GOMAXPROCS` environment variable in Docker Compose to match the `deploy.resources.limits.cpus`.

## 2026-02-25 - Optimized Go GC and Traefik Timeouts
**Learning:** For Go applications in memory-constrained containers, setting 'GOMEMLIMIT' to 90% of the limit prevents aggressive GC cycles while avoiding OOM kills. Additionally, explicit 'readTimeout' and 'writeTimeout' on Traefik entrypoints prevent resource exhaustion from slow or hanging connections.
**Action:** Set 'GOMEMLIMIT' for Go services and tune entrypoint timeouts to improve overall stack resilience and efficiency.

## 2026-02-26 - Portainer Runtime Tuning and Test Robustness
**Learning:** Portainer CE 2.6.0 (Go-based) performance is optimized by setting 'GOMAXPROCS=1' (matching its 0.5 CPU limit) and increasing 'nofile' ulimits to 65535. Note that GOMEMLIMIT is not supported in this version due to its older Go runtime. Additionally, test scripts validating environment variables in 'docker-compose.yml' must handle both list and dictionary normalization to be robust.
**Action:** Align 'GOMAXPROCS' with fractional CPU limits for all Go services and implement robust environment variable parsing in performance tests.

## 2026-02-27 - Portainer Resource Reservations and Test Refactoring
**Learning:** Adding resource reservations for management services like Portainer prevents performance degradation and starvation when the host system is under heavy load. Furthermore, refactoring test suites to use a centralized normalization method for Docker environment variables (handling both list and dict formats) significantly improves maintainability and reliability of performance assertions.
**Action:** Always define resource reservations for critical services and use a common `_get_env_dict` helper in performance tests.

## 2026-02-28 - Global Compression with Traefik v3 Default Middlewares
**Learning:** Traefik v3 allows defining default middlewares for entrypoints. Moving compression from individual services to the entrypoint level ensures all services benefit from Gzip/Brotli by default, reducing configuration redundancy and ensuring a consistent performance baseline across the entire infrastructure.
**Action:** Use `--entrypoints.<name>.http.middlewares` to apply performance-enhancing middlewares like `compress` globally at the edge.

## 2026-03-01 - Optimized Portainer Background Overhead
**Learning:** Portainer's default snapshot interval (5m) creates unnecessary periodic background Docker socket polling in stable environments. Increasing this to 1h significantly reduces background CPU/IO noise without impacting core functionality.
**Action:** Tune `--snapshot-interval` for management services to reduce unnecessary polling overhead.

## 2026-03-08 - Optimized Dashboard Performance and Connection Scaling
**Learning:** Routing management dashboards via Traefik labels (using the `api@internal` service) allows them to benefit from global performance middlewares like compression, even if the insecure API is maintained for backward compatibility. Furthermore, scaling both `maxIdleConns` (global) and `maxIdleConnsPerHost` (per-host) is essential for maximizing throughput in proxies handling multiple concurrent backend connections.
**Action:** Always route internal services through optimized entrypoints and tune both levels of connection pooling for high-concurrency workloads.

## 2026-03-10 - Optimized Test Suite Performance via Configuration Caching
**Learning:** Repetitive execution of expensive external commands (like `docker compose config`) within a test suite creates a significant and avoidable bottleneck. Caching the parsed configuration at the class level (`setUpClass`) instead of the method level (`setUp`) can yield massive relative performance gains (e.g., ~44% reduction in total execution time).
**Action:** Always use `setUpClass` to load and parse shared infrastructure configurations in test suites to minimize subprocess overhead.

## 2026-03-11 - Optimized Traefik Forwarding Timeouts
**Learning:** Default forwarding timeouts in Traefik can be too high for internal Docker networks. Reducing `dialTimeout` to 2s and setting `responseHeaderTimeout` to 30s allows the proxy to fail fast and release resources when a backend is unreachable or slow, preventing resource exhaustion during backend failure scenarios. However, applying similar aggressive responding timeouts to SSH entrypoints is a breaking change for long-lived sessions.
**Action:** Tune `serverstransport` forwarding timeouts for fast failure on internal networks, but avoid aggressive responding timeouts on entrypoints used for persistent connections like SSH.
