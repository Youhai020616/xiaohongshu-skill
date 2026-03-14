"""
xhs — 小红书命令行工具主入口。

Usage:
    xhs publish --title "Hello" --content "内容" --images photo.jpg
    xhs search "AI创业"
    xhs like FEED_ID --token TOKEN
    xhs comment FEED_ID --token TOKEN --content "好文!"
    xhs favorite FEED_ID --token TOKEN
    xhs detail FEED_ID --token TOKEN
    xhs me
    xhs profile USER_ID --token TOKEN
    xhs analytics
    xhs notifications
    xhs feeds
    xhs login
    xhs logout
    xhs status
    xhs server start|stop|status|log
    xhs account list|add|remove|default
    xhs config show|set|get|reset
"""
from __future__ import annotations

import click

from xhs_cli import __version__


BANNER = r"""
  ╔═══════════════════════════════╗
  ║   📕 xhs-cli v{version}        ║
  ║   小红书命令行工具            ║
  ╚═══════════════════════════════╝
""".format(version=__version__)


class AliasGroup(click.Group):
    """支持命令别名的 Click Group。"""

    ALIASES = {
        "pub": "publish",
        "s": "search",
        "fav": "favorite",
        "noti": "notifications",
        "stat": "status",
        "srv": "server",
        "acc": "account",
        "cfg": "config",
    }

    def get_command(self, ctx, cmd_name):
        # 先查别名
        resolved = self.ALIASES.get(cmd_name, cmd_name)
        return super().get_command(ctx, resolved)

    def format_help(self, ctx, formatter):
        """自定义帮助信息。"""
        formatter.write(BANNER)
        super().format_help(ctx, formatter)


@click.group(cls=AliasGroup, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="xhs-cli")
@click.pass_context
def cli(ctx):
    """📕 小红书命令行工具 — 发布、搜索、互动、数据分析"""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# ------------------------------------------------------------------
# 注册所有命令
# ------------------------------------------------------------------

# 发布
from xhs_cli.commands.publish import publish
cli.add_command(publish)

# 搜索 & 详情
from xhs_cli.commands.search import search, detail
cli.add_command(search)
cli.add_command(detail)

# 互动
from xhs_cli.commands.interact import like, favorite, comment, feeds
cli.add_command(like)
cli.add_command(favorite)
cli.add_command(comment)
cli.add_command(feeds)

# 用户
from xhs_cli.commands.profile import me, profile
cli.add_command(me)
cli.add_command(profile)

# 数据分析
from xhs_cli.commands.analytics import analytics, notifications
cli.add_command(analytics)
cli.add_command(notifications)

# 初始化
from xhs_cli.commands.init import init
cli.add_command(init)

# 认证
from xhs_cli.commands.auth import login, logout, auth_status
cli.add_command(login)
cli.add_command(logout)
cli.add_command(auth_status, "status")

# 服务管理
from xhs_cli.commands.server import server_group
cli.add_command(server_group, "server")

# 账号管理
from xhs_cli.commands.account import account_group
cli.add_command(account_group, "account")

# 配置管理
from xhs_cli.commands.config_cmd import config_group
cli.add_command(config_group, "config")


def main():
    cli()


if __name__ == "__main__":
    main()
