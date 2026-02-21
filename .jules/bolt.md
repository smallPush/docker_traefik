## 2026-02-18 - Optimized Traefik Logging and Compression
**Learning:** `DEBUG` log level in Traefik significantly impacts throughput and increases CPU/IO overhead. Enabling `compress` middleware at the edge reduces bandwidth usage and improves perceived load time for web applications like Portainer.
**Action:** Always prefer `INFO` or `ERROR` log levels in production and enable Gzip compression for text-based service responses.

## 2026-02-19 - Tuned Traefik Connection Pooling
**Learning:** Traefik's default `maxIdleConnsPerHost` can be a bottleneck for high-concurrency workloads. Explicitly increasing it to 100+ ensures that Traefik reuses backend connections more effectively, reducing the latency associated with TCP/TLS handshakes.
**Action:** In high-traffic scenarios, always tune `serversTransport` settings, specifically `maxIdleConnsPerHost`, to match expected concurrency.

## 2026-02-21 - Optimized Traefik High-Concurrency and Discovery
**Learning:** Default `nofile` ulimits (1024) in Docker containers can bottleneck high-concurrency proxies like Traefik, leading to "too many open files" errors under load. Additionally, specifying `--providers.docker.network` reduces Traefik's internal overhead by eliminating the need to guess the correct network for service backend communication.
**Action:** Always increase `nofile` ulimits for edge proxies and explicitly define the provider network to streamline service discovery.
