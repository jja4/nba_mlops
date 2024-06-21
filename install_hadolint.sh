#!/bin/bash

# Script to install Hadolint

set -e

HADOLINT_VERSION="v2.6.0"
HADOLINT_URL="https://github.com/hadolint/hadolint/releases/download/${HADOLINT_VERSION}/hadolint-Linux-x86_64"
INSTALL_DIR="/usr/local/bin"

# Download Hadolint binary
wget -O "${INSTALL_DIR}/hadolint" "${HADOLINT_URL}"

# Make Hadolint executable
chmod +x "${INSTALL_DIR}/hadolint"

echo "Hadolint ${HADOLINT_VERSION} installed successfully to ${INSTALL_DIR}"
