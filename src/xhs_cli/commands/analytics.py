"""
xhs analytics / notifications — 数据分析命令（CDP 专属）。
"""
from __future__ import annotations

import click

from xhs_cli.engines.cdp_client import CDPClient, CDPError
from xhs_cli.utils import config
from xhs_cli.utils.output import (
    success, error, info, warning, console,
    print_analytics, print_json,
)


def _get_cdp(account=None):
    cfg = config.load_config()
    return CDPClient(
        host=cfg["cdp"]["host"],
        port=cfg["cdp"]["port"],
        account=account,
        headless=True,
        reuse_tab=True,
    )


@click.command("analytics", help="📊 数据看板 (创作者数据分析)")
@click.option("--csv", "csv_file", default=None, help="导出 CSV 文件路径")
@click.option("--page-size", type=int, default=10, help="每页条数 (默认 10)")
@click.option("--account", default=None, help="账号名")
@click.option("--json-output", "as_json", is_flag=True, help="输出 JSON")
def analytics(csv_file, page_size, account, as_json):
    """获取创作者数据看板（仅 CDP 支持）。"""
    client = _get_cdp(account)
    info("正在获取数据看板 (CDP)...")

    try:
        result = client.content_data(csv_file=csv_file, page_size=page_size)
    except CDPError as e:
        error(f"获取数据失败: {e}")
        info("请确保 Chrome 已启动且已登录")
        raise SystemExit(1)

    if as_json:
        print_json(result)
    else:
        print_analytics(result)

    if csv_file:
        success(f"CSV 已导出: {csv_file}")


@click.command("notifications", help="🔔 通知消息 (提及/互动)")
@click.option("--wait", type=float, default=18.0, help="等待时间 (秒, 默认 18)")
@click.option("--account", default=None, help="账号名")
@click.option("--json-output", "as_json", is_flag=True, help="输出 JSON")
def notifications(wait, account, as_json):
    """获取通知消息（仅 CDP 支持）。"""
    client = _get_cdp(account)
    info(f"正在获取通知消息 (等待 {wait}s)...")

    try:
        result = client.notifications(wait_seconds=wait)
    except CDPError as e:
        error(f"获取通知失败: {e}")
        raise SystemExit(1)

    if as_json:
        print_json(result)
    else:
        _print_notifications(result)


def _print_notifications(data: dict):
    """格式化输出通知。"""
    from rich.table import Table
    from rich import box

    mentions = data.get("mentions", data.get("data", []))
    if not mentions:
        if isinstance(mentions, list) and len(mentions) == 0:
            info("暂无新通知")
        else:
            # 可能数据格式不同，直接打印
            print_json(data)
        return

    table = Table(title="🔔 通知消息", box=box.ROUNDED, show_lines=True)
    table.add_column("#", style="dim", width=3)
    table.add_column("类型", width=8)
    table.add_column("用户", max_width=15)
    table.add_column("内容", max_width=40, overflow="fold")
    table.add_column("时间", width=16)

    for i, mention in enumerate(mentions, 1):
        user = mention.get("user", {})
        table.add_row(
            str(i),
            mention.get("type", "-"),
            user.get("nickname", "-"),
            mention.get("content", mention.get("desc", "-")),
            mention.get("time", "-"),
        )

    console.print(table)
