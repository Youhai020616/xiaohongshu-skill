"""
xhs me / profile — 用户信息命令。
"""
from __future__ import annotations

import json

import click

from xhs_cli.engines.mcp_client import MCPClient, MCPError
from xhs_cli.utils import config
from xhs_cli.utils.output import (
    success, error, info, warning, console,
    print_profile, print_json, status,
)


@click.command("me", help="查看自己的账号信息")
@click.option("--json-output", "as_json", is_flag=True, help="输出 JSON")
def me(as_json):
    """获取当前登录账号信息（通过 check_login_status + user_profile）。"""
    cfg = config.load_config()
    client = MCPClient(host=cfg["mcp"]["host"], port=cfg["mcp"]["port"])

    info("正在获取账号信息...")
    try:
        # Step 1: check login status
        login_result = client.get_self_info()
        if as_json:
            print_json(login_result)
            return

        # 解析 check_login_status 的文本
        text = _extract_text(login_result)
        if "已登录" in text:
            success("已登录小红书")
            # 提取用户名
            for line in text.split("\n"):
                line = line.strip()
                if line and not line.startswith("✅") and "可以使用" not in line:
                    console.print(f"  {line}")
        else:
            error("未登录")
            info("请运行: xhs login")
            raise SystemExit(1)

    except MCPError as e:
        error(f"获取信息失败: {e}")
        info("请确保 MCP 服务已启动且已登录")
        raise SystemExit(1)


def _extract_text(result) -> str:
    """从 MCP 结果中提取文本。"""
    if isinstance(result, dict):
        content = result.get("content", [])
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    parts.append(item.get("text", ""))
            return "\n".join(parts)
        # 尝试直接取 text
        return result.get("text", str(result))
    return str(result)


@click.command("profile", help="查看用户主页")
@click.argument("user_id")
@click.option("--token", "-t", required=True, help="xsec_token")
@click.option("--json-output", "as_json", is_flag=True, help="输出 JSON")
def profile(user_id, token, as_json):
    """查看任意用户的主页信息和笔记。"""
    cfg = config.load_config()
    client = MCPClient(host=cfg["mcp"]["host"], port=cfg["mcp"]["port"])

    info(f"正在获取用户资料: {user_id}")
    try:
        result = client.user_profile(user_id, token)
        if as_json:
            print_json(result)
        else:
            print_profile(result)
    except MCPError as e:
        error(f"获取用户资料失败: {e}")
        raise SystemExit(1)
