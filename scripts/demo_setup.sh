#!/bin/bash

############################################################################
#
#    Agno Demo Environment Setup
#
#    Usage: ./scripts/demo_setup.sh
#    Run:   python cookbook/01_demo/run.py
#
############################################################################

set -e

CURR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "${CURR_DIR}")"
AGNO_DIR="${REPO_ROOT}/libs/agno"
VENV_DIR="${REPO_ROOT}/.venvs/demo"

# Colors
ORANGE='\033[38;5;208m'
DIM='\033[2m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${ORANGE}"
cat << 'BANNER'
     █████╗  ██████╗ ███╗   ██╗ ██████╗
    ██╔══██╗██╔════╝ ████╗  ██║██╔═══██╗
    ███████║██║  ███╗██╔██╗ ██║██║   ██║
    ██╔══██║██║   ██║██║╚██╗██║██║   ██║
    ██║  ██║╚██████╔╝██║ ╚████║╚██████╔╝
    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝
BANNER
echo -e "${NC}"
echo -e "    ${DIM}Demo Environment Setup${NC}"
echo ""

# Preflight
if [[ -n "$VIRTUAL_ENV" ]]; then
    echo "    Deactivate your current venv first."
    exit 1
fi

if ! command -v uv &> /dev/null; then
    echo "    uv not found. Install: https://docs.astral.sh/uv/"
    exit 1
fi

# Setup
echo -e "    ${DIM}Removing old environment...${NC}"
echo -e "    ${DIM}> rm -rf ${VENV_DIR}${NC}"
rm -rf ${VENV_DIR}

echo ""
echo -e "    ${DIM}Creating Python 3.12 venv...${NC}"
echo -e "    ${DIM}> uv venv ${VENV_DIR} --python 3.12${NC}"
uv venv ${VENV_DIR} --python 3.12 --quiet

echo ""
echo -e "    ${DIM}Installing agno[demo]...${NC}"
echo -e "    ${DIM}> VIRTUAL_ENV=${VENV_DIR} uv pip install -e ${AGNO_DIR}[demo]${NC}"
VIRTUAL_ENV=${VENV_DIR} uv pip install -e ${AGNO_DIR}[demo] --quiet

# Copy activation command to clipboard if a tool is available
ACTIVATE_CMD="source .venvs/demo/bin/activate"
COPIED=false
if command -v pbcopy &> /dev/null; then
    echo -n "${ACTIVATE_CMD}" | pbcopy
    COPIED=true
elif command -v xclip &> /dev/null; then
    echo -n "${ACTIVATE_CMD}" | xclip -selection clipboard
    COPIED=true
elif command -v xsel &> /dev/null; then
    echo -n "${ACTIVATE_CMD}" | xsel --clipboard --input
    COPIED=true
fi

echo ""
echo -e "    ${BOLD}Done.${NC}"
echo ""
echo -e "    ${DIM}Activate:${NC}  ${ACTIVATE_CMD}"
echo -e "    ${DIM}Run Demo:${NC}  python cookbook/01_demo/run.py"
echo ""
if [ "$COPIED" = true ]; then
    echo -e "    ${DIM}(Activation command copied to clipboard. Just paste and hit enter.)${NC}"
    echo ""
fi
