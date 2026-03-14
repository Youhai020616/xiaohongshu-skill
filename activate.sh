#!/usr/bin/env bash
# 激活 xhs-cli 环境
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/.venv/Scripts/activate" ]; then
    source "$SCRIPT_DIR/.venv/Scripts/activate"
elif [ -f "$SCRIPT_DIR/.venv/bin/activate" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
else
    echo "❌ 虚拟环境未找到，请先运行: bash setup.sh"
    return 1 2>/dev/null || exit 1
fi
echo "📕 xhs-cli 环境已激活，输入 xhs --help 开始使用"
