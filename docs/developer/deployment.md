# Deployment

gzkit.org is hosted on a DigitalOcean VPS with Caddy.

## Prerequisites

- DigitalOcean droplet (or any VPS)
- Domain pointed to droplet IP (A record)
- SSH access

## Install Caddy (Debian/Ubuntu)

```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy
```

## Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # or restart shell
```

## Clone and Build

```bash
git clone https://github.com/tvproductions/gzkit.git /var/www/gzkit.org
cd /var/www/gzkit.org
uv sync --extra docs
uv run mkdocs build
```

## Caddyfile

Edit `/etc/caddy/Caddyfile`:

```
gzkit.org {
    root * /var/www/gzkit.org/site
    file_server
}
```

Caddy handles automatically:
- HTTPS cert from Let's Encrypt
- Cert renewal
- HTTP → HTTPS redirect

## Start Caddy

```bash
sudo systemctl enable caddy
sudo systemctl start caddy
```

## Deploy Updates

After pushing changes to the repo:

```bash
cd /var/www/gzkit.org
git pull
uv run mkdocs build
```

Or from local machine:

```bash
ssh user@your-vps "cd /var/www/gzkit.org && git pull && uv run mkdocs build"
```

## Verify

Once DNS propagates and Caddy provisions the cert:

```bash
curl -I https://gzkit.org
```

Should return `HTTP/2 200` with valid TLS.
