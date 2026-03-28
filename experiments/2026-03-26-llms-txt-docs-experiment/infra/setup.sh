#!/bin/bash
# Setup script for the llms.txt experiment infrastructure.
#
# Prerequisites:
#   - Ubuntu 24.04 VM with passwordless sudo
#   - uv (https://docs.astral.sh/uv/)
#   - git
#
# This script:
#   1. Installs nginx + mkcert
#   2. Generates a trusted TLS certificate for documentation.ubuntu.com
#   3. Clones the doc repos (shallow)
#   4. Builds docs with sphinx-llm for each repo
#   5. Configures nginx to serve them locally
#
# After running, toggle /etc/hosts with enable-local-docs.sh / disable-local-docs.sh.

set -euo pipefail

EXPERIMENT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORK_DIR="${HOME}/llms-txt-experiment"

echo "=== Setting up llms.txt experiment ==="
echo "Working directory: ${WORK_DIR}"

# --- 1. Install dependencies ---

echo "Installing nginx and mkcert..."
sudo apt install -y nginx libnss3-tools

if ! command -v mkcert &>/dev/null; then
    curl -JLO "https://dl.filippo.io/mkcert/latest?for=linux/amd64"
    chmod +x mkcert-v*-linux-amd64
    sudo mv mkcert-v*-linux-amd64 /usr/local/bin/mkcert
fi

# --- 2. Generate certificate ---

echo "Setting up TLS certificate..."
mkcert -install

mkdir -p "${WORK_DIR}/certs"
cd "${WORK_DIR}/certs"
if [ ! -f documentation.ubuntu.com.pem ]; then
    mkcert documentation.ubuntu.com
fi

# Install into system CA store
sudo cp "$(mkcert -CAROOT)/rootCA.pem" /usr/local/share/ca-certificates/mkcert-rootCA.crt
sudo update-ca-certificates

# --- 3. Clone repos ---

echo "Cloning doc repos (shallow)..."
mkdir -p "${WORK_DIR}/docs-build"

REPOS="operator pebble jubilant charmlibs charmcraft juju"
# Adjust the GitHub org per repo
for repo in ${REPOS}; do
    if [ -d "${WORK_DIR}/docs-build/${repo}" ]; then
        echo "  ${repo}: already cloned"
        continue
    fi
    case "${repo}" in
        juju) org="tonyandrewmeyer" ;;  # or juju/juju upstream
        *)    org="tonyandrewmeyer" ;;
    esac
    echo "  Cloning ${org}/${repo}..."
    git clone --depth 1 "https://github.com/${org}/${repo}.git" \
        "${WORK_DIR}/docs-build/${repo}"
done

# --- 4. Build docs with sphinx-llm ---

echo "Building docs with sphinx-llm..."
mkdir -p "${WORK_DIR}/docs-output"

