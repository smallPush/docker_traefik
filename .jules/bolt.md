## 2026-02-18 - Optimized Traefik Logging and Compression
**Learning:** `DEBUG` log level in Traefik significantly impacts throughput and increases CPU/IO overhead. Enabling `compress` middleware at the edge reduces bandwidth usage and improves perceived load time for web applications like Portainer.
**Action:** Always prefer `INFO` or `ERROR` log levels in production and enable Gzip compression for text-based service responses.

## 2026-02-19 - Tuned Traefik Connection Pooling
**Learning:** Traefik's default `maxIdleConnsPerHost` can be a bottleneck for high-concurrency workloads. Explicitly increasing it to 100+ ensures that Traefik reuses backend connections more effectively, reducing the latency associated with TCP/TLS handshakes.
**Action:** In high-traffic scenarios, always tune `serversTransport` settings, specifically `maxIdleConnsPerHost`, to match expected concurrency.

## 2026-02-20 - Optimized Docker Provider and Resource Limits
**Learning:** Narrowing the Traefik Docker provider's scope to a specific network reduces service discovery overhead. Additionally, increasing the `nofile` soft limit from the default 1024 is critical for a reverse proxy to handle high concurrency without connection failures.
**Action:** Always specify `--providers.docker.network` when using a dedicated network and ensure `ulimits` are tuned for high-concurrency workloads.
