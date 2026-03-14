"""
xhs search — 搜索命令。
"""
from __future__ import annotations

import json

import click

from xhs_cli.engines.mcp_client import MCPClient, MCPError
from xhs_cli.engines.cdp_client import CDPClient, CDPError
from xhs_cli.utils import config
from xhs_cli.utils.output import (
    success, error, info, warning, console,
    print_feeds, print_json, print_feed_detail,
)


@click.command("search", help="搜索小红书笔记")
@click.argument("keyword")
@click.option("--sort", type=click.Choice(["综合", "最新", "最多点赞", "最多评论", "最多收藏"]),
              default=None, help="排序方式")
@click.option("--type", "note_type", type=click.Choice(["不限", "视频", "图文"]),
              default=None, help="笔记类型")
@click.option("--time", "pub_time", type=click.Choice(["不限", "一天内", "一周内", "半年内"]),
              default=None, help="发布时间")
@click.option("--engine", type=click.Choice(["auto", "mcp", "cdp"]), default="auto",
              help="引擎 (cdp 会返回推荐词)")
@click.option("--json-output", "as_json", is_flag=True, help="输出 JSON 格式")
@click.option("--limit", type=int, default=20, help="最大结果数")
def search(keyword, sort, note_type, pub_time, engine, as_json, limit):
    """搜索笔记。MCP 更快，CDP 返回推荐关键词。"""
    cfg = config.load_config()

    if engine == "auto":
        engine = cfg["default"].get("engine", "auto")
    if engine == "auto":
        engine = "mcp" if MCPClient.is_running(
            host=cfg["mcp"]["host"], port=cfg["mcp"]["port"]
        ) else "cdp"

    if engine == "mcp":
        _search_mcp(cfg, keyword, sort, as_json)
    else:
        _search_cdp(cfg, keyword, sort, note_type, pub_time, as_json)


def _search_mcp(cfg, keyword, sort, as_json):
    """MCP 搜索。"""
    client = MCPClient(host=cfg["mcp"]["host"], port=cfg["mcp"]["port"])
    info(f"正在搜索: {keyword} (MCP)")

    try:
        filters = {}
        if sort:
            filters["sort"] = sort
        result = client.search(keyword, filters=filters or None)
    except MCPError as e:
        error(f"搜索失败: {e}")
        raise SystemExit(1)

    if as_json:
        print_json(result)
        return

    # 解析结果
    feeds = _extract_feeds(result)
    print_feeds(feeds, keyword=keyword)


def _search_cdp(cfg, keyword, sort, note_type, pub_time, as_json):
    """CDP 搜索（含推荐词）。"""
    client = CDPClient(
        host=cfg["cdp"]["host"],
        port=cfg["cdp"]["port"],
        headless=True,
        reuse_tab=True,
    )

    info(f"正在搜索: {keyword} (CDP, 含推荐词)")

    try:
        result = client.search(
            keyword=keyword,
            sort_by=sort,
            note_type=note_type,
            publish_time=pub_time,
        )
    except CDPError as e:
        error(f"搜索失败: {e}")
        raise SystemExit(1)

    if as_json:
        print_json(result)
        return

    # 显示推荐词
    rec_keywords = result.get("recommended_keywords", [])
    if rec_keywords:
        kw_str = ", ".join(rec_keywords[:10])
        info(f"推荐关键词: {kw_str}")

    feeds = result.get("feeds", [])
    print_feeds(feeds, keyword=keyword)


def _extract_feeds(result) -> list[dict]:
    """从 MCP 结果中提取 feeds 列表。"""
    if isinstance(result, dict):
        # 直接有 feeds
        if "feeds" in result:
            return result["feeds"]
        # content 数组里找
        content = result.get("content", [])
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text = item.get("text", "")
                    try:
                        parsed = json.loads(text)
                        if isinstance(parsed, dict) and "feeds" in parsed:
                            return parsed["feeds"]
                        if isinstance(parsed, list):
                            return parsed
                    except (json.JSONDecodeError, TypeError):
                        pass
    return []


@click.command("detail", help="查看笔记详情")
@click.argument("feed_id")
@click.option("--token", "-t", required=True, help="xsec_token")
@click.option("--comments", is_flag=True, help="加载所有评论")
@click.option("--engine", type=click.Choice(["auto", "mcp", "cdp"]), default="auto", help="引擎")
@click.option("--json-output", "as_json", is_flag=True, help="输出 JSON")
def detail(feed_id, token, comments, engine, as_json):
    """查看笔记详情和评论。"""
    cfg = config.load_config()

    if engine == "auto":
        engine = "mcp" if MCPClient.is_running(
            host=cfg["mcp"]["host"], port=cfg["mcp"]["port"]
        ) else "cdp"

    try:
        if engine == "mcp":
            client = MCPClient(host=cfg["mcp"]["host"], port=cfg["mcp"]["port"])
            info("正在获取详情 (MCP)...")
            result = client.get_feed_detail(feed_id, token, load_all_comments=comments)
        else:
            client = CDPClient(
                host=cfg["cdp"]["host"], port=cfg["cdp"]["port"],
                headless=True, reuse_tab=True,
            )
            info("正在获取详情 (CDP)...")
            result = client.get_feed_detail(feed_id, token)
    except (MCPError, CDPError) as e:
        error(f"获取详情失败: {e}")
        raise SystemExit(1)

    if as_json:
        print_json(result)
    else:
        print_feed_detail(result)
