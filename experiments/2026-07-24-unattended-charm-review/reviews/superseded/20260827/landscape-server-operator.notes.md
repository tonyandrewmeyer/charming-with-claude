# Landscape Server Operator Review — Working Notes

## Context
- Machine charm (not k8s), single charm `landscape-server`
- Published to charmhub: rev 472 on 26.04/edge (2026-08-25)
- Local HEAD: b753f20 @ 2026-07-17 (David Britton)
- Active contributors: 419 David Britton, 301 Andreas Hasenack, 235 Free Ekanayaka

## Deployment Summary
- Model: rv-ls-test on concierge-lxd (Juju 3.6.27)
- Deployed from charmhub: landscape-server 26.04/edge rev 472
- Install took ~3 min 16 sec
- Related: postgresql 16/stable + rabbitmq-server latest/edge
- All 10 Landscape services running, active status achieved

## Key Findings

### CRITICAL
1. Secret token in error logs — src/charm.py:285, logger.error with full Pydantic errors()

### HIGH  
2. Services restart on every config-changed — src/charm.py:466, no change detection
3. Unit tests crash pytest — tests/unit/test_settings_files.py:79,87, Path.replace() bug

### MEDIUM
4. _update_wsl_distributions returns True on FileNotFoundError — src/charm.py:847
5. Non-leader skips WSL distribution update — src/charm.py:1096-1097

### LOW
6. SMTP config line parsing: line.split("=") vs split("=",1) — src/charm.py:2253
7. PostgreSQL password variable shadowed — src/charm.py:1079-1087 (cosmetic)
8. HAProxy route requirements written on every config hook — src/charm.py:466

## Commands Run
```bash
# Deploy
juju add-model rv-ls-test localhost/localhost -c concierge-lxd
juju deploy landscape-server --channel 26.04/edge --base ubuntu@24.04
juju deploy postgresql --channel 16/stable
juju deploy rabbitmq-server --channel latest/edge
juju relate landscape-server:database postgresql:database
juju relate landscape-server:inbound-amqp rabbitmq-server
juju relate landscape-server:outbound-amqp rabbitmq-server

# Tests
cd /home/ubuntu/charm-review/work/landscape-server-operator/repo
uv run ruff check src/ tests/  # All checks passed
uv run pytest tests/unit -x -q --tb=short  # CRASHES at teardown

# Observing
juju status
juju debug-log --replay --no-tail
juju ssh landscape-server/0 -- sudo systemctl list-units 'landscape-*'
juju run landscape-server/0 get-service-conf
juju run landscape-server/0 pause
juju run landscape-server/0 resume

# Config tests
juju config landscape-server worker_counts=4
juju config landscape-server redirect_https=invalid_value
juju config landscape-server appserver_base_port=8080 pingserver_base_port=8080
```

## Service Restart Evidence
```
20:20:27 - outbound-amqp config-changed: Starting services
20:21:41 - appserver_base_port config-changed: Starting services  
20:22:40 - invalid redirect_https config: Starting services
20:23:20 - appserver_base_port=8080 invalid config (blocked)
20:23:41 - site_name=test-name (trivial): Starting services  ← confirmed!
20:23:45 - config-changed: Starting services
```

## Unit test crash traceback
```
TypeError: Path.replace() takes 2 positional arguments but 3 were given
  File "test_settings_files.py", line 79, in fake_open
    path.replace("/etc/systemd/system", str(tmp_path))
  File "test_settings_files.py", line 87, in fake_exists
    path.replace("/etc/systemd/system", str(tmp_path))
```

## Secret leak evidence (from debug-log)
```
ERROR ... Invalid configuration: [{'type': 'value_error', 'loc': (), 
  'msg': 'Value error, Configured service base ports...',
  'input': {'secret_token': 'IqDpccZgsb3xD...',
            'cookie_encryption_key': '8i-e75VXIgMm...',
            'ssl_key': '', 'ssl_cert': 'DEFAULT', ...}}]
```

## Files reviewed
- src/charm.py (full, 2643 lines)
- src/config.py (full)
- src/database.py (full)
- src/helpers.py (full)
- src/settings_files.py (full)
- src/haproxy.py (full)
- src/autoregistration.py (not read - simple script)
- tests/unit/test_settings_files.py (fixture bug confirmed)
- tests/unit/test_charm.py (partial)
- tests/integration/test_bundle.py (full)
- charmcraft.yaml, metadata.yaml, config.yaml, actions.yaml
- terraform/, AGENTS.md, CONTRIBUTING.md, README.md
- pyproject.toml, Makefile
