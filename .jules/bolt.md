## 2026-02-18 - Optimized Traefik Logging and Compression
**Learning:** `DEBUG` log level in Traefik significantly impacts throughput and increases CPU/IO overhead. Enabling `compress` middleware at the edge reduces bandwidth usage and improves perceived load time for web applications like Portainer.
**Action:** Always prefer `INFO` or `ERROR` log levels in production and enable Gzip compression for text-based service responses.

## 2026-02-19 - Tuned Traefik Connection Pooling
**Learning:** Traefik's default `maxIdleConnsPerHost` can be a bottleneck for high-concurrency workloads. Explicitly increasing it to 100+ ensures that Traefik reuses backend connections more effectively, reducing the latency associated with TCP/TLS handshakes.
**Action:** In high-traffic scenarios, always tune `serversTransport` settings, specifically `maxIdleConnsPerHost`, to match expected concurrency.

## 2026-02-20 - Implemented Portainer Resource Limits
**Learning:** Containers without resource limits can become "noisy neighbors," consuming excessive CPU and memory if a process misbehaves. This can starve critical infrastructure like Traefik. While a baseline couldn't be established due to network timeouts preventing image pulls, adding these limits is a preemptive optimization for stability and predictable performance.
**Action:** Always define `deploy.resources.limits` for management services like Portainer to ensure they operate within a controlled footprint (e.g., 0.5 CPU, 256M RAM).
