# docker-traefik

docker-traefik provides a ready-to-use Docker + Traefik configuration and examples to run Traefik as a reverse proxy for containerized services. It focuses on an easy developer experience with automatic service discovery via the Docker provider, HTTPS via Let's Encrypt, and a minimal secure default configuration.

## Features

- Traefik v2.x as an edge reverse proxy for Docker containers
- Automatic service discovery using the Docker provider
- HTTPS with Let's Encrypt (ACME) support and configurable certificate resolver
- Built-in dashboard for monitoring routes and certificates
- Example docker-compose and service label patterns
- Guidance for secure acme.json handling and logging

## Table of Contents

- [Quick start](#quick-start)
- [Configuration](#configuration)
- [Docker labels examples](#docker-labels-examples)
- [Let's Encrypt / ACME](#lets-encrypt--acme)
- [Security notes](#security-notes)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Quick start

Create a folder for Traefik configuration (e.g. `traefik/`) and an `acme.json` file for certificates:

```bash
mkdir -p traefik
touch traefik/acme.json
chmod 600 traefik/acme.json
```

Example `docker-compose.yml`:

```yaml
version: "3.8"
services:
  traefik:
    image: traefik:v2.10
    command:
      - --providers.docker=true
      - --providers.docker.exposedbydefault=false
      - --entrypoints.web.address=:80
      - --entrypoints.websecure.address=:443
      - --api.insecure=false
      - --api.dashboard=true
      - --certificatesresolvers.le.acme.httpchallenge.entrypoint=web
      - --certificatesresolvers.le.acme.email=you@example.com
      - --certificatesresolvers.le.acme.storage=/letsencrypt/acme.json
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080" # optional: Traefik dashboard
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./traefik/acme.json:/letsencrypt/acme.json
      - ./traefik/traefik.yml:/etc/traefik/traefik.yml:ro # optional static file
    restart: unless-stopped
    labels:
      - "traefik.enable=true"

  whoami:
    image: containous/whoami
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.whoami.rule=Host(`whoami.local`)"
      - "traefik.http.routers.whoami.entrypoints=websecure"
      - "traefik.http.routers.whoami.tls.certresolver=le"
```

Adjust `whoami.local` to a reachable hostname or map it via `/etc/hosts` during local testing.

## Configuration

You can provide configuration through command-line args (as above) or a static `traefik.yml`. Example static config (optional):

```yaml
api:
  dashboard: true
  insecure: false

entryPoints:
  web:
    address: ":80"
  websecure:
    address: ":443"

providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false

certificatesResolvers:
  le:
    acme:
      email: you@example.com
      storage: /letsencrypt/acme.json
      httpChallenge:
        entryPoint: web
```

## Docker labels examples

- Basic HTTPS router:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.app.rule=Host(`app.example.com`)"
  - "traefik.http.routers.app.entrypoints=websecure"
  - "traefik.http.routers.app.tls.certresolver=le"
```

- Force redirect HTTP -> HTTPS using middleware:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.app.rule=Host(`app.example.com`)"
  - "traefik.http.routers.app.entrypoints=web"
  - "traefik.http.routers.app.middlewares=redirect-to-https@docker"

# Middleware service (can be declared as labels on a container named traefik-middlewares)
labels:
  - "traefik.http.middlewares.redirect-to-https.redirectscheme.scheme=https"
```

## Let's Encrypt / ACME

- Ensure `acme.json` is writable by Traefik and stored outside the container with permissions 600.
- For production, prefer DNS challenges if you need wildcard certificates.
- Configure an appropriate `email` for notifications and legal reasons.

## Security notes

- Do not expose the Traefik dashboard to the public without authentication.
- Mount Docker socket as read-only where possible; limit who can control the socket.
- Keep acme.json file permissions restricted (chmod 600).
- Use network segmentation for internal services.

## Troubleshooting

- Dashboard (if enabled) is typically available on port 8080: http://<host>:8080
- Check Traefik logs for ACME or routing errors.
- Use `docker logs traefik` to inspect runtime messages.
- Common issues: domain DNS not pointing to host, firewall blocking ports 80/443.

## Contributing

Contributions, issue reports, and PRs are welcome. Please open an issue first if you plan a significant change.

## License

Specify your license here (e.g., MIT). Replace this with the appropriate license for your project.
