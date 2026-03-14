"""
xhs server — MCP 服务管理命令。
"""
from __future__ import annotations

import click

from xhs_cli.engines.mcp_client import MCPClient, MCPError, MCP_BINARY, MCP_LOG_FILE
from xhs_cli.utils import config
from xhs_cli.utils.output import success, error, info, status, console


@click.group("server", help="MCP 服务管理")
def server_group():
    pass


@server_group.command("start", help="启动 MCP 服务")
@click.option("--port", type=int, default=None, help="端口号 (默认: 18060)")
@click.option("--proxy", default=None, help="代理地址 (默认: http://127.0.0.1:7897)")
@click.option("--no-proxy", is_flag=True, help="不使用代理")
def start(port, proxy, no_proxy):
    """启动 MCP 服务。"""
    cfg = config.load_config()
    port = port or cfg["mcp"]["port"]
    proxy_addr = None if no_proxy else (proxy or cfg["mcp"]["proxy"])

    if MCPClient.is_running(port=port):
        pid = MCPClient.get_server_pid()
        success(f"MCP 服务已在运行 (PID: {pid}, 端口: {port})")
        return

    info(f"正在启动 MCP 服务 (端口: {port})...")
    if proxy_addr:
        info(f"代理: {proxy_addr}")

    try:
        MCPClient.start_server(port=port, proxy=proxy_addr)
        pid = MCPClient.get_server_pid()
        success(f"MCP 服务已启动 (PID: {pid})")
        status("端口", str(port))
        status("日志", MCP_LOG_FILE)
    except MCPError as e:
        error(str(e))
        raise SystemExit(1)


@server_group.command("stop", help="停止 MCP 服务")
def stop():
    """停止 MCP 服务。"""
    pid = MCPClient.get_server_pid()
    if not pid:
        info("MCP 服务未在运行")
        return

    if MCPClient.stop_server():
        success(f"MCP 服务已停止 (PID: {pid})")
    else:
        error("停止 MCP 服务失败")
        raise SystemExit(1)


@server_group.command("status", help="查看 MCP 服务状态")
@click.option("--port", type=int, default=None, help="端口号")
def server_status(port):
    """查看 MCP 服务状态。"""
    cfg = config.load_config()
    port = port or cfg["mcp"]["port"]

    running = MCPClient.is_running(port=port)
    pid = MCPClient.get_server_pid()

    console.print()
    if running:
        success("MCP 服务运行中")
        status("PID", str(pid or "unknown"))
        status("端口", str(port))
        status("地址", f"http://127.0.0.1:{port}/mcp")
    else:
        error("MCP 服务未运行")
        info("使用 [bold]xhs server start[/] 启动服务")
    console.print()


@server_group.command("log", help="查看 MCP 服务日志")
@click.option("-n", "--lines", type=int, default=50, help="显示最后 N 行")
def log(lines):
    """查看 MCP 日志。"""
    import os
    if not os.path.exists(MCP_LOG_FILE):
        info("日志文件不存在")
        return

    with open(MCP_LOG_FILE, "r") as f:
        all_lines = f.readlines()
    for line in all_lines[-lines:]:
        console.print(line.rstrip())
