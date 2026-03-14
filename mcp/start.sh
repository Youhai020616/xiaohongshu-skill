#!/bin/bash
# 启动小红书 MCP 服务
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 检查是否已在运行
if pgrep -f "xiaohongshu-mcp-darwin-arm64" > /dev/null; then
  echo "[mcp] Already running (PID $(pgrep -f xiaohongshu-mcp-darwin-arm64))"
  exit 0
fi

# 启动（COOKIES_PATH 确保登录态持久化）
echo "[mcp] Starting on port 18060..."
export COOKIES_PATH="$SCRIPT_DIR/cookies.json"
nohup ./xiaohongshu-mcp-darwin-arm64 -port :18060 -rod "proxy=http://127.0.0.1:7897" > mcp.log 2>&1 &
echo "[mcp] Started (PID $!)"
