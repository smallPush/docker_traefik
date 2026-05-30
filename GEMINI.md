# Gemini Project Context: docker-traefik

## Project Overview
`docker-traefik` provides a highly optimized Docker + Traefik v3 configuration designed for high-concurrency environments. It serves as an edge reverse proxy with built-in service discovery, automated resource management, and a focus on performance and security.

### Core Technologies
- **Traefik v3.6**: Primary edge proxy and load balancer.
- **Portainer CE**: Management UI for Docker environments.
- **Docker Compose**: Orchestration for the local/edge stack.
- **Python (unittest)**: Comprehensive test suite for configuration validation.

### Architecture
The project employs a "fail-fast" architecture with hyper-aggressive timeouts tuned for stable, low-latency internal Docker networks. Services communicate over a dedicated external network (`rubofvil_lan`).

## Building and Running
### Environment Setup
A `.env` file is required to provide sensitive configuration, specifically:
- `TRAEFIK_DASHBOARD_AUTH`: Basic auth credentials for the Traefik dashboard (format: `user:hashed_password`).

### Key Commands
- **Start Stack**: `docker compose up -d`
- **Stop Stack**: `docker compose down`
- **Validate Configuration**: `docker compose config`
- **Run Tests**: `python3 -m unittest discover tests`

## Development Conventions
### Performance Standards
- **Connection Pooling**: Global connection pools (`maxidleconns`) are scaled to the aggregate of all backend quotas (currently 128,000) to prevent contention.
- **Go Runtime Tuning**: Traefik and other Go services use `GOMAXPROCS=1` (aligned with CPU limits), `GOMEMLIMIT` (90% of memory limit), and relaxed `GOGC` (e.g., 1000) for maximum throughput.
- **Timeouts**: Aggressive timeouts (100ms dial, 1s response header, 1s idle) are used to reclaim resources quickly.

### Security Practices
- **Network Isolation**: All backend services (like Portainer) must NOT expose ports directly. Access is routed exclusively through Traefik.
- **Socket Security**: The Docker socket is mounted as read-only (`:ro`) for the Traefik service.
- **Credential Management**: No plain-text credentials in `docker-compose.yml`; use environment variables.

### Testing and Validation
- All performance and security optimizations documented in `.jules/bolt.md` must be reflected in the test suite (`tests/`).
- Use `setUpClass` in tests to cache `docker compose config` output to minimize execution time.
- Prefer manual loops with `partition('=')` for parsing large lists of Docker environment/label strings.

## Key Files
- `docker-compose.yml`: Main stack definition with extensive inline documentation of optimizations.
- `tests/test_performance_config.py`: Validates performance flags and runtime settings.
- `tests/test_security.py`: Validates security constraints (port exposure, socket permissions, auth).
- `.jules/bolt.md`: Chronological log of architectural decisions, learnings, and optimization actions.
