#!/usr/bin/env bash
# install.sh — Universal installer for skill-breed across AI agents and development environments.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_TARGET="/usr/local/bin/skill-breed"

echo "================================================================================"
echo "  🧬 Installing skill-breed (Interspecific Agent Skills Hybridizer)"
echo "================================================================================"

# 1. Install Python package
if command -v pip &>/dev/null; then
    echo "==> Installing Python package via pip (editable mode)..."
    pip install -e "$REPO_DIR" --quiet
fi

# 2. Integrate into AI Agent environments
integrate_rule() {
    local target_file="$1"
    local rule_content="$2"
    mkdir -p "$(dirname "$target_file")"
    if [ ! -f "$target_file" ] || ! grep -q "skill-breed" "$target_file" 2>/dev/null; then
        echo -e "\n$rule_content" >> "$target_file"
        echo "    ✓ Integrated into: $target_file"
    fi
}

RULE_TEXT="### 🧬 Skill-Breed Gate\nWhen combining or synthesizing agent capabilities, use \`skill-breed breed <skill_a> <skill_b>\` to ensure heterosis and resolve boundary conflicts."

echo "==> Configuring AI Assistant Rules..."
[ -f "CLAUDE.md" ] && integrate_rule "CLAUDE.md" "$RULE_TEXT"
[ -f "GEMINI.md" ] && integrate_rule "GEMINI.md" "$RULE_TEXT"
[ -f "AGENTS.md" ] && integrate_rule "AGENTS.md" "$RULE_TEXT"
[ -f ".cursorrules" ] && integrate_rule ".cursorrules" "$RULE_TEXT"
[ -f ".windsurfrules" ] && integrate_rule ".windsurfrules" "$RULE_TEXT"

echo "================================================================================"
echo "  ✔ skill-breed successfully installed! Run 'skill-breed --help' to start."
echo "================================================================================"
