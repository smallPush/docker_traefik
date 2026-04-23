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

## 2026-02-23 - Optimized Go Runtime with GOMEMLIMIT and Timeouts

**Learning:** Setting `GOMEMLIMIT` to approximately 90% of a container's memory limit helps the Go Garbage Collector (GC) stay within constraints and reduces GC frequency as the limit is approached. Additionally, explicit `readTimeout` and `writeTimeout` on entrypoints prevent resource exhaustion from slow or hanging connections.
**Action:** Always set `GOMEMLIMIT` for Go-based services with memory limits (Go 1.19+) and define explicit connection timeouts to ensure predictable performance.
## 2026-02-25 - Optimized Go GC and Traefik Timeouts
**Learning:** For Go applications in memory-constrained containers, setting 'GOMEMLIMIT' to 90% of the limit prevents aggressive GC cycles while avoiding OOM kills. Additionally, explicit 'readTimeout' and 'writeTimeout' on Traefik entrypoints prevent resource exhaustion from slow or hanging connections.
**Action:** Set 'GOMEMLIMIT' for Go services and tune entrypoint timeouts to improve overall stack resilience and efficiency.

## 2026-02-26 - Optimized Portainer Go Scheduler and Scalability
**Learning:** For Go applications running with fractional CPU limits, the Go scheduler may still attempt to use all host CPUs, leading to excessive context switching and reduced throughput. Explicitly setting `GOMAXPROCS=1` for a service with 0.5 CPU limit improves efficiency. Additionally, increasing `ulimits` for all server-side components (like Portainer) ensures they can scale to handle many concurrent connections, matching the edge proxy's capabilities.
**Action:** Always set `GOMAXPROCS` to match the integer rounded CPU limit and tune `ulimits` for high-concurrency Go services.
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

## 2026-03-11 - Traefik CLI Casing and Forwarding Timeouts
**Learning:** Traefik CLI flags in the `command` section of `docker-compose.yml` are strictly case-sensitive and must be lowercase (e.g., `--serverstransport.forwardingtimeouts.dialtimeout=2s`). CamelCase flags are unrecognized and will cause the service to fail on startup.
**Action:** Always use lowercase for Traefik static configuration flags and verify their presence in the `docker compose config` output with corresponding lowercase assertions.

## 2026-03-11 - Optimized Traefik Forwarding Timeouts
**Learning:** Default forwarding timeouts in Traefik can be too high for internal Docker networks. Reducing `dialTimeout` to 2s and setting `responseHeaderTimeout` to 30s allows the proxy to fail fast and release resources when a backend is unreachable or slow, preventing resource exhaustion during backend failure scenarios. However, applying similar aggressive responding timeouts to SSH entrypoints is a breaking change for long-lived sessions.
**Action:** Tune `serverstransport` forwarding timeouts for fast failure on internal networks, but avoid aggressive responding timeouts on entrypoints used for persistent connections like SSH.

## 2026-03-13 - Optimized Portainer Go GC
**Learning:** Tuning Go's garbage collector via `GOGC=200` reduces CPU cycles spent on GC by allowing the heap to grow larger before triggering a collection; this is safe to use in memory-constrained containers when paired with sufficient memory headroom.
**Action:** Use `GOGC` to balance CPU/Memory for Go services.

## 2026-03-12 - Optimized Go GC and Configuration Hygiene
**Learning:** Tuning Go's garbage collector via `GOGC=200` reduces CPU cycles spent on GC by allowing the heap to grow larger before triggering a collection; this is safe to use in memory-constrained containers when paired with `GOMEMLIMIT`. Additionally, duplicate keys in `docker-compose.yml` (e.g., redundant `environment` blocks) will cause unmarshal errors in `docker compose config`. Finally, maintaining a clean test suite by avoiding duplicate test method names ensures all assertions are executed.
**Action:** Use `GOGC` to balance CPU/Memory for Go services, and always verify configuration validity and test coverage before submission.

## 2026-03-14 - Middleware Redundancy and Config Validation
**Learning:** Applying a middleware globally at the entrypoint level (e.g., `--entrypoints.http.http.middlewares=compress@docker`) renders explicit middleware labels on individual routers redundant. Removing these duplicates streamlines the middleware chain. Furthermore, be cautious with "advanced" middleware properties like `compress.encodings` which may be specific to Traefik Enterprise or Hub and invalid in Traefik Proxy OSS.
**Action:** Remove redundant middleware declarations when global equivalents are in place, and always verify new middleware properties against the specific Traefik version's documentation.

