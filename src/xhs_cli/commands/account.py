"""
xhs account — 多账号管理命令。
"""
from __future__ import annotations

import click

from xhs_cli.engines.cdp_client import CDPClient
from xhs_cli.utils import config
from xhs_cli.utils.output import success, error, info, console

from rich.table import Table
from rich import box


@click.group("account", help="多账号管理")
def account_group():
    pass


@account_group.command("list", help="列出所有账号")
def list_accounts():
    """列出已配置的账号。"""
    cfg = config.load_config()
    client = CDPClient(host=cfg["cdp"]["host"], port=cfg["cdp"]["port"])

    output = client.list_accounts()
    if not output.strip() or "No accounts" in output:
        info("暂无配置账号")
        info("使用 [bold]xhs account add <name>[/] 添加账号")
        return

    # 解析并美化输出
    lines = output.strip().split("\n")
    table = Table(title="📱 账号列表", box=box.ROUNDED)
    table.add_column("名称", style="bold")
    table.add_column("别名")
    table.add_column("默认", justify="center")

    for line in lines:
        line = line.strip()
        if not line or line.startswith("-") or line.startswith("Name"):
            continue
        parts = line.split()
        if len(parts) >= 1:
            name = parts[0]
            alias = parts[1] if len(parts) >= 2 else "-"
            is_default = "⭐" if (len(parts) >= 3 and parts[2] == "*") else ""
            table.add_row(name, alias, is_default)

    console.print(table)


@account_group.command("add", help="添加新账号")
@click.argument("name")
@click.option("--alias", "-a", default=None, help="显示名称")
def add_account(name, alias):
    """添加新账号。"""
    cfg = config.load_config()
    client = CDPClient(host=cfg["cdp"]["host"], port=cfg["cdp"]["port"])

    output = client.add_account(name, alias)
    if "added" in output.lower() or "Account" in output:
        success(f"账号 '{name}' 已添加")
        info(f"使用 [bold]xhs login --cdp --account {name}[/] 登录此账号")
    else:
        error(f"添加失败: {output}")
        raise SystemExit(1)


@account_group.command("remove", help="删除账号")
@click.argument("name")
@click.option("--delete-profile", is_flag=True, help="同时删除 Chrome 配置目录")
@click.confirmation_option(prompt="确认删除此账号?")
def remove_account(name, delete_profile):
    """删除账号。"""
    cfg = config.load_config()
    client = CDPClient(host=cfg["cdp"]["host"], port=cfg["cdp"]["port"])

    output = client.remove_account(name, delete_profile)
    if "removed" in output.lower():
        success(f"账号 '{name}' 已删除")
    else:
        error(f"删除失败: {output}")
        raise SystemExit(1)


@account_group.command("default", help="设置默认账号")
@click.argument("name")
def set_default(name):
    """设置默认账号。"""
    config.set_value("default.account", name)
    success(f"默认账号已设为: {name}")
