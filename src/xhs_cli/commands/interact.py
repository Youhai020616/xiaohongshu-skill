"""
xhs like / comment / favorite — 互动命令。
"""
from __future__ import annotations

import click

from xhs_cli.engines.mcp_client import MCPClient, MCPError
from xhs_cli.utils import config
from xhs_cli.utils.output import success, error, info, console


def _get_mcp(cfg=None):
    cfg = cfg or config.load_config()
    return MCPClient(host=cfg["mcp"]["host"], port=cfg["mcp"]["port"])


@click.command("like", help="点赞笔记")
@click.argument("feed_id")
@click.option("--token", "-t", required=True, help="xsec_token")
@click.option("--unlike", is_flag=True, help="取消点赞")
def like(feed_id, token, unlike):
    """点赞或取消点赞。"""
    client = _get_mcp()
    action = "取消点赞" if unlike else "点赞"
    info(f"正在{action}...")

    try:
        client.like(feed_id, token, unlike=unlike)
        success(f"{action}成功 👍")
    except MCPError as e:
        error(f"{action}失败: {e}")
        raise SystemExit(1)


@click.command("favorite", help="收藏笔记")
@click.argument("feed_id")
@click.option("--token", "-t", required=True, help="xsec_token")
@click.option("--unfavorite", is_flag=True, help="取消收藏")
def favorite(feed_id, token, unfavorite):
    """收藏或取消收藏。"""
    client = _get_mcp()
    action = "取消收藏" if unfavorite else "收藏"
    info(f"正在{action}...")

    try:
        client.favorite(feed_id, token, unfavorite=unfavorite)
        success(f"{action}成功 ⭐")
    except MCPError as e:
        error(f"{action}失败: {e}")
        raise SystemExit(1)


@click.command("comment", help="评论笔记")
@click.argument("feed_id")
@click.option("--token", "-t", required=True, help="xsec_token")
@click.option("--content", "-c", required=True, help="评论内容")
def comment(feed_id, token, content):
    """发表评论。"""
    client = _get_mcp()
    info("正在发表评论...")

    try:
        client.comment(feed_id, token, content)
        success("评论成功 💬")
    except MCPError as e:
        error(f"评论失败: {e}")
        raise SystemExit(1)


@click.command("feeds", help="获取首页推荐")
@click.option("--json-output", "as_json", is_flag=True, help="输出 JSON")
def feeds(as_json):
    """获取首页推荐 Feed。"""
    from xhs_cli.utils.output import print_feeds, print_json

    client = _get_mcp()
    info("正在获取首页推荐...")

    try:
        result = client.list_feeds()
        if as_json:
            print_json(result)
        else:
            # 尝试提取 feeds
            import json
            feed_list = []
            if isinstance(result, dict):
                content = result.get("content", [])
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            try:
                                parsed = json.loads(item.get("text", ""))
                                if isinstance(parsed, list):
                                    feed_list = parsed
                                elif isinstance(parsed, dict) and "feeds" in parsed:
                                    feed_list = parsed["feeds"]
                            except Exception:
                                pass
            print_feeds(feed_list, keyword="首页推荐")
    except MCPError as e:
        error(f"获取推荐失败: {e}")
        raise SystemExit(1)