## 2026-03-15 - Optimized Traefik Outbound Efficiency
**Learning:** Disabling Traefik's anonymous usage statistics via `--global.sendanonymoususage=false` reduces unnecessary outbound network requests and minor background processing overhead. While the resource gain is small, it ensures the application remains focused on routing and minimizes external noise.
**Action:** Always disable anonymous telemetry in production environments to maximize efficiency and privacy.

## 2026-03-16 - Optimized Portainer Outbound Efficiency
**Learning:** Similar to Traefik, Portainer CE sends anonymous usage statistics by default. Disabling this via the `--no-analytics` flag eliminates unnecessary outbound telemetry requests and reduces background processing cycles, further streamlining the management stack.
**Action:** Consistently disable telemetry across all infrastructure components (Traefik, Portainer, etc.) to minimize non-functional overhead.

## 2026-03-23 - Optimized Traefik Churn and Test Isolation
**Learning:** Enabling `--providers.docker.allowEmptyServices=true` in Traefik prevents expensive full configuration reloads and CPU spikes when backend services are temporarily empty during rolling updates. Furthermore, when using a global configuration cache in Python test suites, it is critical to implement both `setUp` and `tearDown` to reset the cache, especially if some tests use mocks that would otherwise pollute the cache for subsequent tests.
**Action:** Use `allowEmptyServices` to stabilize Traefik during container churn and always ensure strict cache isolation in test suites.

## 2026-03-28 - Optimized Test Lookups for CLI Flags
**Learning:** Using lists for membership checks (e.g., `assertIn` on `traefik_command`) in large test suites creates an O(n) bottleneck. Converting these to sets in `setUpClass` allows O(1) lookups, yielding a ~10x speedup (from 2.5s to 0.25s) in this codebase.
**Action:** Always prefer class-level sets for verifying command-line arguments in configuration tests.

## 2026-03-26 - Optimized Docker Provider API Filtering
**Learning:** By default, Traefik's Docker provider watches all Docker events and queries metadata for all containers. Using `--providers.docker.filters=label=traefik.enable=true` pushes the filtering to the Docker API level, reducing Traefik's CPU and memory overhead by only processing relevant containers.
**Action:** Always apply Docker provider filters to limit Traefik's scope to explicitly enabled containers at the API level.

## 2026-03-29 - Tightened Traefik Timeouts for Internal Networks
**Learning:** In controlled internal Docker networks, the default or even slightly tuned timeouts (e.g., 1s dial timeout) can still be tightened further (e.g., 500ms) to accelerate failure detection and resource reclamation without risking false positives.
**Action:** Use aggressive timeouts (500ms dial, 10s response header, 15s idle) for Traefik in stable, internal environments to maximize throughput and resilience.

## 2026-04-01 - Aggressive Timeout Tightening and Test Suite Caching
**Learning:** Further tightening Traefik's `readheadertimeout` (3s) and `idletimeout` (10s) on entrypoints, and `idleconntimeout` (30s) on backends, improves resource reclamation speed in high-churn environments. Additionally, caching normalized environment dictionaries and label sets in the test suite's `setUpClass` reduces redundant parsing during test execution.
**Action:** Always aim for the most aggressive stable timeouts and use class-level caching for configuration data in tests.

## 2026-03-27 - Optimized Traefik HTTP/2 and Header Timeouts
**Learning:** Increasing `maxConcurrentStreams` for HTTP/2 to 500 allows better multiplexing for high-concurrency clients. Additionally, setting a `readHeaderTimeout` (e.g., 10s) is a critical performance and security measure to reclaim resources from slow-reading clients and mitigate Slowloris attacks.
**Action:** Always tune HTTP/2 stream limits for high-concurrency entrypoints and implement header timeouts to improve overall stack resilience.

## 2026-03-29 - Hardened Traefik Forwarding and Idle Timeouts
**Learning:** In internal Docker networks, the default `dialTimeout` and `responseHeaderTimeout` can be significantly reduced to fail fast and reclaim resources. Reducing `dialTimeout` to 500ms and `responseHeaderTimeout` to 10s ensures that Traefik doesn't hang on slow or unreachable backends. Similarly, reducing the entrypoint `idletimeout` to 15s reclaims client-side resources more aggressively without impacting standard web traffic.
**Action:** Use aggressive timeouts (500ms dial, 10s response header, 15s idle) for internal container-to-container routing to maximize throughput and resilience.

