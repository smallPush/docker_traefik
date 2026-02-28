## 2026-02-18 - Optimized Traefik Logging and Compression
**Learning:** `DEBUG` log level in Traefik significantly impacts throughput and increases CPU/IO overhead. Enabling `compress` middleware at the edge reduces bandwidth usage and improves perceived load time for web applications like Portainer.
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

## 2026-02-26 - Version-Specific Go Tuning and Resource Reservations
**Learning:** Not all Go-based images support 'GOMEMLIMIT' (added in Go 1.19). For example, older Portainer images like 'portainer-ce:2.6.0' use an earlier Go version where this variable is a no-op. Additionally, defining 'reservations' in Docker Compose provides a performance baseline by ensuring the scheduler always allocates a minimum amount of resources to critical services.
**Action:** Check the Go version of a container image before applying 'GOMEMLIMIT' and use resource reservations to prevent service starvation.
