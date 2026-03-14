#!/usr/bin/env bash
# 激活 xhs-cli 环境
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/.venv/bin/activate"
echo "📕 xhs-cli 环境已激活，输入 xhs --help 开始使用"
