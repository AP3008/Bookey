#!/usr/bin/env bash
set -e

BOLD="\033[1m"
GREEN="\033[38;2;166;227;161m"
RED="\033[38;2;243;139;168m"
DIM="\033[38;2;108;112;134m"
MAUVE="\033[38;2;203;166;247m"
RESET="\033[0m"

echo ""
echo -e "${MAUVE}${BOLD}  Installing Bookey...${RESET}"
echo ""

# ── Check Python ──────────────────────────────────────────────

if ! command -v python3 &> /dev/null; then
    echo -e "  ${RED}Python 3 is not installed. Please install Python 3.10+ first.${RESET}"
    exit 1
fi

PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.minor}")')
PY_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')

if [ "$PY_MAJOR" -lt 3 ] || [ "$PY_VERSION" -lt 10 ]; then
    echo -e "  ${RED}Python 3.10+ is required. You have Python ${PY_MAJOR}.${PY_VERSION}.${RESET}"
    exit 1
fi

echo -e "  ${GREEN}Python 3.${PY_VERSION} found${RESET}"

# ── Check / Install pipx ─────────────────────────────────────

if ! command -v pipx &> /dev/null; then
    echo -e "  ${DIM}pipx not found, installing...${RESET}"
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath
    echo -e "  ${GREEN}pipx installed${RESET}"

    # Source the updated PATH so pipx is available immediately
    export PATH="$HOME/.local/bin:$PATH"
fi

echo -e "  ${GREEN}pipx found${RESET}"

# ── Install Bookey ────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo -e "  ${DIM}Installing bookey via pipx...${RESET}"
pipx install --force "$SCRIPT_DIR"

echo ""
echo -e "  ${GREEN}${BOLD}Bookey installed successfully!${RESET}"
echo ""
echo -e "  ${BOLD}Next steps:${RESET}"
echo -e "  ${DIM}1. Get your Google OAuth credentials.json from the Google Cloud Console${RESET}"
echo -e "  ${DIM}2. Place it at: ~/.config/bookey/credentials.json${RESET}"
echo -e "  ${DIM}3. Run ${RESET}${MAUVE}bk${RESET}${DIM} to get started!${RESET}"
echo ""
