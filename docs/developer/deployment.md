# Deployment

gzkit.org is served by Caddy from a DigitalOcean droplet. Nobody deploys it by hand: every
published release runs the Docs workflow (`.github/workflows/docs.yml`), which builds the site
once, publishes it to GitHub Pages as a mirror, and rsyncs it to the droplet. A daily check
(`.github/workflows/docs-freshness.yml`) fails when the droplet serves a build older than the
latest release (GHI #802).

The droplet holds only the built site. It needs no clone of the repository and no Python
toolchain.

## How a deploy works

1. The `build` job runs `mkdocs build --strict` and writes `site/build-info.json` with the
   release tag and commit.
2. The `deploy-vps` job rsyncs `site/` to `/var/www/gzkit.org/site` as the `deploy` user, then
   fetches `https://gzkit.org/build-info.json` and fails unless it matches what it uploaded.
3. The `deploy` job publishes the same build to GitHub Pages.

`deploy-vps` and the freshness check are skipped until the `VPS_HOST` repository variable is set.

## One-time server setup

Run on the droplet as a sudo-capable user (Ubuntu or Debian).

### Caddy

```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl rsync
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install -y caddy
```

### Deploy user and site directory

The `deploy` user can write the site directory and nothing else. Its key is restricted by
`rrsync`, so it can only rsync into that one directory: no shell, no other path.

```bash
sudo adduser --system --group --shell /bin/sh --home /home/deploy deploy
sudo install -d -o deploy -g deploy -m 755 /var/www/gzkit.org/site
sudo install -d -o deploy -g deploy -m 700 /home/deploy/.ssh
command -v rrsync || echo "rrsync missing: install rsync 3.2.4+ or copy /usr/share/doc/rsync/scripts/rrsync"
```

### Caddyfile

Write `/etc/caddy/Caddyfile`:

```
gzkit.org, www.gzkit.org {
    root * /var/www/gzkit.org/site
    file_server
}
```

Then start Caddy. It obtains and renews the Let's Encrypt certificate and redirects HTTP to
HTTPS by itself:

```bash
sudo systemctl enable --now caddy
sudo systemctl reload caddy
```

If `ufw` is active, open the web ports: `sudo ufw allow 80,443/tcp`.

## Deploy key and repository settings

Create a key used only by CI, on your own machine (not the droplet):

```bash
ssh-keygen -t ed25519 -N "" -C "gzkit-docs-deploy" -f gzkit-deploy
```

Install the public half on the droplet, restricted to the site directory. Replace `PUBKEY` with
the contents of `gzkit-deploy.pub`:

```bash
echo 'command="rrsync /var/www/gzkit.org/site",restrict PUBKEY' | sudo tee /home/deploy/.ssh/authorized_keys
sudo chown deploy:deploy /home/deploy/.ssh/authorized_keys
sudo chmod 600 /home/deploy/.ssh/authorized_keys
```

Then set the repository secrets and variable from your machine:

```bash
gh secret set VPS_SSH_KEY < gzkit-deploy
ssh-keyscan -t ed25519 gzkit.org | gh secret set VPS_KNOWN_HOSTS
gh variable set VPS_HOST --body gzkit.org
rm gzkit-deploy gzkit-deploy.pub
```

Check the scanned host key against the droplet's own fingerprint
(`ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub` on the droplet) before trusting it.

## First deploy and verify

Run the Docs workflow by hand once:

```bash
gh workflow run docs.yml
gh run watch
```

Then confirm what gzkit.org serves:

```bash
curl -I https://gzkit.org
curl -s https://gzkit.org/build-info.json
```

The first should return `HTTP/2 200` with valid TLS, and the second the latest release tag.

## When the freshness check fails

The check names the served tag and the latest release. Re-run the Docs workflow
(`gh workflow run docs.yml`) and read its `deploy-vps` job. An SSH failure there means the
deploy key or the pinned host key no longer matches the droplet: redo
[Deploy key and repository settings](#deploy-key-and-repository-settings).