for repo in ${REPOS}; do
    echo "  Building ${repo}..."

    cd "${WORK_DIR}/docs-build/${repo}"

    # Determine docs directory
    if [ "${repo}" = "charmlibs" ]; then
        DOCS_DIR=".docs"
    else
        DOCS_DIR="docs"
    fi

    # Create venv and install deps
    if [ ! -d .venv ]; then
        case "${repo}" in
            charmcraft) uv venv .venv --python 3.12 ;;
            *)          uv venv .venv --python 3.11 ;;
        esac
    fi
    source .venv/bin/activate

    # Install doc requirements
    if [ -f "${DOCS_DIR}/requirements.txt" ]; then
        uv pip install -r "${DOCS_DIR}/requirements.txt" sphinx-llm
    elif [ -f "${DOCS_DIR}/.sphinx/requirements.txt" ]; then
        uv pip install -r "${DOCS_DIR}/.sphinx/requirements.txt" sphinx-llm
    fi

    # Install the package itself (needed for autodoc)
    case "${repo}" in
        operator)
            uv pip install -e .
            ;;
        jubilant)
            uv pip install -e .
            ;;
        charmcraft)
            uv pip install pydantic-kitbash sphinxext-rediraffe sphinx-substitution-extensions
            uv pip install -e . 2>/dev/null || true
            ;;
        charmlibs)
            # Install all sub-packages for autodoc
            for pkg in pathops snap apt passwd sysctl systemd; do
                [ -f "${pkg}/pyproject.toml" ] && uv pip install -e "./${pkg}"
            done
            ;;
    esac

    # Add sphinx_llm.txt extension if not already present
    CONF="${DOCS_DIR}/conf.py"
    if ! grep -q 'sphinx_llm' "${CONF}"; then
        # Find the last extension in the list and add after it
        sed -i '/^]$/i\    "sphinx_llm.txt",' "${CONF}" 2>/dev/null || \
        sed -i '/"sphinx_sitemap",/a\    "sphinx_llm.txt",' "${CONF}" 2>/dev/null || \
        echo "WARNING: Could not add sphinx_llm.txt to ${CONF} — add manually"
    fi

    # Build
    if [ "${repo}" = "charmlibs" ]; then
        # charmlibs needs a two-pass build: per-package autodoc, then combined
        # Remove sphinx_llm.txt for per-package pass (uvx envs don't have it)
        sed -i '/"sphinx_llm.txt",/d' "${CONF}"

        if command -v just &>/dev/null; then
            # Per-package pass via justfile
            for pkg in apt nginx_k8s passwd pathops snap sysctl systemd \
                       interfaces/certificate_transfer interfaces/k8s_backup_target \
                       interfaces/otlp interfaces/sloth interfaces/tls-certificates; do
                uvx --from sphinx \
                    --with-requirements .sphinx/requirements.txt \
                    --with "${WORK_DIR}/docs-build/charmlibs/${pkg}" \
                    sphinx-build -T --keep-going -b dirhtml \
                    -d .sphinx/.doctrees -D language=en \
                    -D "package=${pkg}" \
                    -D 'suppress_warnings=ref.ref,ref.doc,myst.xref_missing' \
                    . _build/html 2>&1 | tail -1
            done
        fi

        # Re-add sphinx_llm.txt for combined pass
        sed -i '/"sphinx_sitemap",/a\    "sphinx_llm.txt",' "${CONF}"

        # Combined pass with sphinx-llm
        sphinx-build --keep-going -b dirhtml . _build/html \
            -c . -d .sphinx/.doctrees -j auto 2>&1 | tail -3

        BUILD_OUTPUT="_build/html"
    else
        cd "${DOCS_DIR}"
        sphinx-build --keep-going -b dirhtml . _build \
            -c . -d .sphinx/.doctrees -j auto 2>&1 | tail -3
        BUILD_OUTPUT="_build"
    fi

    # Copy output
    mkdir -p "${WORK_DIR}/docs-output/${repo}"
    cp -r ${BUILD_OUTPUT}/* "${WORK_DIR}/docs-output/${repo}/"
    chmod -R o+rX "${WORK_DIR}/docs-output/${repo}/"

    deactivate
    cd "${WORK_DIR}"
done

# Fix permissions for nginx
chmod o+rx "${HOME}" "${WORK_DIR}" "${WORK_DIR}/docs-output"

# --- 5. Configure nginx ---

echo "Configuring nginx..."
mkdir -p "${WORK_DIR}/logs"

# Update paths in nginx config to match this installation
sed "s|/home/ubuntu/llms-txt-experiment|${WORK_DIR}|g" \
    "${EXPERIMENT_DIR}/infra/nginx-charm-docs.conf" \
    > "${WORK_DIR}/nginx-charm-docs.conf"

sudo ln -sf "${WORK_DIR}/nginx-charm-docs.conf" /etc/nginx/sites-enabled/charm-docs.conf
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

echo ""
echo "=== Setup complete ==="
echo ""
echo "To enable local docs (for conditions C/D/E):"
echo "  bash ${EXPERIMENT_DIR}/infra/enable-local-docs.sh"
echo ""
echo "To disable (for conditions A/B):"
echo "  bash ${EXPERIMENT_DIR}/infra/disable-local-docs.sh"
echo ""
echo "To verify:"
echo "  curl https://documentation.ubuntu.com/ops/llms.txt"