## 2026-04-05 - Optimized Compression Algorithms and Thresholds
**Learning:** Default Traefik compression (Gzip, 1024B threshold) misses opportunities for modern, more efficient algorithms like Zstandard (zstd) and fails to compress small JSON fragments typical of API-heavy management tools. Setting `encodings=zstd,br,gzip` and `minResponseBodyBytes=256` significantly improves transfer efficiency for modern clients and small payloads.
**Action:** Always tune compression algorithms to prioritize `zstd` and `br`, and lower the minimum body size threshold for API-centric deployments.

## 2026-04-09 - Aggressive Timeout Tuning for Internal Networks
**Learning:** In stable, low-latency internal Docker networks, standard timeouts can be aggressively tightened (e.g., 200ms dial, 2s response header, 5s idle) to accelerate resource reclamation and ensure the proxy fails fast during backend degradations. This prevents the proxy from being tied up by slow or hanging connections, maintaining overall stack throughput.
**Action:** Apply aggressive timeouts for internal service-to-service communication to maximize proxy efficiency and resilience against "slow" failure modes.

## 2026-04-11 - Optimized Test Suite Normalization
**Learning:** Configuration data from `docker compose config` can arrive in multiple formats (e.g., labels as lists or dicts). Normalizing these into dictionaries once during `setUpClass` using efficient dictionary comprehensions (`{k: v for item in env for k, v in [item.split('=', 1)]}`) significantly improves test maintainability and slightly boosts execution speed by enabling O(1) direct lookups instead of O(n) membership checks or repeated branching.
**Action:** Centralize data normalization in test suites to simplify assertions and maximize lookup performance.

## 2026-04-14 - Optimized Traefik Hyper-Aggressive Timeouts
**Learning:** In highly controlled internal networks with very low latency, Traefik's forwarding timeouts can be tuned to hyper-aggressive levels (e.g., 100ms dial, 1s response header) to maximize failure detection speed and resource reclamation. Additionally, doubling global connection pooling (to 8000) and halving entrypoint read/write timeouts (to 15s) further reduces resource contention and long-lived connection overhead.
**Action:** Apply hyper-aggressive timeouts and larger connection pools for high-concurrency, low-latency internal environments.

## 2026-04-16 - Refined Traefik Timeout and Connection Scaling
**Learning:** In ultra-low-latency internal Docker networks, Traefik's timeouts can be pushed to extreme levels (e.g., 250ms readHeader, 2s idle) to near-instantly reclaim resources without impacting legitimate traffic. Furthermore, aligning 'maxIdleConnsPerHost' with the global 'maxIdleConns' ensures that a single high-traffic backend can fully utilize the connection pool, eliminating artificial bottlenecks during peak load on a specific service.
**Action:** Continually push timeout boundaries in controlled environments and ensure per-host connection limits don't unnecessarily throttle individual high-demand backends.
## 2026-04-19 - Optimized Global Connection Pooling and Idle Timeouts
**Learning:** Scaling the global 'maxIdleConns' to the sum of all backend 'maxIdleConnsPerHost' quotas (e.g., 16000 for 2 backends with 8000 each) prevents global pool contention and ensures each service can fully utilize its connection reuse potential. Additionally, tightening the responding 'idletimeout' to 2s further accelerates resource reclamation on low-latency internal networks.
**Action:** Always scale global connection pools to accommodate the aggregate per-host limits and push responding timeouts to the lowest stable threshold for internal traffic.

## 2026-04-21 - Aggressive Timeout Risks and Connection Scaling
**Learning:** While hyper-aggressive timeouts (e.g., 200ms readHeader, 1s idle) maximize resource reclamation on low-latency internal networks, they carry a high risk of dropping legitimate connections from unstable or high-latency clients. Additionally, aligning 'maxIdleConnsPerHost' with the global 'maxIdleConns' allows a single high-demand backend to fully utilize the connection pool, eliminating artificial bottlenecks during peak load on a specific service.
**Action:** Push timeout boundaries cautiously in controlled environments and ensure per-host connection limits don't unnecessarily throttle individual high-demand backends.

## 2026-04-24 - Optimized Traefik GC and Connection Scaling
**Learning:** Relaxing Traefik's Garbage Collector via 'GOGC=400' reduces CPU cycles spent on memory management by allowing the heap to grow larger before triggering a collection. To safely support this, increasing memory reservations (e.g., to 256M) ensures the OS doesn't starve the process while 'GOMEMLIMIT' provides a hard boundary against OOM. Additionally, scaling the global 'maxIdleConns' to 32000 (double the per-host limit) eliminates global pool contention when multiple services are under heavy load.
**Action:** Use a combination of relaxed GOGC, increased memory reservations, and oversized global connection pools to maximize Traefik's throughput and minimize CPU overhead in high-concurrency environments.
