# Infrastructure Setup

## How WebFetch Works (Confirmed)

Claude Code's WebFetch tool:
- **Runs locally** via Bun's built-in `fetch()` — requests originate from this machine
- **Respects `/etc/hosts`** — uses `getaddrinfo` (libuv/system resolver), so DNS overrides work
- **Supports `NODE_EXTRA_CA_CERTS`** — custom CAs can be added via this environment variable
- **Also reads system CAs** from `/etc/ssl/certs/ca-certificates.crt`

This means the `/etc/hosts` + mkcert approach will work as designed.

## Setup Steps

### 1. Install Dependencies

```bash
# nginx
sudo apt install -y nginx

# mkcert + dependencies
sudo apt install -y libnss3-tools
curl -JLO "https://dl.filippo.io/mkcert/latest?for=linux/amd64"
chmod +x mkcert-v*-linux-amd64
sudo mv mkcert-v*-linux-amd64 /usr/local/bin/mkcert

# Install local CA
mkcert -install
```

### 2. Generate Certificate

```bash
mkdir -p ~/llms-txt-experiment/certs
cd ~/llms-txt-experiment/certs
mkcert documentation.ubuntu.com

# This produces:
#   documentation.ubuntu.com.pem       (certificate)
#   documentation.ubuntu.com-key.pem   (private key)

# Also install into system CA store for belt-and-braces
sudo cp "$(mkcert -CAROOT)/rootCA.pem" /usr/local/share/ca-certificates/mkcert-rootCA.crt
sudo update-ca-certificates
```

### 3. nginx Configuration

```nginx
# /etc/nginx/sites-available/charm-docs

server {
    listen 443 ssl;
    server_name documentation.ubuntu.com;

    ssl_certificate     /home/ubuntu/llms-txt-experiment/certs/documentation.ubuntu.com.pem;
    ssl_certificate_key /home/ubuntu/llms-txt-experiment/certs/documentation.ubuntu.com-key.pem;

    # Separate access log per session (rotated by the runner script)
    access_log /home/ubuntu/llms-txt-experiment/logs/access.log combined;

    # ops docs
    location /ops/ {
        alias /home/ubuntu/llms-txt-experiment/docs-output/operator/;
        try_files $uri $uri/ =404;
    }

    # pebble docs
    location /pebble/ {
        alias /home/ubuntu/llms-txt-experiment/docs-output/pebble/;
        try_files $uri $uri/ =404;
    }

    # jubilant docs
    location /jubilant/ {
        alias /home/ubuntu/llms-txt-experiment/docs-output/jubilant/;
        try_files $uri $uri/ =404;
    }

    # charmlibs docs
    location /charmlibs/ {
        alias /home/ubuntu/llms-txt-experiment/docs-output/charmlibs/;
        try_files $uri $uri/ =404;
    }

    # charmcraft docs
    location /charmcraft/ {
        alias /home/ubuntu/llms-txt-experiment/docs-output/charmcraft/;
        try_files $uri $uri/ =404;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name documentation.ubuntu.com;
    return 301 https://$host$request_uri;
}
```

### 4. /etc/hosts Toggle

```bash
# scripts/enable-local-docs.sh
#!/bin/bash
if ! grep -q "documentation.ubuntu.com" /etc/hosts; then
    echo "127.0.0.1 documentation.ubuntu.com" | sudo tee -a /etc/hosts
    echo "Local docs enabled"
else
    echo "Local docs already enabled"
fi

# scripts/disable-local-docs.sh
#!/bin/bash
sudo sed -i '/documentation.ubuntu.com/d' /etc/hosts
echo "Local docs disabled — using real internet"
```

### 5. Claude Code Launch with CA

For conditions C and D, launch Claude Code with:

```bash
export NODE_EXTRA_CA_CERTS="$(mkcert -CAROOT)/rootCA.pem"
claude  # or however the runner invokes it
```

This ensures WebFetch trusts the local mkcert certificate.

For conditions A and B, this variable is harmless (the local CA exists but documentation.ubuntu.com resolves to the real server), so it can be set globally.

## Building the Docs with sphinx-llm

### Per-Repo Build Process

Each repo needs:
1. Clone the fork
2. Add `sphinx_llm.txt` to the extensions list in `conf.py`
3. Install dependencies (including `sphinx-llm`)
4. Build the docs

```bash
# Example for operator
cd ~/llms-txt-experiment/docs-build/operator/docs

# Add the extension to conf.py (automated via script)
# The exact edit depends on the repo's conf.py structure

# Create a venv and install deps
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # or equivalent
pip install sphinx-llm

# Build
make html

# Copy output
cp -r _build/html/* ~/llms-txt-experiment/docs-output/operator/
```

### charmlibs Special Case

charmlibs uses `.docs/` (with leading dot) instead of `docs/`, and uses a `justfile` for building. Adjust paths accordingly.

### charmcraft Special Case

charmcraft uses RST source and has `.readthedocs.yaml` at the repo root (not in `docs/`). The `sphinx-llm` extension should still work — it converts RST to markdown output regardless of source format. Worth testing early.

## Smoke Test Results (2026-03-26)

All infrastructure components validated successfully:

- [x] **mkcert** — v1.4.4 installed, local CA created and installed in system trust store
- [x] **Certificate** — generated for `documentation.ubuntu.com`, valid until 2028-06-26
- [x] **nginx** — serving over HTTPS on port 443, config passes `nginx -t`
- [x] **/etc/hosts** — `127.0.0.1 documentation.ubuntu.com` correctly intercepts DNS
- [x] **curl test** — `curl https://documentation.ubuntu.com/test/llms.txt` returns content (200)
- [x] **WebFetch test** — Claude Code's WebFetch successfully fetches both `.txt` and `.html` pages over HTTPS from the local server
- [x] **Access logs** — nginx logs capture all requests with user-agent `Claude-User (claude-code/...)` — can distinguish WebFetch from other traffic
- [x] **/etc/hosts toggle** — removing the entry restores normal DNS resolution

**Key finding:** WebFetch (Bun's built-in fetch) resolves DNS via system `getaddrinfo` and trusts the mkcert CA installed via `update-ca-certificates`. No `NODE_EXTRA_CA_CERTS` was needed — the system CA store was sufficient.

**Permission note:** nginx worker (`www-data`) needs `o+rx` on the path to doc files. Applied to `/home/ubuntu`, `/home/ubuntu/llms-txt-experiment`, and doc output directories.

## Verification Checklist

Before running any experiment sessions:

- [x] mkcert, nginx installed and working
- [x] HTTPS + DNS override validated with WebFetch
- [x] nginx access logs capture requests with user-agent
- [ ] All 5 doc sets build successfully with sphinx-llm
- [ ] Each doc set has `llms.txt`, `llms-full.txt`, and per-page `.html.md` files
- [ ] nginx serves all 5 doc sets over HTTPS without errors
- [ ] `curl https://documentation.ubuntu.com/ops/latest/llms.txt` returns content (with /etc/hosts enabled)
- [ ] WebFetch from a test Claude Code session can access real doc pages
- [ ] With /etc/hosts disabled, WebFetch reaches the real `documentation.ubuntu.com`

## Log Collection

For each session, the runner script should:

1. **Rotate nginx access log** — copy current log to `results/raw/{session_id}/access.log` and truncate
2. **Capture Claude Code session data** — token usage, tool calls, responses
3. **Record environment** — condition, model, question, run number, timestamps
